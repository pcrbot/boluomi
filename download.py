import string
import requests
import re
from urllib.parse import urlparse
import json,datetime,time


cookie_string = 'RK=tjHwkemE7g; ptcz=1ef4422208dec2b1d430cc558e4fb820f7de768720151c5ad3a67930f0c3ae73; iip=0; pac_uid=1_3264218165; fingerprint=30c57cf8aa42413791e0869e8043f03766; pgv_pvid=4539286888; fqm_pvqid=88273108-5bca-444f-b43b-e92a77b95211; low_login_enable=1; o_cookie=3264218165; tvfe_boss_uuid=224c9cd8f0973530; adtag=s_pcqq_panel_app; has_been_login=1; luin=o3264218165; lskey=0001000089672044f87065bb11e815e5d52ed2b71e1fbca22f9ec9383a2dd61ced545bc6cfa693bbbd82542b; p_luin=o3264218165; p_lskey=000400003cdf8441f9ba835a3822cdacc3bc43c207f6f2dcfb83f756f9c508e72e8d26dcd69da3a0e152971a; DOC_QQ_APPID=101458937; DOC_QQ_OPENID=8E1FCFB1C8C1745DE1F3C80FE9EA712A; DOC_SID=fd471ed6c1d94581a41bfa7cc0757fafc8be7fbd1974471c9395fff7389664b6; SID=fd471ed6c1d94581a41bfa7cc0757fafc8be7fbd1974471c9395fff7389664b6; backup_cdn_domain=docs.gtimg.com; loginTime=1681388985710; adtag=s_pcqq_panel_app; optimal_cdn_domain=docs2.gtimg.com; traceid=94cfab5ec4; TOK=94cfab5ec41207cf; hashkey=94cfab5e'  #腾讯文档cookies，我相信你们不会搞坏事的

class user_data():
    def __init__(self):
        self.cookies = None

    def set_cookies(self, cookiesfile):
        self.cookies = None

    def get_cookies(self):
        cookie_headers = {'cookie': cookie_string}
        return cookie_headers


def initial_fetch(url:string, cookie_data:user_data):
    init_url = re.search(r"((.+))\?|(.+)",url).group(1) # 无url参数的形式的url

    t = datetime.datetime.timestamp( datetime.datetime.now() )
    t = int(t*1000) # 取当前毫秒时间戳，不需要从页面获取
    id = re.search(r"/sheet/(.+)\??", init_url).group(1)

    opendoc_url = "https://docs.qq.com/dop-api/opendoc"
    opendoc_params={
        "id" : id,
        "normal" : "1",
        "outformat" : "1",
        "startrow" : "0",
        "endrow" : "60",
        "wb" : "1",
        "nowb" : "0",
        "callback" : "clientVarsCallback",
        "xsrf" : "",
        "t" : t
    }
    header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Referer":re.search(r"(.+)\?|(.+)",init_url).group(0),
        # "cookie": cookie_string
    }
    header.update(cookie_data.get_cookies())

    opendoc_text = requests.get(opendoc_url, headers=header, params=opendoc_params).text
    opendoc_json = read_callback(opendoc_text)
    title = opendoc_json["clientVars"]["title"]
    tabs = opendoc_json["clientVars"]["collab_client_vars"]["header"][0]["d"]
    padId = opendoc_json["clientVars"]["collab_client_vars"]["globalPadId"]


    return title, tabs, opendoc_params

def read_sheet(url:string, sheet, opendoc_params, cookie_data:user_data):
    init_url = url
    opendoc_url = "https://docs.qq.com/dop-api/opendoc"
    opendoc_params["tab"] = sheet

    header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Referer":re.search(r"(.+)\?|(.+)",init_url).group(0),
        # "cookie": cookie_string
    }
    header.update(cookie_data.get_cookies())

    opendoc_text = requests.get(opendoc_url, headers=header, params=opendoc_params).text
    opendoc_json = read_callback(opendoc_text)
    max_row = opendoc_json["clientVars"]["collab_client_vars"]["maxRow"]
    max_col = opendoc_json["clientVars"]["collab_client_vars"]["maxCol"]
    padId = opendoc_json["clientVars"]["collab_client_vars"]["globalPadId"]
    rev = opendoc_json["clientVars"]["collab_client_vars"]["rev"]

    sheet_url = "https://docs.qq.com/dop-api/get/sheet"
    sheet_params={
        "tab" : sheet,
        "padId" : padId,
        "subId" : sheet,
        "outformat" : "1",
        "startrow" : "0",
        "endrow" : max_row,
        "normal" : "1",
        "preview_token" : "",
        "nowb" : "1",
        "rev" : rev
    }
    sheet_text = requests.get(sheet_url, headers=header, params=sheet_params).text
    sheet_json = json.loads(sheet_text)
    # sheet_content = sheet_json["data"]["initialAttributedText"]["text"][0][-1][0]["c"][1]
    sheet_content = {}
    img_url = {}
    for temp_class in sheet_json["data"]["initialAttributedText"]["text"][0]:
        if type(temp_class[0]) == dict and "c" in temp_class[0].keys():
            if len(temp_class[0]["c"]) > 1 and type(temp_class[0]["c"][1]) == dict:
                temp = temp_class[0]["c"][1] # type: dict
                for k, v in temp.items():
                    if k.isdigit() and type(v) == dict:
                        sheet_content[k] = v
            if temp_class[0]["c"][0] == "cell-image":
                temp = temp_class
                for i in temp:
                    if i["c"][0] == "cell-image":
                        url = i["c"][2]
                        img_url[url] = i["c"][3]
    return sheet_content, max_col,img_url

def read_callback(text):
    content = re.search(r"clientVarsCallback\(\"(.+)\"\)", text).group(1)
    content = content.replace("&#34;", "\"")
    content = content.replace(r'\\"', r"\\'")
    return json.loads(content)


