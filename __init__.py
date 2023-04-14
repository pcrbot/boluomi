import json,re,asyncio
from os.path import dirname, join, exists
from . import download, db
from hoshino import Service, priv
from hoshino import aiorequests

sv_help = '''
[菠萝密 XX] 查看菠萝的秘密
提取：2233
解压：菠萝/菠萝的合集
'''.strip()

sv = Service(
    name = '菠萝密',  #功能名
    use_priv = priv.NORMAL, #使用权限
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = False, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )


@sv.on_fullmatch(["帮助菠萝密"])
async def cwbangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)



curpath = dirname(__file__) #当前路径
save_json_path= join(curpath,'test.json') #json文件的保存路径




def pic_url_64(url):
    return f'[CQ:image,file={url}]'

def cheee(url):
    group = re.match("https://pan.baidu.com/s/([-A-Za-z0-9+&@#/%?=~_|!:,.;]+)[?pwd=]*([a-zA-Z0-9]*)",url)
    if group.group(2):
        msg = "BD～" + group.group(1) + "?pwd=" + group.group(2)
        return msg
    if group.group(1):
        msg = "BD～" + group.group(1)
        return msg

def uncheee(url_str):
    group = re.match("([-A-Za-z0-9+&@#/%?=~_|!:,.;]+)[?pwd=]*([a-zA-Z0-9]*)",url_str)
    if group.group(2):
        msg = "https://pan.baidu.com/s/" + group.group(1) + "?pwd=" + group.group(2)
        return msg
    if group.group(1):
        msg = "https://pan.baidu.com/s/" + group.group(1)
        return msg

@sv.on_prefix('BD～')
async def decherulize(bot, ev):
    s = ev.message.extract_plain_text()
    if len(s) > 1501:
        await bot.send(ev, '？？...？？', at_sender=True)
        return
    msg = '的BD链接是：\n' + uncheee(s)
    to_del = await bot.send(ev, msg, at_sender=True)
    try:
        await asyncio.sleep(30)
        await bot.delete_msg(message_id=to_del['message_id'])
        await bot.delete_msg(message_id=int(ev.message_id))#撤回反馈互动,防止刷屏
    except:
        await bot.send(ev, f"请给bot管理员或群主权限以解锁全部功能")


def get_data():
    cookie_data=download.user_data()
    url = r"https://docs.qq.com/sheet/DSlFXWWxMSXlSVFhZ?tab=BB08J2&scode="
    title, tabs, opendoc_params = download.initial_fetch(url,cookie_data=cookie_data)
    print("文档名称: %s" % title)
    with open(save_json_path,"r",encoding="utf-8") as f:
        remsg = json.loads(f.read())
    #remsg = {}
    tosend = ""
    for tab in tabs:
        rmsg = {}
        tab_id = tab["id"]
        name = tab["name"]
        print("正在下载: %s" % name)
        sheet_content, max_col,img_url = download.read_sheet(url, tab_id, opendoc_params,cookie_data)
        for k, v in sheet_content.items():
            if '2' in v:
                msg = v['6'] if '6' in v else v['2'][1]
                if msg == '3D' or msg == 'MMD' or msg == '2D':
                    k1 = str(int(k)+1)
                    img = sheet_content[k1]['14'][0] if '14' in sheet_content[k1] else ""
                    k1 = str(int(k)+2)
                    name1 = sheet_content[k1]['2'][1] if '2' in sheet_content[k1] else ""
                    type_ = msg
                    k1 = str(int(k)+3)
                    time = sheet_content[k1]['2'][1] if '2' in sheet_content[k1] else 1
                    k1 = str(int(k)+4)
                    title1 = sheet_content[k1]['2'][1] if '2' in sheet_content[k1] else ""
                    k1 = str(int(k)+5)
                    url1 = sheet_content[k1]['6'] if '2' in sheet_content[k1] and '6' in sheet_content[k1] else ""
                    try:
                        img2 = img_url[img]
                    except:
                        img2 = ""
                    if name1 in remsg[name]:
                        name2 = remsg[name][name1]["更新贴"]
                        if name2 != title1:
                            url_cheee = cheee(url1)
                            tosend += f"菠萝の秘密\n[CQ:image,file={img2}]\n作者：{name1}\n更新贴：{title1}\n{url_cheee}\n"
                    rmsg[name1] = {"头像":img2,"类型":type_,"更新时间":time,"更新贴":title1,"网盘":url1}
        remsg[name] = rmsg
    with open(save_json_path,"w",encoding="utf-8") as f:
        f.write(json.dumps(remsg, indent=4,ensure_ascii=False))
    return tosend


def update_db():
    with open(save_json_path,"r",encoding="utf-8") as f:
        data = json.loads(f.read())
    for i in data:
        if data[i]:
            for j in data[i]:
                boluo_name = j
                boluo_pic = data[i][j]["头像"]
                boluo_type = data[i][j]["类型"]
                boluo_time = data[i][j]["更新时间"]
                boluo_titel = data[i][j]["更新贴"]
                boluo_url = data[i][j]["网盘"]
                db.add_boluo(boluo_name, boluo_pic, boluo_type, boluo_time, boluo_titel, boluo_url)




@sv.scheduled_job('cron', minute='*/30')
async def boluomi_broad():
    msg = get_data()
    update_db()
    print(msg)
    if msg:
        await sv.broadcast(msg, '菠萝密', 0.5)
    # else:
    #     await sv.broadcast("菠萝密成功启动了哦", '菠萝密', 0.5)


@sv.on_prefix('菠萝密')
async def bolomi(bot, ev):
    tags = ev.message.extract_plain_text().strip()
    remsg = db.like_boluo(tags)
    if remsg:
        msg = ""
        for i in remsg:
            pan_cheee = cheee(i[5])
            msg += f"菠萝密已取来\n作者：{i[0]}\n[CQ:image,file={i[1]}]\n类型：{i[2]}\n更新贴：{i[4]}\n{pan_cheee}\n"
        await bot.send(ev, msg, at_sender=True)
    else:
        await bot.send(ev, "没有找到哦~", at_sender=True)
