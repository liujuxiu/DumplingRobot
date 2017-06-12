#coding=utf8
import requests
import itchat
import checkFriend
import pickle as pk
import dHash
import random
from PIL import Image
import jieba
import fenci
import jieba.analyse
#基本聊天回复 斗图 学习功能 好友关系检测
#Tuling Key 为与图灵机器人对话权限
KEY = '8edce3ce905a4c1dbb965e6b35c3834d'
listmessage=['发个图片','斗图']
MAP = {}
MAP1={}
LIST=[]
MAP_FILE = None
MAP1_FILE = None
PIC_FILE=None
mappic={'5.jpg':['2.jpg','4.jpg','1.jpg'],'4.jpg':'7.jpg','2.jpg':'7.jpg','7.jpg':'8.jpg','8.jpg':'9.jpg',
        '9.jpg':'10.jpg','10.jpg':'11.jpg','11.jpg':'13.gif','13.gif':'14.jpg','14.jpg':'13.jpg',
        '13.jpg':'15.jpg','15.jpg':'16.jpg','16.jpg':'17.jpg','17.jpg':'18.jpg','18.jpg':'22.jpg',
'22.jpg':'21.jpg','21.jpg':'19.jpg','19.jpg':'20.jpg','20.jpg':'23.jpg','23.jpg':'4.jpg'}

#发送文本至图灵，返回图灵的回复  无响应则返回None
def get_response(msg):
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : KEY,
        'info'   : msg,
        'userid' : 'wechat-robot',
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        return r.get('text')
    except:
        return
#文本注册方式 教说话(群聊 与好友)
@itchat.msg_register(itchat.content.TEXT,isFriendChat=True,isGroupChat=True)
def tuling_replset(msg):
    text = msg['Text']
    if text == 'HELP':
        return \
        u'''
         教说话,格式为
         :question:answer
        '''
    if text in listmessage:
        itchat.send('@%s@%s' % ('img', './images/'
                                + LIST[random.randint(0, len(LIST) - 1)]), msg['FromUserName'])
        return \
            u'''看！这是你要的图片'''
    if text[0]==':' and text.count(':') == 2:
        msgs = text[1:].split(':')
        segkey=fenci.segmentation(msgs[0])
        print(segkey)
        for seg in MAP.keys():
            chongfu = True
            for word in segkey:
                if word not in seg:
                    chongfu = False
                    break
            if chongfu:
                del MAP[seg]
               # print("del map item",seg)
                break
        MAP[segkey] = msgs[1]
        MAP1[msgs[0]] = msgs[1]
        with open('MAP.pk', 'wb') as MAP_FILE:
            pk.dump(MAP,MAP_FILE)
        with open('MAP1.pk', 'wb') as MAP1_FILE:
            pk.dump(MAP1,MAP1_FILE)
        return \
        u'''
        learning success
        '''
    #1、直接匹配
    if text in MAP1.keys():
        return MAP1[text]
    #分词
    extract_seg = jieba.analyse.extract_tags(text)
    textseg=fenci.segmentation(text)
   # print("fenci jieguo")
    #print(extract_seg)
    #print(textseg)
    #print("find ans")
    max=0
    min = 10000000
    maxtuple=None
    reply1 = None
    #print(MAP)
    #关键词匹配
    if extract_seg:
        for key in MAP.keys():
            segcount = 0
            for ex in extract_seg:
                if ex in key:
                    segcount += 1
            if max <= segcount and segcount >= 1:
                max = segcount
                maxtuple = key
                reply1 = MAP[maxtuple]
                print("ex  " + reply1)
    if not reply1: #模糊匹配
        #print("start match")
        for key in MAP.keys():
            segcount = 0
            notcount = 0
            for ts in textseg:
                for word in key:
                    if ts in word:
                        segcount += 1
                    else :
                        notcount += 1
            size = len(textseg)*len(key)
            if((segcount >= 1 and notcount/size < 0.8 ) or segcount >= 3):
                if (max < segcount ) or (notcount < min and  max <= segcount):
                    max = segcount
                    min = notcount
                    maxtuple = key
                    reply1 = MAP[maxtuple]
            #print("match segcount:%d notcount:%d now reply:%s "%(segcount,notcount,reply1))
    if reply1:
        return reply1
    else:
        #图灵回复
        reply = get_response(text)
        return reply

try:
    MAP_FILE = open('MAP.pk','rb')
except:
    MAP_FILE = open('MAP.pk', 'wb')
    pk.dump(MAP, MAP_FILE)
    MAP_FILE.close()
    MAP_FILE = open('MAP.pk', 'rb')
MAP = pk.load(MAP_FILE)
MAP_FILE.close()


try:
    MAP1_FILE = open('MAP1.pk','rb')
except:
    MAP1_FILE = open('MAP1.pk', 'wb')
    pk.dump(MAP1, MAP1_FILE)
    MAP1_FILE.close()
    MAP1_FILE = open('MAP1.pk', 'rb')
MAP1 = pk.load(MAP1_FILE)
MAP1_FILE.close()

#图图片回复 lp[random.randint(0, len(lp) - 1)])
@itchat.msg_register(['Picture', 'Recording', 'Attachment', 'Video'])
def download_files(msg):
    msg['Text']('./images/'+msg['FileName'])
    path = './images/' + msg['FileName']
    flag1=False
    for key in mappic.keys():
        p2 = './images/' + key
        print(dHash.hamming_distance(Image.open(path), Image.open(p2)))
        if dHash.hamming_distance(Image.open(path), Image.open(p2)) <=8:
            lp = mappic[key]
            flag1=True
            if type(lp) is str:
                itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', './images/'
                                        + mappic[key]), msg['FromUserName'])
            else:
                itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', './images/'
                                        + lp[random.randint(0, len(lp) - 1)]), msg['FromUserName'])
    flag2=False
    if flag1 is False:
        if len(LIST)==0 :
            LIST.append(msg['FileName'])
            print('这是list的第一个元素'+LIST[0])
            with open('PIC.pk','wb') as PIC_FILE:
                pk.dump(LIST,PIC_FILE)
                PIC_FILE.close()
        else:
            for i in range(0, len(LIST) - 1):
                p2 = './images/' + LIST[i]
                if dHash.hamming_distance(Image.open(path), Image.open(p2)) <= 8:
                    flag2=True
                    itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', './images/'
                                            + LIST[i+1]), msg['FromUserName'])
            if flag2 is False:
                LIST.append(msg['FileName'])
                print(LIST)
                with open('PIC.pk', 'wb') as PIC_FILE:
                    pk.dump(LIST, PIC_FILE)
                    PIC_FILE.close()
                itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', './images/'
                                        + LIST[len(LIST) - 1]), msg['FromUserName'])

try:
    PIC_FILE = open('PIC.pk', 'rb')
except:
    PIC_FILE = open('PIC.pk', 'wb')
    pk.dump(LIST, PIC_FILE)
    PIC_FILE.close()
    PIC_FILE = open('PIC.pk', 'rb')
LIST = pk.load(PIC_FILE)
PIC_FILE.close()
#好友关系检测
@itchat.msg_register(itchat.content.CARD)
def get_friend(msg):
    if msg['ToUserName'] != 'filehelper': return
    friendStatus = checkFriend.get_friend_status(msg['RecommendInfo'])
    itchat.send(friendStatus, 'filehelper')


#登录配置
itchat.auto_login(hotReload=True)
itchat.send(checkFriend.HELP_MSG, 'filehelper')
itchat.run()
