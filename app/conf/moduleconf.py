# coding: utf-8
from app.utils.types import *


class ModuleConf(object):
    # 菜单对应关系，配置WeChat应用中配置的菜单ID与执行命令的对应关系，需要手工修改
    # 菜单序号在https://work.weixin.qq.com/wework_admin/frame#apps 应用自定义菜单中维护，然后看日志输出的菜单序号是啥（按顺利能猜到的）....
    # 命令对应关系：/ptt 下载文件转移；/ptr 删种；/pts 站点签到；/rst 目录同步；/rss RSS下载；/udt 系统更新
    WECHAT_MENU = {
        '_1_0': '/rst'
    }

    # 全量转移模式
    RMT_MODES = {
        "copy": RmtMode.COPY,
        "link": RmtMode.LINK,
        "softlink": RmtMode.SOFTLINK,
        "move": RmtMode.MOVE,
        "rclone": RmtMode.RCLONE,
        "rclonecopy": RmtMode.RCLONECOPY,
        "minio": RmtMode.MINIO,
        "miniocopy": RmtMode.MINIOCOPY
    }

    # 精简版转移模式
    RMT_MODES_LITE = {
        "copy": RmtMode.COPY,
        "link": RmtMode.LINK,
        "softlink": RmtMode.SOFTLINK,
        "move": RmtMode.MOVE
    }

    # 媒体服务器
    MEDIASERVER_DICT = {
        "emby": MediaServerType.EMBY,
        "jellyfin": MediaServerType.JELLYFIN,
        "plex": MediaServerType.PLEX
    }

    # 消息通知类型
    MESSAGE_CONF = {
        "client": {
            "telegram": {
                "name": "Telegram",
                "img_url": "../static/img/telegram.png",
                "search_type": SearchType.TG,
                "config": {
                    "token": {
                        "id": "telegram_token",
                        "required": True,
                        "title": "Bot Token",
                        "tooltip": "telegram机器人的Token，关注BotFather创建机器人",
                        "type": "text"
                    },
                    "chat_id": {
                        "id": "telegram_chat_id",
                        "required": True,
                        "title": "Chat ID",
                        "tooltip": "接受消息通知的用户、群组或频道Chat ID，关注@getidsbot获取",
                        "type": "text"
                    },
                    "user_ids": {
                        "id": "telegram_user_ids",
                        "required": False,
                        "title": "User IDs",
                        "tooltip": "允许使用交互的用户Chat ID，留空则只允许管理用户使用，关注@getidsbot获取",
                        "type": "text",
                        "placeholder": "使用,分隔多个Id"
                    },
                    "admin_ids": {
                        "id": "telegram_admin_ids",
                        "required": False,
                        "title": "Admin IDs",
                        "tooltip": "允许使用管理命令的用户Chat ID，关注@getidsbot获取",
                        "type": "text",
                        "placeholder": "使用,分隔多个Id"
                    },
                    "webhook": {
                        "id": "telegram_webhook",
                        "required": False,
                        "title": "Webhook",
                        "tooltip": "Telegram机器人消息有两种模式：Webhook或消息轮循；开启后将使用Webhook方式，需要在基础设置中正确配置好外网访问地址，同时受Telegram官方限制，外网访问地址需要设置为以下端口之一：443, 80, 88, 8443，且需要有公网认证的可信SSL证书；关闭后将使用消息轮循方式，使用该方式需要在基础设置->安全处将Telegram ipv4源地址设置为127.0.0.1，如同时使用了内置的SSL证书功能，消息轮循方式可能无法正常使用",
                        "type": "switch"
                    }
                }
            },
            "wechat": {
                "name": "微信",
                "img_url": "../static/img/wechat.png",
                "search_type": SearchType.WX,
                "config": {
                    "corpid": {
                        "id": "wechat_corpid",
                        "required": True,
                        "title": "企业ID",
                        "tooltip": "每个企业都拥有唯一的corpid，获取此信息可在管理后台“我的企业”－“企业信息”下查看“企业ID”（需要有管理员权限）",
                        "type": "text"
                    },
                    "corpsecret": {
                        "id": "wechat_corpsecret",
                        "required": True,
                        "title": "应用Secret",
                        "tooltip": "每个应用都拥有唯一的secret，获取此信息可在管理后台“应用与小程序”－“自建”下查看“Secret”（需要有管理员权限）",
                        "type": "text",
                        "placeholder": "Secret"
                    },
                    "agentid": {
                        "id": "wechat_agentid",
                        "required": True,
                        "title": "应用ID",
                        "tooltip": "每个应用都拥有唯一的agentid，获取此信息可在管理后台“应用与小程序”－“自建”下查看“AgentId”（需要有管理员权限）",
                        "type": "text",
                        "placeholder": "AgentId",
                    },
                    "default_proxy": {
                        "id": "wechat_default_proxy",
                        "required": False,
                        "title": "消息推送代理",
                        "tooltip": "由于微信官方限制，2022年6月20日后创建的企业微信应用需要有固定的公网IP地址并加入IP白名单后才能发送消息，使用有固定公网IP的代理服务器转发可解决该问题；代理服务器需自行搭建，搭建方法可参考项目主页说明",
                        "type": "text",
                        "placeholder": "https://wechat.nastool.cn"
                    },
                    "token": {
                        "id": "wechat_token",
                        "required": False,
                        "title": "Token",
                        "tooltip": "需要交互功能时才需要填写，在微信企业应用管理后台-接收消息设置页面生成，填入完成后重启本应用，然后再在微信页面输入地址确定",
                        "type": "text",
                        "placeholder": "API接收消息Token"
                    },
                    "encodingAESKey": {
                        "id": "wechat_encodingAESKey",
                        "required": False,
                        "title": "EncodingAESKey",
                        "tooltip": "需要交互功能时才需要填写，在微信企业应用管理后台-接收消息设置页面生成，填入完成后重启本应用，然后再在微信页面输入地址确定",
                        "type": "text",
                        "placeholder": "API接收消息EncodingAESKey"
                    }
                }
            },
            "serverchan": {
                "name": "Server酱",
                "img_url": "../static/img/serverchan.png",
                "config": {
                    "sckey": {
                        "id": "serverchan_sckey",
                        "required": True,
                        "title": "SCKEY",
                        "tooltip": "填写ServerChan的API Key，SCT类型，在https://sct.ftqq.com/中申请",
                        "type": "text",
                        "placeholder": "SCT..."
                    }
                }
            },
            "bark": {
                "name": "Bark",
                "img_url": "../static/img/bark.webp",
                "config": {
                    "server": {
                        "id": "bark_server",
                        "required": True,
                        "title": "Bark服务器地址",
                        "tooltip": "自己搭建Bark服务端请实际配置，否则可使用：https://api.day.app",
                        "type": "text",
                        "placeholder": "https://api.day.app",
                        "default": "https://api.day.app"
                    },
                    "apikey": {
                        "id": "bark_apikey",
                        "required": True,
                        "title": "API Key",
                        "tooltip": "在Bark客户端中点击右上角的“...”按钮，选择“生成Bark Key”，然后将生成的KEY填入此处",
                        "type": "text"
                    }
                }
            },
            "pushdeer": {
                "name": "PushDeer",
                "img_url": "../static/img/pushdeer.png",
                "config": {
                    "server": {
                        "id": "pushdeer_server",
                        "required": True,
                        "title": "PushDeer服务器地址",
                        "tooltip": "自己搭建pushdeer服务端请实际配置，否则可使用：https://api2.pushdeer.com",
                        "type": "text",
                        "placeholder": "https://api2.pushdeer.com",
                        "default": "https://api2.pushdeer.com"
                    },
                    "apikey": {
                        "id": "pushdeer_apikey",
                        "required": True,
                        "title": "API Key",
                        "tooltip": "pushdeer客户端生成的KEY",
                        "type": "text"
                    }
                }
            },
            "pushplus": {
                "name": "PushPlus",
                "img_url": "../static/img/pushplus.jpg",
                "config": {
                    "token": {
                        "id": "pushplus_token",
                        "required": True,
                        "title": "Token",
                        "tooltip": "在PushPlus官网中申请，申请地址：http://pushplus.plus/",
                        "type": "text"
                    },
                    "channel": {
                        "id": "pushplus_channel",
                        "required": True,
                        "title": "推送渠道",
                        "tooltip": "使用PushPlus中配置的发送渠道，具体参考pushplus.plus官网文档说明，支持第三方webhook、钉钉、飞书、邮箱等",
                        "type": "select",
                        "options": {
                            "wechat": "微信",
                            "mail": "邮箱",
                            "webhook": "第三方Webhook"
                        },
                        "default": "wechat"
                    },
                    "topic": {
                        "id": "pushplus_topic",
                        "required": False,
                        "title": "群组编码",
                        "tooltip": "PushPlus中创建的群组，如未设置可为空",
                        "type": "text"
                    },
                    "webhook": {
                        "id": "pushplus_webhook",
                        "required": False,
                        "title": "Webhook编码",
                        "tooltip": "PushPlus中创建的webhook编码，发送渠道为第三方webhook时需要填入",
                    }
                }
            },
            "iyuu": {
                "name": "爱语飞飞",
                "img_url": "../static/img/iyuu.png",
                "config": {
                    "token": {
                        "id": "iyuumsg_token",
                        "required": True,
                        "title": "令牌Token",
                        "tooltip": "在爱语飞飞官网中申请，申请地址：https://iyuu.cn/",
                        "type": "text",
                        "placeholder": "登录https://iyuu.cn获取"
                    }
                }
            },
            "slack": {
                "name": "Slack",
                "img_url": "../static/img/slack.png",
                "search_type": SearchType.SLACK,
                "config": {
                    "bot_token": {
                        "id": "slack_bot_token",
                        "required": True,
                        "title": "Bot User OAuth Token",
                        "tooltip": "在Slack中创建应用，获取Bot User OAuth Token",
                        "type": "text",
                        "placeholder": "xoxb-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx"
                    },
                    "app_token": {
                        "id": "slack_app_token",
                        "required": True,
                        "title": "App-Level Token",
                        "tooltip": "在Slack中创建应用，获取App-Level Token",
                        "type": "text",
                        "placeholder": "xapp-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx"
                    }
                }
            },
            "gotify": {
                "name": "Gotify",
                "img_url": "../static/img/gotify.png",
                "config": {
                    "server": {
                        "id": "gotify_server",
                        "required": True,
                        "title": "Gotify服务器地址",
                        "tooltip": "自己搭建gotify服务端地址",
                        "type": "text",
                        "placeholder": "http://localhost:8800"
                    },
                    "token": {
                        "id": "gotify_token",
                        "required": True,
                        "title": "令牌Token",
                        "tooltip": "Gotify服务端APPS下创建的token",
                        "type": "text"
                    },
                    "priority": {
                        "id": "gotify_priority",
                        "required": False,
                        "title": "消息Priority",
                        "tooltip": "消息通知优先级, 请填写数字(1-8), 默认: 8",
                        "type": "text",
                        "placeholder": "8"
                    }
                }
            },
            "chanify": {
                "name": "Chanify",
                "img_url": "../static/img/chanify.png",
                "config": {
                    "server": {
                        "id": "chanify_server",
                        "required": True,
                        "title": "Chanify服务器地址",
                        "tooltip": "自己搭建Chanify服务端地址或使用https://api.chanify.net",
                        "type": "text",
                        "placeholder": "https://api.chanify.net",
                        "default": "https://api.chanify.net"
                    },
                    "token": {
                        "id": "chanify_token",
                        "required": True,
                        "title": "令牌",
                        "tooltip": "在Chanify客户端频道中获取",
                        "type": "text"
                    }
                }
            },
            "synologychat": {
                "name": "Synology Chat",
                "img_url": "../static/img/synologychat.png",
                "search_type": SearchType.SYNOLOGY,
                "config": {
                    "webhook_url": {
                        "id": "synologychat_webhook_url",
                        "required": True,
                        "title": "机器人传入URL",
                        "tooltip": "在Synology Chat中创建机器人，获取机器人传入URL",
                        "type": "text",
                        "placeholder": "https://xxx/webapi/entry.cgi?api=xxx"
                    },
                    "token": {
                        "id": "synologychat_token",
                        "required": True,
                        "title": "令牌",
                        "tooltip": "在Synology Chat中创建机器人，获取机器人令牌",
                        "type": "text",
                        "placeholder": ""
                    }
                }
            },
        },
        "switch": {
            "download_start": {
                "name": "新增下载",
                "fuc_name": "download_start"
            },
            "download_fail": {
                "name": "下载失败",
                "fuc_name": "download_fail"
            },
            "transfer_finished": {
                "name": "入库完成",
                "fuc_name": "transfer_finished"
            },
            "transfer_fail": {
                "name": "入库失败",
                "fuc_name": "transfer_fail"
            },
            "rss_added": {
                "name": "新增订阅",
                "fuc_name": "rss_added"
            },
            "rss_finished": {
                "name": "订阅完成",
                "fuc_name": "rss_finished"
            },
            "site_signin": {
                "name": "站点签到",
                "fuc_name": "site_signin"
            },
            "site_message": {
                "name": "站点消息",
                "fuc_name": "site_message"
            },
            "brushtask_added": {
                "name": "刷流下种",
                "fuc_name": "brushtask_added"
            },
            "brushtask_remove": {
                "name": "刷流删种",
                "fuc_name": "brushtask_remove"
            },
            "mediaserver_message": {
                "name": "媒体服务",
                "fuc_name": "mediaserver_message"
            },
            "custom_message": {
                "name": "自定义消息",
                "fuc_name": "custom_message"
            }
        }
    }

    # 搜索种子过滤属性
    TORRENT_SEARCH_PARAMS = {
        "restype": {
            "BLURAY": r"Blu-?Ray|BD|BDRIP",
            "REMUX": r"REMUX",
            "DOLBY": r"DOLBY|DOVI|\s+DV$|\s+DV\s+",
            "WEB": r"WEB-?DL|WEBRIP",
            "HDTV": r"U?HDTV",
            "UHD": r"UHD",
            "HDR": r"HDR",
            "3D": r"3D"
        },
        "pix": {
            "8k": r"8K",
            "4k": r"4K|2160P|X2160",
            "1080p": r"1080[PIX]|X1080",
            "720p": r"720P"
        }
    }

    # 网络测试对象
    NETTEST_TARGETS = [
        "www.themoviedb.org",
        "api.themoviedb.org",
        "api.tmdb.org",
        "image.tmdb.org",
        "webservice.fanart.tv",
        "api.telegram.org",
        "qyapi.weixin.qq.com",
        "www.opensubtitles.org"
    ]

    # 媒体服务器
    MEDIASERVER_CONF = {
        "emby": {
            "name": "Emby",
            "img_url": "../static/img/emby.png",
            "background": "bg-green",
            "test_command": "app.mediaserver.client.emby|Emby",
            "config": {
                "host": {
                    "id": "emby.host",
                    "required": True,
                    "title": "服务器地址",
                    "tooltip": "配置IP地址和端口，如为https则需要增加https://前缀",
                    "type": "text",
                    "placeholder": "http://127.0.0.1:8096"
                },
                "api_key": {
                    "id": "emby.api_key",
                    "required": True,
                    "title": "Api Key",
                    "tooltip": "在Emby设置->高级->API密钥处生成，注意不要复制到了应用名称",
                    "type": "text",
                    "placeholder": ""
                }
            }
        },
        "jellyfin": {
            "name": "Jellyfin",
            "img_url": "../static/img/jellyfin.jpg",
            "background": "bg-purple",
            "test_command": "app.mediaserver.client.jellyfin|Jellyfin",
            "config": {
                "host": {
                    "id": "jellyfin.host",
                    "required": True,
                    "title": "服务器地址",
                    "tooltip": "配置IP地址和端口，如为https则需要增加https://前缀",
                    "type": "text",
                    "placeholder": "http://127.0.0.1:8096"
                },
                "api_key": {
                    "id": "jellyfin.api_key",
                    "required": True,
                    "title": "Api Key",
                    "tooltip": "在Jellyfin设置->高级->API密钥处生成",
                    "type": "text",
                    "placeholder": ""
                }
            }
        },
        "plex": {
            "name": "Plex",
            "img_url": "../static/img/plex.png",
            "background": "bg-yellow",
            "test_command": "app.mediaserver.client.plex|Plex",
            "config": {
                "host": {
                    "id": "plex.host",
                    "required": True,
                    "title": "服务器地址",
                    "tooltip": "配置IP地址和端口，如为https则需要增加https://前缀",
                    "type": "text",
                    "placeholder": "http://127.0.0.1:32400"
                },
                "token": {
                    "id": "plex.token",
                    "required": False,
                    "title": "X-Plex-Token",
                    "tooltip": "Plex网页Cookie中的X-Plex-Token，通过浏览器F12->网络中获取，如填写将优先使用；Token与服务器名称、用户名及密码 二选一，推荐使用Token，连接速度更快",
                    "type": "text",
                    "placeholder": "X-Plex-Token与其它认证信息二选一"
                },
                "servername": {
                    "id": "plex.servername",
                    "required": False,
                    "title": "服务器名称",
                    "tooltip": "配置Plex设置->左侧下拉框中看到的服务器名称；如填写了Token则无需填写服务器名称、用户名及密码",
                    "type": "text",
                    "placeholder": ""
                },
                "username": {
                    "id": "plex.username",
                    "required": False,
                    "title": "用户名",
                    "type": "text",
                    "placeholder": ""
                },
                "password": {
                    "id": "plex.password",
                    "required": False,
                    "title": "密码",
                    "type": "password",
                    "placeholder": ""
                }
            }
        },
    }

    # 发现过滤器
    DISCOVER_FILTER_CONF = {
        "tmdb_movie": {
            "with_genres": {
                "name": "类型",
                "type": "selectgroup",
                "options": [{'value': 28, 'name': '动作'},
                            {'value': 12, 'name': '冒险'},
                            {'value': 16, 'name': '动画'},
                            {'value': 35, 'name': '喜剧'},
                            {'value': 80, 'name': '犯罪'},
                            {'value': 18, 'name': '剧情'},
                            {'value': 14, 'name': '奇幻'},
                            {'value': 27, 'name': '恐怖'},
                            {'value': 9648, 'name': '悬疑'},
                            {'value': 10749, 'name': '爱情'},
                            {'value': 878, 'name': '科幻'},
                            {'value': 53, 'name': '惊悚'},
                            {'value': 10752, 'name': '战争'}]
            },
            "with_original_language": {
                "name": "语言",
                "type": "selectgroup",
                "options": [{'value': 'zh', 'name': '中文'},
                            {'value': 'en', 'name': '英语'},
                            {'value': 'ja', 'name': '日语'},
                            {'value': 'ko', 'name': '韩语'},
                            {'value': 'fr', 'name': '法语'},
                            {'value': 'de', 'name': '德语'},
                            {'value': 'ru', 'name': '俄语'},
                            {'value': 'hi', 'name': '印地语'}]
            }
        },
        "tmdb_tv": {
            "with_genres": {
                "name": "类型",
                "type": "selectgroup",
                "options": [{'value': 10759, 'name': '动作冒险'},
                            {'value': 16, 'name': '动画'},
                            {'value': 35, 'name': '喜剧'},
                            {'value': 80, 'name': '犯罪'},
                            {'value': 99, 'name': '纪录'},
                            {'value': 18, 'name': '剧情'},
                            {'value': 10762, 'name': '儿童'},
                            {'value': 9648, 'name': '悬疑'},
                            {'value': 10764, 'name': '真人秀'},
                            {'value': 10765, 'name': '科幻'}]
            },
            "with_original_language": {
                "name": "语言",
                "type": "selectgroup",
                "options": [{'id': 'zh', 'name': '中文'},
                            {'id': 'en', 'name': '英语'},
                            {'id': 'ja', 'name': '日语'},
                            {'id': 'ko', 'name': '韩语'},
                            {'id': 'fr', 'name': '法语'},
                            {'id': 'de', 'name': '德语'},
                            {'id': 'ru', 'name': '俄语'},
                            {'id': 'hi', 'name': '印地语'}]
            }
        },
        "douban_movie": {
            "sort": {
                "name": "排序",
                "type": "select",
                "options": [{'value': 'U', 'name': '综合排序'},
                            {'value': 'T', 'name': '首播时间'},
                            {'value': 'S', 'name': '高分优先'},
                            {'value': 'R', 'name': '近期热度'}]
            },
            "类型": {
                "parent": "selected_categories",
                "name": "类型",
                "type": "selectgroup",
                "options": [{"value": "喜剧"},
                            {"value": "爱情"},
                            {"value": "动作"},
                            {"value": "科幻"},
                            {"value": "动画"},
                            {"value": "悬疑"},
                            {"value": "犯罪"},
                            {"value": "惊悚"},
                            {"value": "冒险"},
                            {"value": "奇幻"},
                            {"value": "恐怖"},
                            {"value": "战争"},
                            {"value": "武侠"},
                            {"value": "灾难"}]
            },
            "地区": {
                "parent": "selected_categories",
                "name": "地区",
                "type": "selectgroup",
                "options": [{"value": "华语"},
                            {"value": "中国大陆"},
                            {"value": "中国香港"},
                            {"value": "中国台湾"},
                            {"value": "欧美"},
                            {"value": "韩国"},
                            {"value": "日本"},
                            {"value": "意大利"},
                            {"value": "西班牙"},
                            {"value": "印度"},
                            {"value": "泰国"}]
            }
        },
        "douban_tv": {
            "sort": {
                "name": "排序",
                "type": "select",
                "options": [{'value': 'U', 'name': '综合排序'},
                            {'value': 'T', 'name': '首播时间'},
                            {'value': 'S', 'name': '高分优先'},
                            {'value': 'R', 'name': '近期热度'}]
            },
            "形式": {
                "parent": "selected_categories",
                "name": "形式",
                "type": "select",
                "options": [{"value": "电视剧"},
                            {"value": "综艺"}]
            },
            "类型": {
                "parent": "selected_categories",
                "name": "类型",
                "type": "selectgroup",
                "options": [{"value": "喜剧"},
                            {"value": "爱情"},
                            {"value": "悬疑"},
                            {"value": "动画"},
                            {"value": "武侠"},
                            {"value": "古装"},
                            {"value": "犯罪"},
                            {"value": "科幻"},
                            {"value": "恐怖"},
                            {"value": "历史"},
                            {"value": "战争"},
                            {"value": "动作"},
                            {"value": "冒险"},
                            {"value": "传记"},
                            {"value": "剧情"},
                            {"value": "奇幻"},
                            {"value": "惊悚"},
                            {"value": "灾难"}]
            },
            "地区": {
                "parent": "selected_categories",
                "name": "地区",
                "type": "selectgroup",
                "options": [{"value": "华语"},
                            {"value": "中国大陆"},
                            {"value": "中国香港"},
                            {"value": "中国台湾"},
                            {"value": "欧美"},
                            {"value": "韩国"},
                            {"value": "日本"},
                            {"value": "印度"},
                            {"value": "泰国"}]
            }
        }
    }

    @staticmethod
    def get_enum_name(enum, value):
        """
        根据Enum的value查询name
        :param enum: 枚举
        :param value: 枚举值
        :return: 枚举名或None
        """
        for e in enum:
            if e.value == value:
                return e.name
        return None

    @staticmethod
    def get_enum_item(enum, value):
        """
        根据Enum的value查询name
        :param enum: 枚举
        :param value: 枚举值
        :return: 枚举项
        """
        for e in enum:
            if e.value == value:
                return e
        return None

    @staticmethod
    def get_dictenum_key(dictenum, value):
        """
        根据Enum dict的value查询key
        :param dictenum: 枚举字典
        :param value: 枚举类（字典值）的值
        :return: 字典键或None
        """
        for k, v in dictenum.items():
            if v.value == value:
                return k
        return None
