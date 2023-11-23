class SiteConf:
    # 站点详情页字幕下载链接识别XPATH
    SITE_SUBTITLE_XPATH = [
        '//td[@class="rowhead"][text()="字幕"]/following-sibling::td//a/@href',
    ]
