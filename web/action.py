import base64
import datetime
import importlib
import json
import os.path
import re
import shutil
import signal
from math import floor
from urllib.parse import unquote

from flask_login import logout_user
from werkzeug.security import generate_password_hash

import log
from app.conf import SystemConfig, ModuleConf
from app.filetransfer import FileTransfer
from app.filter import Filter
from app.helper import DbHelper, ProgressHelper, ThreadHelper, \
    MetaHelper, DisplayHelper, WordsHelper
from app.media import Media
from app.media.meta import MetaInfo
from app.mediaserver import MediaServer
from app.message import Message, MessageCenter
from app.scheduler import stop_scheduler
from app.subtitle import Subtitle
from app.sync import Sync, stop_monitor
from app.utils import StringUtils, EpisodeFormat, RequestUtils, PathUtils, \
    SystemUtils, ExceptionUtils
from app.utils.types import RmtMode, OsType, SearchType, SyncType, MediaType
from config import RMT_MEDIAEXT, RMT_SUBEXT, Config
from web.backend.web_utils import WebUtils


class WebAction:
    dbhelper = None
    _actions = {}
    _MovieTypes = ['MOV', '电影']
    _TvTypes = ['TV', '电视剧']

    def __init__(self):
        self.dbhelper = DbHelper()
        self._actions = {
            "sch": self.__sch,
            "del_unknown_path": self.__del_unknown_path,
            "rename": self.__rename,
            "rename_udf": self.__rename_udf,
            "delete_history": self.__delete_history,
            "logging": self.__logging,
            "restart": self.__restart,
            "reset_db_version": self.__reset_db_version,
            "logout": self.__logout,
            "update_config": self.__update_config,
            "update_directory": self.__update_directory,
            "add_or_edit_sync_path": self.__add_or_edit_sync_path,
            "get_sync_path": self.__get_sync_path,
            "delete_sync_path": self.__delete_sync_path,
            "check_sync_path": self.__check_sync_path,
            "re_identification": self.__re_identification,
            "test_connection": self.__test_connection,
            "user_manager": self.__user_manager,
            "refresh_message": self.__refresh_message,
            "delete_tmdb_cache": self.__delete_tmdb_cache,
            "modify_tmdb_cache": self.__modify_tmdb_cache,
            "truncate_blacklist": self.__truncate_blacklist,
            "name_test": self.__name_test,
            "rule_test": self.__rule_test,
            "net_test": self.__net_test,
            "add_filtergroup": self.__add_filtergroup,
            "restore_filtergroup": self.__restore_filtergroup,
            "set_default_filtergroup": self.__set_default_filtergroup,
            "del_filtergroup": self.__del_filtergroup,
            "add_filterrule": self.__add_filterrule,
            "del_filterrule": self.__del_filterrule,
            "filterrule_detail": self.__filterrule_detail,
            "clear_tmdb_cache": self.__clear_tmdb_cache,
            "refresh_process": self.__refresh_process,
            "restory_backup": self.__restory_backup,
            "start_mediasync": self.__start_mediasync,
            "mediasync_state": self.__mediasync_state,
            "add_custom_word_group": self.__add_custom_word_group,
            "delete_custom_word_group": self.__delete_custom_word_group,
            "add_or_edit_custom_word": self.__add_or_edit_custom_word,
            "get_custom_word": self.__get_custom_word,
            "delete_custom_word": self.__delete_custom_word,
            "check_custom_words": self.__check_custom_words,
            "export_custom_words": self.__export_custom_words,
            "analyse_import_custom_words_code": self.__analyse_import_custom_words_code,
            "import_custom_words": self.__import_custom_words,
            "share_filtergroup": self.__share_filtergroup,
            "import_filtergroup": self.__import_filtergroup,
            "search_media_infos": self.search_media_infos,
            "get_sub_path": self.__get_sub_path,
            "rename_file": self.__rename_file,
            "delete_files": self.__delete_files,
            "download_subtitle": self.__download_subtitle,
            "update_message_client": self.__update_message_client,
            "delete_message_client": self.__delete_message_client,
            "check_message_client": self.__check_message_client,
            "get_message_client": self.__get_message_client,
            "test_message_client": self.__test_message_client,
            "find_hardlinks": self.__find_hardlinks,
            "send_custom_message": self.send_custom_message,
            "save_user_script": self.__save_user_script
        }

    def action(self, cmd, data=None):
        func = self._actions.get(cmd)
        if not func:
            return {"code": -1, "msg": "非授权访问！"}
        else:
            return func(data)

    def api_action(self, cmd, data=None):
        result = self.action(cmd, data)
        if not result:
            return {
                "code": -1,
                "success": False,
                "message": "服务异常，未获取到返回结果"
            }
        code = result.get("code", result.get("retcode", 0))
        if not code or str(code) == "0":
            success = True
        else:
            success = False
        message = result.get("msg", result.get("retmsg", ""))
        for key in ['code', 'retcode', 'msg', 'retmsg']:
            if key in result:
                result.pop(key)
        return {
            "code": code,
            "success": success,
            "message": message,
            "data": result
        }

    @staticmethod
    def restart_server():
        """
        停止进程
        """
        # 停止定时服务
        stop_scheduler()
        # 停止监控
        stop_monitor()
        # 签退
        logout_user()
        # 关闭虚拟显示
        DisplayHelper().quit()
        # 重启进程
        if os.name == "nt":
            os.kill(os.getpid(), getattr(signal, "SIGKILL", signal.SIGTERM))
        elif SystemUtils.is_synology():
            os.system(
                "ps -ef | grep -v grep | grep 'python run.py'|awk '{print $2}'|xargs kill -9")
        else:
            os.system("pm2 restart NAStool")

    @staticmethod
    def handle_message_job(msg, in_from=SearchType.OT, user_id=None, user_name=None):
        """
        处理消息事件
        """
        if not msg:
            return
        commands = {
            "/rst": {"func": Sync().transfer_all_sync, "desp": "目录同步"},
        }
        command = commands.get(msg)
        message = Message()

        if command:
            # 启动服务
            ThreadHelper().start_thread(command.get("func"), ())
            message.send_channel_msg(
                channel=in_from, title="正在运行 %s ..." % command.get("desp"), user_id=user_id)

    @staticmethod
    def set_config_value(cfg, cfg_key, cfg_value):
        """
        根据Key设置配置值
        """
        # 密码
        if cfg_key == "app.login_password":
            if cfg_value and not cfg_value.startswith("[hash]"):
                cfg['app']['login_password'] = "[hash]%s" % generate_password_hash(
                    cfg_value)
            else:
                cfg['app']['login_password'] = cfg_value or "password"
            return cfg
        # 代理
        if cfg_key == "app.proxies":
            if cfg_value:
                if not cfg_value.startswith("http") and not cfg_value.startswith("sock"):
                    cfg['app']['proxies'] = {
                        "https": "http://%s" % cfg_value, "http": "http://%s" % cfg_value}
                else:
                    cfg['app']['proxies'] = {"https": "%s" %
                                             cfg_value, "http": "%s" % cfg_value}
            else:
                cfg['app']['proxies'] = {"https": None, "http": None}
            return cfg
        # 最大支持三层赋值
        keys = cfg_key.split(".")
        if keys:
            if len(keys) == 1:
                cfg[keys[0]] = cfg_value
            elif len(keys) == 2:
                if not cfg.get(keys[0]):
                    cfg[keys[0]] = {}
                cfg[keys[0]][keys[1]] = cfg_value
            elif len(keys) == 3:
                if cfg.get(keys[0]):
                    if not cfg[keys[0]].get(keys[1]) or isinstance(cfg[keys[0]][keys[1]], str):
                        cfg[keys[0]][keys[1]] = {}
                    cfg[keys[0]][keys[1]][keys[2]] = cfg_value
                else:
                    cfg[keys[0]] = {}
                    cfg[keys[0]][keys[1]] = {}
                    cfg[keys[0]][keys[1]][keys[2]] = cfg_value

        return cfg

    @staticmethod
    def set_config_directory(cfg, oper, cfg_key, cfg_value, update_value=None):
        """
        更新目录数据
        """

        def remove_sync_path(obj, key):
            if not isinstance(obj, list):
                return []
            ret_obj = []
            for item in obj:
                if item.split("@")[0].replace("\\", "/") != key.split("@")[0].replace("\\", "/"):
                    ret_obj.append(item)
            return ret_obj

        # 最大支持二层赋值
        keys = cfg_key.split(".")
        if keys:
            if len(keys) == 1:
                if cfg.get(keys[0]):
                    if not isinstance(cfg[keys[0]], list):
                        cfg[keys[0]] = [cfg[keys[0]]]
                    if oper == "add":
                        cfg[keys[0]].append(cfg_value)
                    elif oper == "sub":
                        cfg[keys[0]].remove(cfg_value)
                        if not cfg[keys[0]]:
                            cfg[keys[0]] = None
                    elif oper == "set":
                        cfg[keys[0]].remove(cfg_value)
                        if update_value:
                            cfg[keys[0]].append(update_value)
                else:
                    cfg[keys[0]] = cfg_value
            elif len(keys) == 2:
                if cfg.get(keys[0]):
                    if not cfg[keys[0]].get(keys[1]):
                        cfg[keys[0]][keys[1]] = []
                    if not isinstance(cfg[keys[0]][keys[1]], list):
                        cfg[keys[0]][keys[1]] = [cfg[keys[0]][keys[1]]]
                    if oper == "add":
                        cfg[keys[0]][keys[1]].append(
                            cfg_value.replace("\\", "/"))
                    elif oper == "sub":
                        cfg[keys[0]][keys[1]] = remove_sync_path(
                            cfg[keys[0]][keys[1]], cfg_value)
                        if not cfg[keys[0]][keys[1]]:
                            cfg[keys[0]][keys[1]] = None
                    elif oper == "set":
                        cfg[keys[0]][keys[1]] = remove_sync_path(
                            cfg[keys[0]][keys[1]], cfg_value)
                        if update_value:
                            cfg[keys[0]][keys[1]].append(
                                update_value.replace("\\", "/"))
                else:
                    cfg[keys[0]] = {}
                    cfg[keys[0]][keys[1]] = cfg_value.replace("\\", "/")
        return cfg

    @staticmethod
    def __sch(data):
        """
        启动定时服务
        """
        commands = {
            "sync": Sync().transfer_all_sync,
        }
        sch_item = data.get("item")
        if sch_item and commands.get(sch_item):
            ThreadHelper().start_thread(commands.get(sch_item), ())
        return {"retmsg": "服务已启动", "item": sch_item}



    def __del_unknown_path(self, data):
        """
        删除路径
        """
        tids = data.get("id")
        if isinstance(tids, list):
            for tid in tids:
                if not tid:
                    continue
                self.dbhelper.delete_transfer_unknown(tid)
            return {"retcode": 0}
        else:
            retcode = self.dbhelper.delete_transfer_unknown(tids)
            return {"retcode": retcode}

    def __rename(self, data):
        """
        手工转移
        """
        path = dest_dir = None
        syncmod = ModuleConf.RMT_MODES.get(data.get("syncmod"))
        logid = data.get("logid")
        if logid:
            paths = self.dbhelper.get_transfer_path_by_id(logid)
            if paths:
                path = os.path.join(
                    paths[0].SOURCE_PATH, paths[0].SOURCE_FILENAME)
                dest_dir = paths[0].DEST
            else:
                return {"retcode": -1, "retmsg": "未查询到转移日志记录"}
        else:
            unknown_id = data.get("unknown_id")
            if unknown_id:
                paths = self.dbhelper.get_unknown_path_by_id(unknown_id)
                if paths:
                    path = paths[0].PATH
                    dest_dir = paths[0].DEST
                else:
                    return {"retcode": -1, "retmsg": "未查询到未识别记录"}
        if not dest_dir:
            dest_dir = ""
        if not path:
            return {"retcode": -1, "retmsg": "输入路径有误"}
        tmdbid = data.get("tmdb")
        mtype = data.get("type")
        season = data.get("season")
        episode_format = data.get("episode_format")
        episode_details = data.get("episode_details")
        episode_offset = data.get("episode_offset")
        min_filesize = data.get("min_filesize")
        if mtype in self._MovieTypes:
            media_type = MediaType.MOVIE
        elif mtype in self._TvTypes:
            media_type = MediaType.TV
        else:
            media_type = MediaType.ANIME
        # 如果改次手动修复时一个单文件，自动修复改目录下同名文件，需要配合episode_format生效
        need_fix_all = False
        if os.path.splitext(path)[-1].lower() in RMT_MEDIAEXT and episode_format:
            path = os.path.dirname(path)
            need_fix_all = True
        # 开始转移
        succ_flag, ret_msg = self.__manual_transfer(inpath=path,
                                                    syncmod=syncmod,
                                                    outpath=dest_dir,
                                                    media_type=media_type,
                                                    episode_format=episode_format,
                                                    episode_details=episode_details,
                                                    episode_offset=episode_offset,
                                                    need_fix_all=need_fix_all,
                                                    min_filesize=min_filesize,
                                                    tmdbid=tmdbid,
                                                    season=season)
        if succ_flag:
            if not need_fix_all and not logid:
                # 更新记录状态
                self.dbhelper.update_transfer_unknown_state(path)
            return {"retcode": 0, "retmsg": "转移成功"}
        else:
            return {"retcode": 2, "retmsg": ret_msg}

    def __rename_udf(self, data):
        """
        自定义识别
        """
        inpath = data.get("inpath")
        if not os.path.exists(inpath):
            return {"retcode": -1, "retmsg": "输入路径不存在"}
        outpath = data.get("outpath")
        syncmod = ModuleConf.RMT_MODES.get(data.get("syncmod"))
        tmdbid = data.get("tmdb")
        mtype = data.get("type")
        season = data.get("season")
        episode_format = data.get("episode_format")
        episode_details = data.get("episode_details")
        episode_offset = data.get("episode_offset")
        min_filesize = data.get("min_filesize")
        if mtype in self._MovieTypes:
            media_type = MediaType.MOVIE
        elif mtype in self._TvTypes:
            media_type = MediaType.TV
        else:
            media_type = MediaType.ANIME
        # 开始转移
        succ_flag, ret_msg = self.__manual_transfer(inpath=inpath,
                                                    syncmod=syncmod,
                                                    outpath=outpath,
                                                    media_type=media_type,
                                                    episode_format=episode_format,
                                                    episode_details=episode_details,
                                                    episode_offset=episode_offset,
                                                    min_filesize=min_filesize,
                                                    tmdbid=tmdbid,
                                                    season=season)
        if succ_flag:
            return {"retcode": 0, "retmsg": "转移成功"}
        else:
            return {"retcode": 2, "retmsg": ret_msg}

    @staticmethod
    def __manual_transfer(inpath,
                          syncmod,
                          outpath=None,
                          media_type=None,
                          episode_format=None,
                          episode_details=None,
                          episode_offset=None,
                          min_filesize=None,
                          tmdbid=None,
                          season=None,
                          need_fix_all=False
                          ):
        """
        开始手工转移文件
        """
        inpath = os.path.normpath(inpath)
        if outpath:
            outpath = os.path.normpath(outpath)
        if not os.path.exists(inpath):
            return False, "输入路径不存在"
        if tmdbid:
            # 有输入TMDBID
            tmdb_info = Media().get_tmdb_info(mtype=media_type, tmdbid=tmdbid)
            if not tmdb_info:
                return False, "识别失败，无法查询到TMDB信息"
            # 按识别的信息转移
            succ_flag, ret_msg = FileTransfer().transfer_media(in_from=SyncType.MAN,
                                                               in_path=inpath,
                                                               rmt_mode=syncmod,
                                                               target_dir=outpath,
                                                               tmdb_info=tmdb_info,
                                                               media_type=media_type,
                                                               season=season,
                                                               episode=(
                                                                   EpisodeFormat(episode_format,
                                                                                 episode_details,
                                                                                 episode_offset),
                                                                   need_fix_all),
                                                               min_filesize=min_filesize,
                                                               udf_flag=True)
        else:
            # 按识别的信息转移
            succ_flag, ret_msg = FileTransfer().transfer_media(in_from=SyncType.MAN,
                                                               in_path=inpath,
                                                               rmt_mode=syncmod,
                                                               target_dir=outpath,
                                                               media_type=media_type,
                                                               episode=(
                                                                   EpisodeFormat(episode_format,
                                                                                 episode_details,
                                                                                 episode_offset),
                                                                   need_fix_all),
                                                               min_filesize=min_filesize,
                                                               udf_flag=True)
        return succ_flag, ret_msg

    def __delete_history(self, data):
        """
        删除识别记录及文件
        """
        logids = data.get('logids')
        flag = data.get('flag')
        for logid in logids:
            # 读取历史记录
            paths = self.dbhelper.get_transfer_path_by_id(logid)
            if paths:
                # 删除记录
                self.dbhelper.delete_transfer_log_by_id(logid)
                # 根据flag删除文件
                source_path = paths[0].SOURCE_PATH
                source_filename = paths[0].SOURCE_FILENAME
                dest = paths[0].DEST
                dest_path = paths[0].DEST_PATH
                dest_filename = paths[0].DEST_FILENAME
                if flag in ["del_source", "del_all"]:
                    del_flag, del_msg = self.delete_media_file(
                        source_path, source_filename)
                    if not del_flag:
                        log.error(f"【History】{del_msg}")
                    else:
                        log.info(f"【History】{del_msg}")
                if flag in ["del_dest", "del_all"]:
                    if dest_path and dest_filename:
                        del_flag, del_msg = self.delete_media_file(
                            dest_path, dest_filename)
                        if not del_flag:
                            log.error(f"【History】{del_msg}")
                        else:
                            log.info(f"【History】{del_msg}")
                    else:
                        meta_info = MetaInfo(title=source_filename)
                        meta_info.title = paths[0].TITLE
                        meta_info.category = paths[0].CATEGORY
                        meta_info.year = paths[0].YEAR
                        if paths[0].SEASON_EPISODE:
                            meta_info.begin_season = int(
                                str(paths[0].SEASON_EPISODE).replace("S", ""))
                        if paths[0].TYPE == MediaType.MOVIE.value:
                            meta_info.type = MediaType.MOVIE
                        else:
                            meta_info.type = MediaType.TV
                        # 删除文件
                        dest_path = FileTransfer().get_dest_path_by_info(dest=dest, meta_info=meta_info)
                        if dest_path and dest_path.find(meta_info.title) != -1:
                            rm_parent_dir = False
                            if not meta_info.get_season_list():
                                # 电影，删除整个目录
                                try:
                                    shutil.rmtree(dest_path)
                                except Exception as e:
                                    ExceptionUtils.exception_traceback(e)
                            elif not meta_info.get_episode_string():
                                # 电视剧但没有集数，删除季目录
                                try:
                                    shutil.rmtree(dest_path)
                                except Exception as e:
                                    ExceptionUtils.exception_traceback(e)
                                rm_parent_dir = True
                            else:
                                # 有集数的电视剧，删除对应的集数文件
                                for dest_file in PathUtils.get_dir_files(dest_path):
                                    file_meta_info = MetaInfo(
                                        os.path.basename(dest_file))
                                    if file_meta_info.get_episode_list() and set(
                                            file_meta_info.get_episode_list()
                                    ).issubset(set(meta_info.get_episode_list())):
                                        try:
                                            os.remove(dest_file)
                                        except Exception as e:
                                            ExceptionUtils.exception_traceback(
                                                e)
                                rm_parent_dir = True
                            if rm_parent_dir \
                                    and not PathUtils.get_dir_files(os.path.dirname(dest_path), exts=RMT_MEDIAEXT):
                                # 没有媒体文件时，删除整个目录
                                try:
                                    shutil.rmtree(os.path.dirname(dest_path))
                                except Exception as e:
                                    ExceptionUtils.exception_traceback(e)
        return {"retcode": 0}

    @staticmethod
    def delete_media_file(filedir, filename):
        """
        删除媒体文件，空目录也支被删除
        """
        filedir = os.path.normpath(filedir).replace("\\", "/")
        file = os.path.join(filedir, filename)
        try:
            if not os.path.exists(file):
                return False, f"{file} 不存在"
            os.remove(file)
            nfoname = f"{os.path.splitext(filename)[0]}.nfo"
            nfofile = os.path.join(filedir, nfoname)
            if os.path.exists(nfofile):
                os.remove(nfofile)
            # 检查空目录并删除
            if re.findall(r"^S\d{2}|^Season", os.path.basename(filedir), re.I):
                # 当前是季文件夹，判断并删除
                seaon_dir = filedir
                if seaon_dir.count('/') > 1 and not PathUtils.get_dir_files(seaon_dir, exts=RMT_MEDIAEXT):
                    shutil.rmtree(seaon_dir)
                # 媒体文件夹
                media_dir = os.path.dirname(seaon_dir)
            else:
                media_dir = filedir
            # 检查并删除媒体文件夹，非根目录且目录大于二级，且没有媒体文件时才会删除
            if media_dir != '/' \
                    and media_dir.count('/') > 1 \
                    and not re.search(r'[a-zA-Z]:/$', media_dir) \
                    and not PathUtils.get_dir_files(media_dir, exts=RMT_MEDIAEXT):
                shutil.rmtree(media_dir)
            return True, f"{file} 删除成功"
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return True, f"{file} 删除失败"

    @staticmethod
    def __logging(data):
        """
        查询实时日志
        """
        log_list = []
        refresh_new = data.get('refresh_new')
        if not refresh_new:
            log_list = list(log.LOG_QUEUE)
        elif log.LOG_INDEX:
            if log.LOG_INDEX > len(list(log.LOG_QUEUE)):
                log_list = list(log.LOG_QUEUE)
            else:
                log_list = list(log.LOG_QUEUE)[-log.LOG_INDEX:]
        log.LOG_INDEX = 0
        return {"loglist": log_list}


    def __restart(self, data):
        """
        重启
        """
        # 退出主进程
        self.restart_server()
        return {"code": 0}


    def __reset_db_version(self, data):
        """
        重置数据库版本
        """
        try:
            self.dbhelper.drop_table("alembic_version")
            return {"code": 0}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": str(e)}

    @staticmethod
    def __logout(data):
        """
        注销
        """
        logout_user()
        return {"code": 0}

    def __update_config(self, data):
        """
        更新配置信息
        """
        cfg = Config().get_config()
        cfgs = dict(data).items()
        # 仅测试不保存
        config_test = False
        # 修改配置
        for key, value in cfgs:
            if key == "test" and value:
                config_test = True
                continue
            # 生效配置
            cfg = self.set_config_value(cfg, key, value)

        # 保存配置
        if not config_test:
            Config().save_config(cfg)

        return {"code": 0}

    def __add_or_edit_sync_path(self, data):
        """
        维护同步目录
        """
        sid = data.get("sid")
        source = data.get("from")
        dest = data.get("to")
        unknown = data.get("unknown")
        mode = data.get("syncmod")
        rename = 1 if StringUtils.to_bool(data.get("rename"), False) else 0
        enabled = 1 if StringUtils.to_bool(data.get("enabled"), False) else 0
        # 源目录检查
        if not source:
            return {"code": 1, "msg": f'源目录不能为空'}
        if not os.path.exists(source):
            return {"code": 1, "msg": f'{source}目录不存在'}
        # windows目录用\，linux目录用/
        source = os.path.normpath(source)
        # 目的目录检查，目的目录可为空
        if dest:
            dest = os.path.normpath(dest)
            if PathUtils.is_path_in_path(source, dest):
                return {"code": 1, "msg": "目的目录不可包含在源目录中"}
        if unknown:
            unknown = os.path.normpath(unknown)

        # 硬链接不能跨盘
        if mode == "link" and dest:
            common_path = os.path.commonprefix([source, dest])
            if not common_path or common_path == "/":
                return {"code": 1, "msg": "硬链接不能跨盘"}

        # 编辑先删再增
        if sid:
            self.dbhelper.delete_config_sync_path(sid)
        # 若启用，则关闭其他相同源目录的同步目录
        if enabled == 1:
            self.dbhelper.check_config_sync_paths(source=source,
                                                  enabled=0)
        # 插入数据库
        self.dbhelper.insert_config_sync_path(source=source,
                                              dest=dest,
                                              unknown=unknown,
                                              mode=mode,
                                              rename=rename,
                                              enabled=enabled)
        Sync().init_config()
        return {"code": 0, "msg": ""}

    def __get_sync_path(self, data):
        """
        查询同步目录
        """
        try:
            sid = data.get("sid")
            sync_item = self.dbhelper.get_config_sync_paths(sid=sid)[0]
            syncpath = {'id': sync_item.ID,
                        'from': sync_item.SOURCE,
                        'to': sync_item.DEST or "",
                        'unknown': sync_item.UNKNOWN or "",
                        'syncmod': sync_item.MODE,
                        'rename': sync_item.RENAME,
                        'enabled': sync_item.ENABLED}
            return {"code": 0, "data": syncpath}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": "查询识别词失败"}

    def __delete_sync_path(self, data):
        """
        移出同步目录
        """
        sid = data.get("sid")
        self.dbhelper.delete_config_sync_path(sid)
        Sync().init_config()
        return {"code": 0}

    def __check_sync_path(self, data):
        """
        维护同步目录
        """
        flag = data.get("flag")
        sid = data.get("sid")
        checked = data.get("checked")
        if flag == "rename":
            self.dbhelper.check_config_sync_paths(sid=sid,
                                                  rename=1 if checked else 0)
            Sync().init_config()
            return {"code": 0}
        elif flag == "enable":
            # 若启用，则关闭其他相同源目录的同步目录
            if checked:
                sync_item = self.dbhelper.get_config_sync_paths(sid=sid)[0]
                self.dbhelper.check_config_sync_paths(source=sync_item.SOURCE,
                                                      enabled=0)
            self.dbhelper.check_config_sync_paths(sid=sid,
                                                  enabled=1 if checked else 0)
            Sync().init_config()
            return {"code": 0}
        else:
            return {"code": 1}


    def __re_identification(self, data):
        """
        未识别的重新识别
        """
        flag = data.get("flag")
        ids = data.get("ids")
        ret_flag = True
        ret_msg = []
        if flag == "unidentification":
            for wid in ids:
                paths = self.dbhelper.get_unknown_path_by_id(wid)
                if paths:
                    path = paths[0].PATH
                    dest_dir = paths[0].DEST
                    rmt_mode = ModuleConf.get_enum_item(
                        RmtMode, paths[0].MODE) if paths[0].MODE else None
                else:
                    return {"retcode": -1, "retmsg": "未查询到未识别记录"}
                if not dest_dir:
                    dest_dir = ""
                if not path:
                    return {"retcode": -1, "retmsg": "未识别路径有误"}
                succ_flag, msg = FileTransfer().transfer_media(in_from=SyncType.MAN,
                                                               rmt_mode=rmt_mode,
                                                               in_path=path,
                                                               target_dir=dest_dir)
                if succ_flag:
                    self.dbhelper.update_transfer_unknown_state(path)
                else:
                    ret_flag = False
                    if msg not in ret_msg:
                        ret_msg.append(msg)
        elif flag == "history":
            for wid in ids:
                paths = self.dbhelper.get_transfer_path_by_id(wid)
                if paths:
                    path = os.path.join(
                        paths[0].SOURCE_PATH, paths[0].SOURCE_FILENAME)
                    dest_dir = paths[0].DEST
                    rmt_mode = ModuleConf.get_enum_item(
                        RmtMode, paths[0].MODE) if paths[0].MODE else None
                else:
                    return {"retcode": -1, "retmsg": "未查询到转移日志记录"}
                if not dest_dir:
                    dest_dir = ""
                if not path:
                    return {"retcode": -1, "retmsg": "未识别路径有误"}
                succ_flag, msg = FileTransfer().transfer_media(in_from=SyncType.MAN,
                                                               rmt_mode=rmt_mode,
                                                               in_path=path,
                                                               target_dir=dest_dir)
                if not succ_flag:
                    ret_flag = False
                    if msg not in ret_msg:
                        ret_msg.append(msg)
        if ret_flag:
            return {"retcode": 0, "retmsg": "转移成功"}
        else:
            return {"retcode": 2, "retmsg": "、".join(ret_msg)}


    @staticmethod
    def __test_connection(data):
        """
        测试连通性
        """
        # 支持两种传入方式：命令数组或单个命令，单个命令时xx|xx模式解析为模块和类，进行动态引入
        command = data.get("command")
        ret = None
        if command:
            try:
                module_obj = None
                if isinstance(command, list):
                    for cmd_str in command:
                        ret = eval(cmd_str)
                        if not ret:
                            break
                else:
                    if command.find("|") != -1:
                        module = command.split("|")[0]
                        class_name = command.split("|")[1]
                        module_obj = getattr(
                            importlib.import_module(module), class_name)()
                        if hasattr(module_obj, "init_config"):
                            module_obj.init_config()
                        ret = module_obj.get_status()
                    else:
                        ret = eval(command)
                # 重载配置
                Config().init_config()
                if module_obj:
                    if hasattr(module_obj, "init_config"):
                        module_obj.init_config()
            except Exception as e:
                ret = None
                ExceptionUtils.exception_traceback(e)
            return {"code": 0 if ret else 1}
        return {"code": 0}

    def __user_manager(self, data):
        """
        用户管理
        """
        oper = data.get("oper")
        name = data.get("name")
        if oper == "add":
            password = generate_password_hash(str(data.get("password")))
            pris = data.get("pris")
            if isinstance(pris, list):
                pris = ",".join(pris)
            ret = self.dbhelper.insert_user(name, password, pris)
        else:
            ret = self.dbhelper.delete_user(name)

        if ret == 1 or ret:
            return {"code": 0, "success": False}
        return {"code": -1, "success": False, 'message': '操作失败'}

    @staticmethod

    @staticmethod
    def get_system_message(lst_time):
        messages = MessageCenter().get_system_messages(lst_time=lst_time)
        if messages:
            lst_time = messages[0].get("time")
        return {
            "code": 0,
            "message": messages,
            "lst_time": lst_time
        }

    def __refresh_message(self, data):
        """
        刷新首页消息中心
        """
        lst_time = data.get("lst_time")
        system_msg = self.get_system_message(lst_time=lst_time)
        messages = system_msg.get("message")
        lst_time = system_msg.get("lst_time")
        message_html = []
        for message in list(reversed(messages)):
            level = "bg-red" if message.get("level") == "ERROR" else ""
            content = re.sub(r"#+", "<br>",
                             re.sub(r"<[^>]+>", "",
                                    re.sub(r"<br/?>", "####", message.get("content"), flags=re.IGNORECASE)))
            message_html.append(f"""
            <div class="list-group-item">
              <div class="row align-items-center">
                <div class="col-auto">
                  <span class="status-dot {level} d-block"></span>
                </div>
                <div class="col text-truncate">
                  <span class="text-wrap">{message.get("title")}</span>
                  <div class="d-block text-muted text-truncate mt-n1 text-wrap">{content}</div>
                  <div class="d-block text-muted text-truncate mt-n1 text-wrap">{message.get("time")}</div>
                </div>
              </div>
            </div>
            """)
        return {"code": 0, "message": message_html, "lst_time": lst_time}

    @staticmethod
    def __delete_tmdb_cache(data):
        """
        删除tmdb缓存
        """
        if MetaHelper().delete_meta_data(data.get("cache_key")):
            MetaHelper().save_meta_data()
        return {"code": 0}

    @staticmethod
    def __modify_tmdb_cache(data):
        """
        修改TMDB缓存的标题
        """
        if MetaHelper().modify_meta_data(data.get("key"), data.get("title")):
            MetaHelper().save_meta_data(force=True)
        return {"code": 0}

    def __truncate_blacklist(self, data):
        """
        清空文件转移黑名单记录
        """
        self.dbhelper.truncate_transfer_blacklist()
        return {"code": 0}

    def __name_test(self, data):
        """
        名称识别测试
        """
        name = data.get("name")
        if not name:
            return {"code": -1}
        media_info = Media().get_media_info(title=name)
        if not media_info:
            return {"code": 0, "data": {"name": "无法识别"}}
        return {"code": 0, "data": self.mediainfo_dict(media_info)}

    @staticmethod
    def mediainfo_dict(media_info):
        if not media_info:
            return {}
        tmdb_id = media_info.tmdb_id
        tmdb_link = media_info.get_detail_url()
        tmdb_S_E_link = ""
        if tmdb_id:
            if media_info.get_season_string():
                tmdb_S_E_link = "%s/season/%s" % (tmdb_link,
                                                  media_info.get_season_seq())
                if media_info.get_episode_string():
                    tmdb_S_E_link = "%s/episode/%s" % (
                        tmdb_S_E_link, media_info.get_episode_seq())
        return {
            "type": media_info.type.value if media_info.type else "",
            "name": media_info.get_name(),
            "title": media_info.title,
            "year": media_info.year,
            "season_episode": media_info.get_season_episode_string(),
            "part": media_info.part,
            "tmdbid": tmdb_id,
            "tmdblink": tmdb_link,
            "tmdb_S_E_link": tmdb_S_E_link,
            "category": media_info.category,
            "restype": media_info.resource_type,
            "effect": media_info.resource_effect,
            "pix": media_info.resource_pix,
            "team": media_info.resource_team,
            "video_codec": media_info.video_encode,
            "audio_codec": media_info.audio_encode,
            "org_string": media_info.org_string,
            "ignored_words": media_info.ignored_words,
            "replaced_words": media_info.replaced_words,
            "offset_words": media_info.offset_words
        }

    @staticmethod
    def __rule_test(data):
        title = data.get("title")
        subtitle = data.get("subtitle")
        size = data.get("size")
        rulegroup = data.get("rulegroup")
        if not title:
            return {"code": -1}
        meta_info = MetaInfo(title=title, subtitle=subtitle)
        meta_info.size = float(size) * 1024 ** 3 if size else 0
        match_flag, res_order, match_msg = \
            Filter().check_torrent_filter(meta_info=meta_info,
                                          filter_args={"rule": rulegroup})
        return {
            "code": 0,
            "flag": match_flag,
            "text": "匹配" if match_flag else "未匹配",
            "order": 100 - res_order if res_order else 0
        }

    @staticmethod
    def __net_test(data):
        target = data
        if target == "image.tmdb.org":
            target = target + "/t/p/w500/wwemzKWzjKYJFfCeiB57q3r4Bcm.png"
        if target == "qyapi.weixin.qq.com":
            target = target + "/cgi-bin/message/send"
        target = "https://" + target
        start_time = datetime.datetime.now()
        if target.find("themoviedb") != -1 \
                or target.find("telegram") != -1 \
                or target.find("fanart") != -1 \
                or target.find("tmdb") != -1:
            res = RequestUtils(proxies=Config().get_proxies(),
                               timeout=5).get_res(target)
        else:
            res = RequestUtils(timeout=5).get_res(target)
        seconds = int((datetime.datetime.now() -
                      start_time).microseconds / 1000)
        if not res:
            return {"res": False, "time": "%s 毫秒" % seconds}
        elif res.ok:
            return {"res": True, "time": "%s 毫秒" % seconds}
        else:
            return {"res": False, "time": "%s 毫秒" % seconds}


    def __add_filtergroup(self, data):
        """
        新增规则组
        """
        name = data.get("name")
        default = data.get("default")
        if not name:
            return {"code": -1}
        self.dbhelper.add_filter_group(name, default)
        Filter().init_config()
        return {"code": 0}

    def __restore_filtergroup(self, data):
        """
        恢复初始规则组
        """
        groupids = data.get("groupids")
        init_rulegroups = data.get("init_rulegroups")
        for groupid in groupids:
            try:
                self.dbhelper.delete_filtergroup(groupid)
            except Exception as err:
                ExceptionUtils.exception_traceback(err)
            for init_rulegroup in init_rulegroups:
                if str(init_rulegroup.get("id")) == groupid:
                    for sql in init_rulegroup.get("sql"):
                        self.dbhelper.excute(sql)
        Filter().init_config()
        return {"code": 0}

    def __set_default_filtergroup(self, data):
        groupid = data.get("id")
        if not groupid:
            return {"code": -1}
        self.dbhelper.set_default_filtergroup(groupid)
        Filter().init_config()
        return {"code": 0}

    def __del_filtergroup(self, data):
        groupid = data.get("id")
        self.dbhelper.delete_filtergroup(groupid)
        Filter().init_config()
        return {"code": 0}

    def __add_filterrule(self, data):
        rule_id = data.get("rule_id")
        item = {
            "group": data.get("group_id"),
            "name": data.get("rule_name"),
            "pri": data.get("rule_pri"),
            "include": data.get("rule_include"),
            "exclude": data.get("rule_exclude"),
            "size": data.get("rule_sizelimit"),
            "free": data.get("rule_free")
        }
        self.dbhelper.insert_filter_rule(ruleid=rule_id, item=item)
        Filter().init_config()
        return {"code": 0}

    def __del_filterrule(self, data):
        ruleid = data.get("id")
        self.dbhelper.delete_filterrule(ruleid)
        Filter().init_config()
        return {"code": 0}

    @staticmethod
    def __filterrule_detail(data):
        rid = data.get("ruleid")
        groupid = data.get("groupid")
        ruleinfo = Filter().get_rules(groupid=groupid, ruleid=rid)
        if ruleinfo:
            ruleinfo['include'] = "\n".join(ruleinfo.get("include"))
            ruleinfo['exclude'] = "\n".join(ruleinfo.get("exclude"))
        return {"code": 0, "info": ruleinfo}




    @staticmethod
    def __clear_tmdb_cache(data):
        """
        清空TMDB缓存
        """
        try:
            MetaHelper().clear_meta_data()
            os.remove(MetaHelper().get_meta_data_path())
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 0, "msg": str(e)}
        return {"code": 0}


    @staticmethod
    def __refresh_process(data):
        """
        刷新进度条
        """
        detail = ProgressHelper().get_process(data.get("type"))
        if detail:
            return {"code": 0, "value": detail.get("value"), "text": detail.get("text")}
        else:
            return {"code": 1, "value": 0, "text": "正在处理..."}

    @staticmethod
    def __restory_backup(data):
        """
        解压恢复备份文件
        """
        filename = data.get("file_name")
        if filename:
            config_path = Config().get_config_path()
            temp_path = Config().get_temp_path()
            file_path = os.path.join(temp_path, filename)
            try:
                shutil.unpack_archive(file_path, config_path, format='zip')
                return {"code": 0, "msg": ""}
            except Exception as e:
                ExceptionUtils.exception_traceback(e)
                return {"code": 1, "msg": str(e)}
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)

        return {"code": 1, "msg": "文件不存在"}

    @staticmethod
    def __start_mediasync(data):
        """
        开始媒体库同步
        """
        ThreadHelper().start_thread(MediaServer().sync_mediaserver, ())
        return {"code": 0}

    @staticmethod
    def __mediasync_state(data):
        """
        获取媒体库同步数据情况
        """
        status = MediaServer().get_mediasync_status()
        if not status:
            return {"code": 0, "text": "未同步"}
        else:
            return {"code": 0, "text": "电影：%s，电视剧：%s，同步时间：%s" %
                                       (status.get("movie_count"),
                                        status.get("tv_count"),
                                        status.get("time"))}


    def __add_custom_word_group(self, data):
        try:
            tmdb_id = data.get("tmdb_id")
            tmdb_type = data.get("tmdb_type")
            if tmdb_type == "tv":
                if not self.dbhelper.is_custom_word_group_existed(tmdbid=tmdb_id, gtype=2):
                    tmdb_info = Media().get_tmdb_info(mtype=MediaType.TV, tmdbid=tmdb_id)
                    if not tmdb_info:
                        return {"code": 1, "msg": "添加失败，无法查询到TMDB信息"}
                    self.dbhelper.insert_custom_word_groups(title=tmdb_info.get("name"),
                                                            year=tmdb_info.get(
                                                                "first_air_date")[0:4],
                                                            gtype=2,
                                                            tmdbid=tmdb_id,
                                                            season_count=tmdb_info.get("number_of_seasons"))
                    return {"code": 0, "msg": ""}
                else:
                    return {"code": 1, "msg": "识别词组（TMDB ID）已存在"}
            elif tmdb_type == "movie":
                if not self.dbhelper.is_custom_word_group_existed(tmdbid=tmdb_id, gtype=1):
                    tmdb_info = Media().get_tmdb_info(mtype=MediaType.MOVIE, tmdbid=tmdb_id)
                    if not tmdb_info:
                        return {"code": 1, "msg": "添加失败，无法查询到TMDB信息"}
                    self.dbhelper.insert_custom_word_groups(title=tmdb_info.get("title"),
                                                            year=tmdb_info.get(
                                                                "release_date")[0:4],
                                                            gtype=1,
                                                            tmdbid=tmdb_id,
                                                            season_count=0)
                    return {"code": 0, "msg": ""}
                else:
                    return {"code": 1, "msg": "识别词组（TMDB ID）已存在"}
            else:
                return {"code": 1, "msg": "无法识别媒体类型"}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": str(e)}

    def __delete_custom_word_group(self, data):
        try:
            gid = data.get("gid")
            self.dbhelper.delete_custom_word_group(gid=gid)
            WordsHelper().init_config()
            return {"code": 0, "msg": ""}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": str(e)}

    def __add_or_edit_custom_word(self, data):
        try:
            wid = data.get("id")
            gid = data.get("gid")
            group_type = data.get("group_type")
            replaced = data.get("new_replaced")
            replace = data.get("new_replace")
            front = data.get("new_front")
            back = data.get("new_back")
            offset = data.get("new_offset")
            whelp = data.get("new_help")
            wtype = data.get("type")
            season = data.get("season")
            enabled = data.get("enabled")
            regex = data.get("regex")
            # 集数偏移格式检查
            if wtype in ["3", "4"]:
                if not re.findall(r'EP', offset):
                    return {"code": 1, "msg": "偏移集数格式有误"}
                if re.findall(r'(?!-|\+|\*|/|[0-9]).', re.sub(r'EP', "", offset)):
                    return {"code": 1, "msg": "偏移集数格式有误"}
            if wid:
                self.dbhelper.delete_custom_word(wid=wid)
            # 电影
            if group_type == "1":
                season = -2
            # 屏蔽
            if wtype == "1":
                if not self.dbhelper.is_custom_words_existed(replaced=replaced):
                    self.dbhelper.insert_custom_word(replaced=replaced,
                                                     replace="",
                                                     front="",
                                                     back="",
                                                     offset="",
                                                     wtype=wtype,
                                                     gid=gid,
                                                     season=season,
                                                     enabled=enabled,
                                                     regex=regex,
                                                     whelp=whelp if whelp else "")
                    WordsHelper().init_config()
                    return {"code": 0, "msg": ""}
                else:
                    return {"code": 1, "msg": "识别词已存在\n（被替换词：%s）" % replaced}
            # 替换
            elif wtype == "2":
                if not self.dbhelper.is_custom_words_existed(replaced=replaced):
                    self.dbhelper.insert_custom_word(replaced=replaced,
                                                     replace=replace,
                                                     front="",
                                                     back="",
                                                     offset="",
                                                     wtype=wtype,
                                                     gid=gid,
                                                     season=season,
                                                     enabled=enabled,
                                                     regex=regex,
                                                     whelp=whelp if whelp else "")
                    WordsHelper().init_config()
                    return {"code": 0, "msg": ""}
                else:
                    return {"code": 1, "msg": "识别词已存在\n（被替换词：%s）" % replaced}
            # 集偏移
            elif wtype == "4":
                if not self.dbhelper.is_custom_words_existed(front=front, back=back):
                    self.dbhelper.insert_custom_word(replaced="",
                                                     replace="",
                                                     front=front,
                                                     back=back,
                                                     offset=offset,
                                                     wtype=wtype,
                                                     gid=gid,
                                                     season=season,
                                                     enabled=enabled,
                                                     regex=regex,
                                                     whelp=whelp if whelp else "")
                    WordsHelper().init_config()
                    return {"code": 0, "msg": ""}
                else:
                    return {"code": 1, "msg": "识别词已存在\n（前后定位词：%s@%s）" % (front, back)}
            # 替换+集偏移
            elif wtype == "3":
                if not self.dbhelper.is_custom_words_existed(replaced=replaced):
                    self.dbhelper.insert_custom_word(replaced=replaced,
                                                     replace=replace,
                                                     front=front,
                                                     back=back,
                                                     offset=offset,
                                                     wtype=wtype,
                                                     gid=gid,
                                                     season=season,
                                                     enabled=enabled,
                                                     regex=regex,
                                                     whelp=whelp if whelp else "")
                    WordsHelper().init_config()
                    return {"code": 0, "msg": ""}
                else:
                    return {"code": 1, "msg": "识别词已存在\n（被替换词：%s）" % replaced}
            else:
                return {"code": 1, "msg": ""}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": str(e)}

    def __get_custom_word(self, data):
        try:
            wid = data.get("wid")
            word_info = self.dbhelper.get_custom_words(wid=wid)
            if word_info:
                word_info = word_info[0]
                word = {"id": word_info.ID,
                        "replaced": word_info.REPLACED,
                        "replace": word_info.REPLACE,
                        "front": word_info.FRONT,
                        "back": word_info.BACK,
                        "offset": word_info.OFFSET,
                        "type": word_info.TYPE,
                        "group_id": word_info.GROUP_ID,
                        "season": word_info.SEASON,
                        "enabled": word_info.ENABLED,
                        "regex": word_info.REGEX,
                        "help": word_info.HELP, }
            else:
                word = {}
            return {"code": 0, "data": word}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": "查询识别词失败"}

    def __delete_custom_word(self, data):
        try:
            wid = data.get("id")
            self.dbhelper.delete_custom_word(wid)
            WordsHelper().init_config()
            return {"code": 0, "msg": ""}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": str(e)}

    def __check_custom_words(self, data):
        try:
            flag_dict = {"enable": 1, "disable": 0}
            ids_info = data.get("ids_info")
            enabled = flag_dict.get(data.get("flag"))
            ids = [id_info.split("_")[1] for id_info in ids_info]
            for wid in ids:
                self.dbhelper.check_custom_word(wid=wid, enabled=enabled)
            WordsHelper().init_config()
            return {"code": 0, "msg": ""}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": "识别词状态设置失败"}

    def __export_custom_words(self, data):
        try:
            note = data.get("note")
            ids_info = data.get("ids_info").split("@")
            group_ids = []
            word_ids = []
            for id_info in ids_info:
                wid = id_info.split("_")
                group_ids.append(wid[0])
                word_ids.append(wid[1])
            export_dict = {}
            for group_id in group_ids:
                if group_id == "-1":
                    export_dict["-1"] = {"id": -1,
                                         "title": "通用",
                                         "type": 1,
                                         "words": {}, }
                else:
                    group_info = self.dbhelper.get_custom_word_groups(
                        gid=group_id)
                    if group_info:
                        group_info = group_info[0]
                        export_dict[str(group_info.ID)] = {"id": group_info.ID,
                                                           "title": group_info.TITLE,
                                                           "year": group_info.YEAR,
                                                           "type": group_info.TYPE,
                                                           "tmdbid": group_info.TMDBID,
                                                           "season_count": group_info.SEASON_COUNT,
                                                           "words": {}, }
            for word_id in word_ids:
                word_info = self.dbhelper.get_custom_words(wid=word_id)
                if word_info:
                    word_info = word_info[0]
                    export_dict[str(word_info.GROUP_ID)]["words"][str(word_info.ID)] = {"id": word_info.ID,
                                                                                        "replaced": word_info.REPLACED,
                                                                                        "replace": word_info.REPLACE,
                                                                                        "front": word_info.FRONT,
                                                                                        "back": word_info.BACK,
                                                                                        "offset": word_info.OFFSET,
                                                                                        "type": word_info.TYPE,
                                                                                        "season": word_info.SEASON,
                                                                                        "regex": word_info.REGEX,
                                                                                        "help": word_info.HELP, }
            export_string = json.dumps(export_dict) + "@@@@@@" + str(note)
            string = base64.b64encode(
                export_string.encode("utf-8")).decode('utf-8')
            return {"code": 0, "string": string}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": str(e)}

    @staticmethod
    def __analyse_import_custom_words_code(data):
        try:
            import_code = data.get('import_code')
            string = base64.b64decode(import_code.encode(
                "utf-8")).decode('utf-8').split("@@@@@@")
            note_string = string[1]
            import_dict = json.loads(string[0])
            groups = []
            for group in import_dict.values():
                wid = group.get('id')
                title = group.get("title")
                year = group.get("year")
                wtype = group.get("type")
                tmdbid = group.get("tmdbid")
                season_count = group.get("season_count") or ""
                words = group.get("words")
                if tmdbid:
                    link = "https://www.themoviedb.org/%s/%s" % (
                        "movie" if int(wtype) == 1 else "tv", tmdbid)
                else:
                    link = ""
                groups.append({"id": wid,
                               "name": "%s（%s）" % (title, year) if year else title,
                               "link": link,
                               "type": wtype,
                               "seasons": season_count,
                               "words": words})
            return {"code": 0, "groups": groups, "note_string": note_string}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": str(e)}

    def __import_custom_words(self, data):
        try:
            import_code = data.get('import_code')
            ids_info = data.get('ids_info')
            string = base64.b64decode(import_code.encode(
                "utf-8")).decode('utf-8').split("@@@@@@")
            import_dict = json.loads(string[0])
            import_group_ids = [id_info.split("_")[0] for id_info in ids_info]
            group_id_dict = {}
            for import_group_id in import_group_ids:
                import_group_info = import_dict.get(import_group_id)
                if int(import_group_info.get("id")) == -1:
                    group_id_dict["-1"] = -1
                    continue
                title = import_group_info.get("title")
                year = import_group_info.get("year")
                gtype = import_group_info.get("type")
                tmdbid = import_group_info.get("tmdbid")
                season_count = import_group_info.get("season_count")
                if not self.dbhelper.is_custom_word_group_existed(tmdbid=tmdbid, gtype=gtype):
                    self.dbhelper.insert_custom_word_groups(title=title,
                                                            year=year,
                                                            gtype=gtype,
                                                            tmdbid=tmdbid,
                                                            season_count=season_count)
                group_info = self.dbhelper.get_custom_word_groups(
                    tmdbid=tmdbid, gtype=gtype)
                if group_info:
                    group_id_dict[import_group_id] = group_info[0].ID
            for id_info in ids_info:
                id_info = id_info.split('_')
                import_group_id = id_info[0]
                import_word_id = id_info[1]
                import_word_info = import_dict.get(
                    import_group_id).get("words").get(import_word_id)
                gid = group_id_dict.get(import_group_id)
                replaced = import_word_info.get("replaced")
                replace = import_word_info.get("replace")
                front = import_word_info.get("front")
                back = import_word_info.get("back")
                offset = import_word_info.get("offset")
                whelp = import_word_info.get("help")
                wtype = int(import_word_info.get("type"))
                season = import_word_info.get("season")
                regex = import_word_info.get("regex")
                # 屏蔽, 替换, 替换+集偏移
                if wtype in [1, 2, 3]:
                    if self.dbhelper.is_custom_words_existed(replaced=replaced):
                        return {"code": 1, "msg": "识别词已存在\n（被替换词：%s）" % replaced}
                # 集偏移
                elif wtype == 4:
                    if self.dbhelper.is_custom_words_existed(front=front, back=back):
                        return {"code": 1, "msg": "识别词已存在\n（前后定位词：%s@%s）" % (front, back)}
                self.dbhelper.insert_custom_word(replaced=replaced,
                                                 replace=replace,
                                                 front=front,
                                                 back=back,
                                                 offset=offset,
                                                 wtype=wtype,
                                                 gid=gid,
                                                 season=season,
                                                 enabled=1,
                                                 regex=regex,
                                                 whelp=whelp if whelp else "")
            WordsHelper().init_config()
            return {"code": 0, "msg": ""}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1, "msg": str(e)}

    def __share_filtergroup(self, data):
        gid = data.get("id")
        group_info = self.dbhelper.get_config_filter_group(gid=gid)
        if not group_info:
            return {"code": 1, "msg": "规则组不存在"}
        group_rules = self.dbhelper.get_config_filter_rule(groupid=gid)
        if not group_rules:
            return {"code": 1, "msg": "规则组没有对应规则"}
        rules = []
        for rule in group_rules:
            rules.append({
                "name": rule.ROLE_NAME,
                "pri": rule.PRIORITY,
                "include": rule.INCLUDE,
                "exclude": rule.EXCLUDE,
                "size": rule.SIZE_LIMIT,
                "free": rule.NOTE
            })
        rule_json = {
            "name": group_info[0].GROUP_NAME,
            "rules": rules
        }
        json_string = base64.b64encode(json.dumps(
            rule_json).encode("utf-8")).decode('utf-8')
        return {"code": 0, "string": json_string}

    def __import_filtergroup(self, data):
        content = data.get("content")
        try:
            json_str = base64.b64decode(
                str(content).encode("utf-8")).decode('utf-8')
            json_obj = json.loads(json_str)
            if json_obj:
                if not json_obj.get("name"):
                    return {"code": 1, "msg": "数据格式不正确"}
                self.dbhelper.add_filter_group(name=json_obj.get("name"))
                group_id = self.dbhelper.get_filter_groupid_by_name(
                    json_obj.get("name"))
                if not group_id:
                    return {"code": 1, "msg": "数据内容不正确"}
                if json_obj.get("rules"):
                    for rule in json_obj.get("rules"):
                        self.dbhelper.insert_filter_rule(item={
                            "group": group_id,
                            "name": rule.get("name"),
                            "pri": rule.get("pri"),
                            "include": rule.get("include"),
                            "exclude": rule.get("exclude"),
                            "size": rule.get("size"),
                            "free": rule.get("free")
                        })
                Filter().init_config()
            return {"code": 0, "msg": ""}
        except Exception as err:
            ExceptionUtils.exception_traceback(err)
            return {"code": 1, "msg": "数据格式不正确，%s" % str(err)}

    @staticmethod
    def get_library_spacesize(data=None):
        """
        查询媒体库存储空间
        """
        # 磁盘空间
        UsedPercent = 0
        TotalSpaceList = []
        media = Config().get_config('media')
        if media:
            # 电影目录
            movie_paths = media.get('movie_path')
            if not isinstance(movie_paths, list):
                movie_paths = [movie_paths]
            movie_used, movie_total = 0, 0
            for movie_path in movie_paths:
                if not movie_path:
                    continue
                used, total = SystemUtils.get_used_of_partition(movie_path)
                if "%s-%s" % (used, total) not in TotalSpaceList:
                    TotalSpaceList.append("%s-%s" % (used, total))
                    movie_used += used
                    movie_total += total
            # 电视目录
            tv_paths = media.get('tv_path')
            if not isinstance(tv_paths, list):
                tv_paths = [tv_paths]
            tv_used, tv_total = 0, 0
            for tv_path in tv_paths:
                if not tv_path:
                    continue
                used, total = SystemUtils.get_used_of_partition(tv_path)
                if "%s-%s" % (used, total) not in TotalSpaceList:
                    TotalSpaceList.append("%s-%s" % (used, total))
                    tv_used += used
                    tv_total += total
            # 动漫目录
            anime_paths = media.get('anime_path')
            if not isinstance(anime_paths, list):
                anime_paths = [anime_paths]
            anime_used, anime_total = 0, 0
            for anime_path in anime_paths:
                if not anime_path:
                    continue
                used, total = SystemUtils.get_used_of_partition(anime_path)
                if "%s-%s" % (used, total) not in TotalSpaceList:
                    TotalSpaceList.append("%s-%s" % (used, total))
                    anime_used += used
                    anime_total += total
            # 总空间
            TotalSpaceAry = []
            if movie_total not in TotalSpaceAry:
                TotalSpaceAry.append(movie_total)
            if tv_total not in TotalSpaceAry:
                TotalSpaceAry.append(tv_total)
            if anime_total not in TotalSpaceAry:
                TotalSpaceAry.append(anime_total)
            TotalSpace = sum(TotalSpaceAry)
            # 已使用空间
            UsedSapceAry = []
            if movie_used not in UsedSapceAry:
                UsedSapceAry.append(movie_used)
            if tv_used not in UsedSapceAry:
                UsedSapceAry.append(tv_used)
            if anime_used not in UsedSapceAry:
                UsedSapceAry.append(anime_used)
            UsedSapce = sum(UsedSapceAry)
            # 电影电视使用百分比格式化
            if TotalSpace:
                UsedPercent = "%0.1f" % ((UsedSapce / TotalSpace) * 100)
            # 总剩余空间 格式化
            FreeSpace = "{:,} TB".format(
                round((TotalSpace - UsedSapce) / 1024 / 1024 / 1024 / 1024, 2))
            # 总使用空间 格式化
            UsedSapce = "{:,} TB".format(
                round(UsedSapce / 1024 / 1024 / 1024 / 1024, 2))
            # 总空间 格式化
            TotalSpace = "{:,} TB".format(
                round(TotalSpace / 1024 / 1024 / 1024 / 1024, 2))

            return {"code": 0,
                    "UsedPercent": UsedPercent,
                    "FreeSpace": FreeSpace,
                    "UsedSapce": UsedSapce,
                    "TotalSpace": TotalSpace}

    def get_transfer_statistics(self, data=None):
        """
        查询转移历史统计数据
        """
        MovieChartLabels = []
        MovieNums = []
        TvChartData = {}
        TvNums = []
        AnimeNums = []
        for statistic in self.dbhelper.get_transfer_statistics():
            if statistic[0] == "电影":
                MovieChartLabels.append(statistic[1])
                MovieNums.append(statistic[2])
            else:
                if not TvChartData.get(statistic[1]):
                    TvChartData[statistic[1]] = {"tv": 0, "anime": 0}
                if statistic[0] == "电视剧":
                    TvChartData[statistic[1]]["tv"] += statistic[2]
                elif statistic[0] == "动漫":
                    TvChartData[statistic[1]]["anime"] += statistic[2]
        TvChartLabels = list(TvChartData)
        for tv_data in TvChartData.values():
            TvNums.append(tv_data.get("tv"))
            AnimeNums.append(tv_data.get("anime"))

        return {
            "code": 0,
            "MovieChartLabels": MovieChartLabels,
            "MovieNums": MovieNums,
            "TvChartLabels": TvChartLabels,
            "TvNums": TvNums,
            "AnimeNums": AnimeNums
        }

    @staticmethod
    def get_library_mediacount(data=None):
        """
        查询媒体库统计数据
        """
        MediaServerClient = MediaServer()
        media_counts = MediaServerClient.get_medias_count()
        UserCount = MediaServerClient.get_user_count()
        if media_counts:
            return {
                "code": 0,
                "Movie": "{:,}".format(media_counts.get('MovieCount')),
                "Series": "{:,}".format(media_counts.get('SeriesCount')),
                "Episodes": "{:,}".format(media_counts.get('EpisodeCount')) if media_counts.get(
                    'EpisodeCount') else "",
                "Music": "{:,}".format(media_counts.get('SongCount')),
                "User": UserCount
            }
        else:
            return {"code": -1, "msg": "媒体库服务器连接失败"}

    @staticmethod
    def get_library_playhistory(data=None):
        """
        查询媒体库播放记录
        """
        return {"code": 0, "result": MediaServer().get_activity_log(30)}

    @staticmethod
    def search_media_infos(data):
        """
        根据关键字搜索相似词条
        """
        SearchWord = data.get("keyword")
        if not SearchWord:
            return []
        SearchSourceType = data.get("searchtype")
        medias = WebUtils.search_media_infos(keyword=SearchWord,
                                             source=SearchSourceType)

        return {"code": 0, "result": [media.to_dict() for media in medias]}


    def get_transfer_history(self, data):
        """
        查询媒体整理历史记录
        """
        PageNum = data.get("pagenum")
        if not PageNum:
            PageNum = 30
        SearchStr = data.get("keyword")
        CurrentPage = data.get("page")
        if not CurrentPage:
            CurrentPage = 1
        else:
            CurrentPage = int(CurrentPage)
        totalCount, historys = self.dbhelper.get_transfer_history(
            SearchStr, CurrentPage, PageNum)
        historys_list = []
        for history in historys:
            history = history.as_dict()
            sync_mode = history.get("MODE")
            rmt_mode = ModuleConf.get_dictenum_key(
                ModuleConf.RMT_MODES, sync_mode) if sync_mode else ""
            history.update({
                "SYNC_MODE": sync_mode,
                "RMT_MODE": rmt_mode
            })
            historys_list.append(history)
        TotalPage = floor(totalCount / PageNum) + 1

        return {
            "code": 0,
            "total": totalCount,
            "result": historys_list,
            "totalPage": TotalPage,
            "pageNum": PageNum,
            "currentPage": CurrentPage
        }

    def get_unknown_list(self, data=None):
        """
        查询所有未识别记录
        """
        Items = []
        Records = self.dbhelper.get_transfer_unknown_paths()
        for rec in Records:
            if not rec.PATH:
                continue
            path = rec.PATH.replace("\\", "/") if rec.PATH else ""
            path_to = rec.DEST.replace("\\", "/") if rec.DEST else ""
            sync_mode = rec.MODE or ""
            rmt_mode = ModuleConf.get_dictenum_key(ModuleConf.RMT_MODES,
                                                   sync_mode) if sync_mode else ""
            Items.append({
                "id": rec.ID,
                "path": path,
                "to": path_to,
                "name": path,
                "sync_mode": sync_mode,
                "rmt_mode": rmt_mode,
            })

        return {"code": 0, "items": Items}

    def get_customwords(self, data=None):
        words = []
        words_info = self.dbhelper.get_custom_words(gid=-1)
        for word_info in words_info:
            words.append({"id": word_info.ID,
                          "replaced": word_info.REPLACED,
                          "replace": word_info.REPLACE,
                          "front": word_info.FRONT,
                          "back": word_info.BACK,
                          "offset": word_info.OFFSET,
                          "type": word_info.TYPE,
                          "group_id": word_info.GROUP_ID,
                          "season": word_info.SEASON,
                          "enabled": word_info.ENABLED,
                          "regex": word_info.REGEX,
                          "help": word_info.HELP, })
        groups = [{"id": "-1",
                   "name": "通用",
                   "link": "",
                   "type": "1",
                   "seasons": "0",
                   "words": words}]
        groups_info = self.dbhelper.get_custom_word_groups()
        for group_info in groups_info:
            gid = group_info.ID
            name = "%s (%s)" % (group_info.TITLE, group_info.YEAR)
            gtype = group_info.TYPE
            if gtype == 1:
                link = "https://www.themoviedb.org/movie/%s" % group_info.TMDBID
            else:
                link = "https://www.themoviedb.org/tv/%s" % group_info.TMDBID
            words = []
            words_info = self.dbhelper.get_custom_words(gid=gid)
            for word_info in words_info:
                words.append({"id": word_info.ID,
                              "replaced": word_info.REPLACED,
                              "replace": word_info.REPLACE,
                              "front": word_info.FRONT,
                              "back": word_info.BACK,
                              "offset": word_info.OFFSET,
                              "type": word_info.TYPE,
                              "group_id": word_info.GROUP_ID,
                              "season": word_info.SEASON,
                              "enabled": word_info.ENABLED,
                              "regex": word_info.REGEX,
                              "help": word_info.HELP, })
            groups.append({"id": gid,
                           "name": name,
                           "link": link,
                           "type": group_info.TYPE,
                           "seasons": group_info.SEASON_COUNT,
                           "words": words})
        return {
            "code": 0,
            "result": groups
        }

    def get_directorysync(self, data=None):
        """
        查询所有同步目录
        """
        sync_paths = self.dbhelper.get_config_sync_paths()
        SyncPaths = []
        if sync_paths:
            for sync_item in sync_paths:
                SyncPath = {'id': sync_item.ID,
                            'from': sync_item.SOURCE,
                            'to': sync_item.DEST or "",
                            'unknown': sync_item.UNKNOWN or "",
                            'syncmod': sync_item.MODE,
                            'syncmod_name': RmtMode[sync_item.MODE.upper()].value,
                            'rename': sync_item.RENAME,
                            'enabled': sync_item.ENABLED}
                SyncPaths.append(SyncPath)
        SyncPaths = sorted(SyncPaths, key=lambda o: o.get("from"))
        return {"code": 0, "result": SyncPaths}

    def get_users(self, data=None):
        """
        查询所有用户
        """
        user_list = self.dbhelper.get_users()
        Users = []
        for user in user_list:
            pris = str(user.PRIS).split(",")
            Users.append({"id": user.ID, "name": user.NAME, "pris": pris})
        return {"code": 0, "result": Users}

    @staticmethod
    def get_filterrules(data=None):
        """
        查询所有过滤规则
        """
        RuleGroups = Filter().get_rule_infos()
        sql_file = os.path.join(Config().get_root_path(),
                                "config", "init_filter.sql")
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_list = f.read().split(';\n')
            Init_RuleGroups = []
            i = 0
            while i < len(sql_list):
                rulegroup = {}
                rulegroup_info = re.findall(
                    r"[0-9]+,'[^\"]+NULL", sql_list[i], re.I)[0].split(",")
                rulegroup['id'] = int(rulegroup_info[0])
                rulegroup['name'] = rulegroup_info[1][1:-1]
                rulegroup['rules'] = []
                rulegroup['sql'] = [sql_list[i]]
                if i + 1 < len(sql_list):
                    rules = re.findall(
                        r"[0-9]+,'[^\"]+NULL", sql_list[i + 1], re.I)[0].split("),\n (")
                    for rule in rules:
                        rule_info = {}
                        rule = rule.split(",")
                        rule_info['name'] = rule[2][1:-1]
                        rule_info['include'] = rule[4][1:-1]
                        rule_info['exclude'] = rule[5][1:-1]
                        rulegroup['rules'].append(rule_info)
                    rulegroup["sql"].append(sql_list[i + 1])
                Init_RuleGroups.append(rulegroup)
                i = i + 2
        return {
            "code": 0,
            "ruleGroups": RuleGroups,
            "initRules": Init_RuleGroups
        }

    def __update_directory(self, data):
        """
        维护媒体库目录
        """
        cfg = self.set_config_directory(Config().get_config(),
                                        data.get("oper"),
                                        data.get("key"),
                                        data.get("value"),
                                        data.get("replace_value"))
        # 保存配置
        Config().save_config(cfg)
        return {"code": 0}

    @staticmethod
    def __get_sub_path(data):
        """
        查询下级子目录
        """
        r = []
        try:
            ft = data.get("filter") or "ALL"
            d = data.get("dir")
            if not d or d == "/":
                if SystemUtils.get_system() == OsType.WINDOWS:
                    partitions = SystemUtils.get_windows_drives()
                    if partitions:
                        dirs = [os.path.join(partition, "/")
                                for partition in partitions]
                    else:
                        dirs = [os.path.join("C:/", f)
                                for f in os.listdir("C:/")]
                else:
                    dirs = [os.path.join("/", f) for f in os.listdir("/")]
            else:
                d = os.path.normpath(unquote(d))
                if not os.path.isdir(d):
                    d = os.path.dirname(d)
                dirs = [os.path.join(d, f) for f in os.listdir(d)]
            dirs.sort()
            for ff in dirs:
                if os.path.isdir(ff):
                    if 'ONLYDIR' in ft or 'ALL' in ft:
                        r.append({
                            "path": ff.replace("\\", "/"),
                            "name": os.path.basename(ff),
                            "type": "dir",
                            "rel": os.path.dirname(ff).replace("\\", "/")
                        })
                else:
                    ext = os.path.splitext(ff)[-1][1:]
                    flag = False
                    if 'ONLYFILE' in ft or 'ALL' in ft:
                        flag = True
                    elif "MEDIAFILE" in ft and f".{str(ext).lower()}" in RMT_MEDIAEXT:
                        flag = True
                    elif "SUBFILE" in ft and f".{str(ext).lower()}" in RMT_SUBEXT:
                        flag = True
                    if flag:
                        r.append({
                            "path": ff.replace("\\", "/"),
                            "name": os.path.basename(ff),
                            "type": "file",
                            "rel": os.path.dirname(ff).replace("\\", "/"),
                            "ext": ext,
                            "size": StringUtils.str_filesize(os.path.getsize(ff))
                        })

        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {
                "code": -1,
                "message": '加载路径失败: %s' % str(e)
            }
        return {
            "code": 0,
            "count": len(r),
            "data": r
        }

    @staticmethod
    def __rename_file(data):
        """
        文件重命名
        """
        path = data.get("path")
        name = data.get("name")
        if path and name:
            try:
                os.rename(path, os.path.join(os.path.dirname(path), name))
            except Exception as e:
                ExceptionUtils.exception_traceback(e)
                return {"code": -1, "msg": str(e)}
        return {"code": 0}

    def __delete_files(self, data):
        """
        删除文件
        """
        files = data.get("files")
        if files:
            # 删除文件
            for file in files:
                del_flag, del_msg = self.delete_media_file(filedir=os.path.dirname(file),
                                                           filename=os.path.basename(file))
                if not del_flag:
                    log.error(f"【MediaFile】{del_msg}")
                else:
                    log.info(f"【MediaFile】{del_msg}")
        return {"code": 0}

    @staticmethod
    def __download_subtitle(data):
        """
        从配置的字幕服务下载单个文件的字幕
        """
        path = data.get("path")
        name = data.get("name")
        media = Media().get_media_info(title=name)
        if not media or not media.tmdb_info:
            return {"code": -1, "msg": f"{name} 无法从TMDB查询到媒体信息"}
        if not media.imdb_id:
            media.set_tmdb_info(Media().get_tmdb_info(mtype=media.type,
                                                      tmdbid=media.tmdb_id))
        subtitle_item = [{"type": media.type,
                          "file": os.path.splitext(path)[0],
                          "file_ext": os.path.splitext(name)[-1],
                          "name": media.en_name if media.en_name else media.cn_name,
                          "title": media.title,
                          "year": media.year,
                          "season": media.begin_season,
                          "episode": media.begin_episode,
                          "bluray": False,
                          "imdbid": media.imdb_id}]
        success, retmsg = Subtitle().download_subtitle(items=subtitle_item)
        if success:
            return {"code": 0, "msg": retmsg}
        else:
            return {"code": -1, "msg": retmsg}

    def __update_message_client(self, data):
        """
        更新消息设置
        """
        name = data.get("name")
        cid = data.get("cid")
        ctype = data.get("type")
        config = data.get("config")
        switchs = data.get("switchs")
        interactive = data.get("interactive")
        enabled = data.get("enabled")
        if cid:
            self.dbhelper.delete_message_client(cid=cid)
        self.dbhelper.insert_message_client(name=name,
                                            ctype=ctype,
                                            config=config,
                                            switchs=switchs,
                                            interactive=interactive,
                                            enabled=enabled)
        Message().init_config()
        return {"code": 0}

    def __delete_message_client(self, data):
        """
        删除消息设置
        """
        if self.dbhelper.delete_message_client(cid=data.get("cid")):
            Message().init_config()
            return {"code": 0}
        else:
            return {"code": 1}

    def __check_message_client(self, data):
        """
        维护消息设置
        """
        flag = data.get("flag")
        cid = data.get("cid")
        ctype = data.get("type")
        checked = data.get("checked")
        if flag == "interactive":
            # TG/WX只能开启一个交互
            if checked:
                self.dbhelper.check_message_client(interactive=0, ctype=ctype)
            self.dbhelper.check_message_client(cid=cid,
                                               interactive=1 if checked else 0)
            Message().init_config()
            return {"code": 0}
        elif flag == "enable":
            self.dbhelper.check_message_client(cid=cid,
                                               enabled=1 if checked else 0)
            Message().init_config()
            return {"code": 0}
        else:
            return {"code": 1}

    @staticmethod
    def __get_message_client(data):
        """
        获取消息设置
        """
        cid = data.get("cid")
        return {"code": 0, "detail": Message().get_message_client_info(cid=cid)}

    @staticmethod
    def __test_message_client(data):
        """
        测试消息设置
        """
        ctype = data.get("type")
        config = json.loads(data.get("config"))
        res = Message().get_status(ctype=ctype, config=config)
        if res:
            return {"code": 0}
        else:
            return {"code": 1}


    @staticmethod
    def __find_hardlinks(data):
        files = data.get("files")
        file_dir = data.get("dir")
        if not files:
            return []
        if not file_dir and os.name != "nt":
            # 取根目录下一级为查找目录
            file_dir = os.path.commonpath(files).replace("\\", "/")
            if file_dir != "/":
                file_dir = "/" + str(file_dir).split("/")[1]
            else:
                return []
        hardlinks = {}
        if files:
            try:
                for file in files:
                    hardlinks[os.path.basename(file)] = SystemUtils(
                    ).find_hardlinks(file=file, fdir=file_dir)
            except Exception as e:
                ExceptionUtils.exception_traceback(e)
                return {"code": 1}
        return {"code": 0, "data": hardlinks}

    @staticmethod
    def __set_system_config(data):
        """
        设置系统设置（数据库）
        """
        key = data.get("key")
        value = data.get("value")
        if not key or not value:
            return {"code": 1}
        try:
            SystemConfig().set_system_config(key=key, value=value)
            return {"code": 0}
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            return {"code": 1}

    @staticmethod
    def send_custom_message(data):
        """
        发送自定义消息
        """
        title = data.get("title")
        text = data.get("text") or ""
        image = data.get("image") or ""
        Message().send_custom_message(title=title, text=text, image=image)
        return {"code": 0}

    @staticmethod
    def get_rmt_modes():
        RmtModes = ModuleConf.RMT_MODES_LITE if SystemUtils.is_lite_version(
        ) else ModuleConf.RMT_MODES
        return [{
            "value": value,
            "name": name.value
        } for value, name in RmtModes.items()]


    @staticmethod
    def __save_user_script(data):
        """
        保存用户自定义脚本
        """
        script = data.get("javascript") or ""
        css = data.get("css") or ""
        SystemConfig().set_system_config(key="CustomScript",
                                         value={
                                             "css": css,
                                             "javascript": script
                                         })
        return {"code": 0, "msg": "保存成功"}
