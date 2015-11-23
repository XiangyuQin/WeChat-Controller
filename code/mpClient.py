#!/usr/bin/env python
# -*- coding:utf-8 -*-

__all__ = ['mpClient']

import cookielib
import urllib2
import urllib
import urlparse
import json
import poster
import hashlib
import time
import random
import sys
import os
import traceback
from cStringIO import StringIO
import tornado
import tornado.escape
import Image
from util import Base, Config
from bs4 import BeautifulSoup
import uuid


class mpClientException(Exception):
    pass


class mpClient(object):

    def __init__(self, user='tool', redisdb=None, force=False, config=None):
        """
        公众平台初始化
        """
        self.user = user
        self.key = "mp_%s" % user
        self.ticket = None
        self.ticket_id = None
        self.msgType = {'text': 1, 'image': 2, 'audio': 3, 'news': 10, 'video': 15}
        if not config:
            config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config/config.ini")
        self.readConfig(config)
        bs = Base(config)
        self.mail = bs.mail
        self.redisdb = redisdb or bs.redisdb()
        self.logger = bs.logger()
        self.login(force=force)

    def readConfig(self, config):
        conf = Config(config).options
        self.email = conf[self.user]['email']
        self.password = conf[self.user]['password']
        self.cookiefile = os.path.join(os.path.dirname(os.path.abspath(__file__)), conf[self.user]['cookie'])
        self.tokenfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), conf[self.user]['token'])

    def _setOpener(self):
        """
        设置请求头部信息模拟浏览器
        """
        self.opener = poster.streaminghttp.register_openers()
        self.opener.addheaders = [
            ('Accept', 'application/json, text/javascript, */*; q=0.01'),
            ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
            ('Referer', 'https://mp.weixin.qq.com'), ('Cache-Control', 'max-age=0'),
            ('Connection', 'keep-alive'), ('Host', 'mp.weixin.qq.com'),
            ('Origin', 'mp.weixin.qq.com'), ('X-Requested-With', 'XMLHttpRequest'),
            ('User-Agent',
             'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36')]

    def login(self, force=False):
        """
        登陆公众平台，失败将抛出异常，token是经常更换的，登录成功后要暂停一会，否则cookie会被清空
        """
        email = self.email
        password = self.password
        cookie = cookielib.MozillaCookieJar(self.cookiefile)
        self._setOpener()

        # if self.redisdb.hget(self.key, 'login') == '1':
        #    force = False

        if force or not os.path.exists(self.cookiefile) or not os.path.exists(self.tokenfile):
            self.opener.add_handler(urllib2.HTTPCookieProcessor(cookie))
            url = "https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN"

            m = hashlib.md5(password[0:16])
            m.digest()
            password = m.hexdigest()

            body = {'username': email, 'pwd': password, 'imgcode': '', 'f': 'json'}
            msg = json.loads(self.opener.open(url, urllib.urlencode(body), timeout=30).read())

            if 'base_resp' in msg and msg['base_resp']['ret'] == 0:
                self.token = msg['redirect_url'].split("=")[-1]
            else:
                self.logger.error("%s login error" % self.user + str(msg))
                self.mail("%s login error" % self.user, str(msg))
                raise mpClientException

            if not os.path.exists(self.tokenfile):
                os.system("mkdir -p %s" % os.path.dirname(self.tokenfile))
            open(self.tokenfile, "w").write(self.token)
            cookie.save(ignore_discard=True, ignore_expires=True)
            self.logger.info("login success,sleep 1s")

            self.redisdb.delete(self.key)
            self.redisdb.hset(self.key, 'login', 1)
            self.redisdb.expire(self.key, 3600)

            time.sleep(1)

            # 重启程序
            # os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            try:
                cookie.load(ignore_discard=True, ignore_expires=True)
                self.opener.add_handler(urllib2.HTTPCookieProcessor(cookie))
                self.token = open(self.tokenfile, "r").read().strip()
            except:
                self.login(force=True)

    @property
    def errCode(self):
        message = {
            # send
            10700: "不能发送，对方不是你的粉丝",
            10701: "该用户已被加入黑名单，无法向其发送消息",
            10703: "对方关闭了接收消息",
            10704: "该素材已被删除",
            10705: "该素材已被删除",
            10706: "由于该用户48小时未与你互动，你不能再主动发消息给他。直到用户下次主动发消息给你才可以对其进行回复",
            -8: "请输入验证码",

            # appmsg_edit
            64506: "保存失败,链接不合法",
            64507: "内容不能包含链接，请调整",
            64508: "查看原文链接可能具备安全风险，请检查",
            10801: "标题不能有违反公众平台协议、相关法律法规和政策的内容，请重新编辑",
            10802: "作者不能有违反公众平台协议、相关法律法规和政策的内容，请重新编辑",
            10803: "敏感链接，请重新添加",
            10804: "正文或摘要不能有违反公众平台协议、相关法律法规和政策的内容，请重新编辑",
            10806: "正文不能有违反公众平台协议、相关法律法规和政策的内容，请重新编辑",
            15801: "图文消息中含有诱导分享内容|为保证用户体验，微信公众平台禁止发布各种诱导分享行为。你所编辑的图文消息可能涉及诱导分享内容。",
            -20000: "登录态超时，请重新登录",
            -99: "内容超出字数，请调整",
        }
        for key in xrange(15802, 15807):
            message[key] = message[15801]
        return message

    def _sendRequest(self, url, data={}, headers={}, method="POST", jsonformat=True):
        """
        发送GET或POST请求，由于token经常更换，所以当出错时需要重新登录
        """
        from_function = sys._getframe().f_back.f_code.co_name
        msg = None
        for i in xrange(3):
            try:
                if method == "POST":
                    if(isinstance(data, dict)):
                        data.update({'f': 'json',
                                     'lang': 'zh_CN',
                                     'ajax': 1,
                                     'token': self.token,
                                     'random': random.random()})
                        if 't' not in data.keys():
                            data.update({'t': 'ajax-response'})
                        resp = self.opener.open(url, urllib.urlencode(data))
                    else:
                        req = urllib2.Request(url, data, headers)
                        resp = urllib2.urlopen(req)
                else:
                    data.update({'token': self.token, 'f': 'json', 'lang': 'zh_CN'})
                    resp = self.opener.open(url + "?" + urllib.urlencode(data))

                if resp.getcode() in [200, 302, 304]:
                    msg = resp.read()
                    self.logger.info(from_function + " success")
                    break
            except:
                self.logger.error(from_function + " failed, sleep 1s")
                self.logger.error(traceback.format_exc())
                time.sleep(1)

        if not msg:
            return False

        self.lastMsg = msg

        # 非json格式直接返回msg
        if jsonformat:
            msg = json.loads(msg)
        else:
            return msg

        # 结果是json格式，判断发送的结果，现在只有两种
        if 'base_resp' in msg:
            ret = int(msg['base_resp']['ret'])
        else:
            ret = int(msg['ret'])

        # 判断返回的结果
        if ret == 0:
            return msg
        else:
            time.sleep(1)
            if ret == -3:
                # token过期，重新登录
                self.logger.info("token expired, relogin")
                self.login(force=True)
                return self._sendRequest(url, data, headers, method, jsonformat)
            elif ret == -18:
                # ticket过期，重新获取
                self.getTicket(force=True)
                self.logger.info("ticket expired,reget")
                return self._sendRequest(url, data, headers, method, jsonformat)
            elif ret in self.errCode:
                self.lastMsg = self.errCode[ret]
                print self.lastMsg
                return False
            else:
                # 一些其他情况，比如删除已经删除了的图文或是群发超限等
                self.logger.error(from_function + " " + str(msg))
                return False

    def getTicket(self, force=False):
        """
        返回上传图片所需的ticket_id和ticket
        """
        if not force:
            ticket = self.redisdb.hget(self.key, 'ticket')
            ticket_id = self.redisdb.hget(self.key, 'ticket_id')
            if ticket and ticket_id:
                return ticket, ticket_id

        url = "https://mp.weixin.qq.com/cgi-bin/message"
        data = {
            't': 'message/list',
            'count': 20,
            'day': 0
        }
        ret = self._sendRequest(url, data, method="GET")
        if ret:
            ticket_id = ret['user_info']['user_name']
            ticket = ret['base_resp']['media_ticket']
            self.redisdb.hset(self.key, 'ticket', ticket)
            self.redisdb.hset(self.key, 'ticket_id', ticket_id)
            self.redisdb.expire(self.key, 3600)
            return ticket, ticket_id
        else:
            return None, None

    def uploadImg(self, img):
        """
        根据图片地址来上传图片，返回上传结果id
        """
        self.ensureLogin()
        ticket, ticket_id = self.getTicket()
        if not ticket:
            return False

        url = 'https://mp.weixin.qq.com/cgi-bin/filetransfer?action=upload_material&f=json' \
            '&writetype=doublewrite&groupid=1&ticket_id={0}&ticket={1}&token={2}&lang=zh_CN'.format(
                ticket_id,
                ticket,
                self.token)
        params = {'file': open(img, "rb")}
        data, headers = poster.encode.multipart_encode(params)
        headers.update({
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'mp.weixin.qq.com',
            'Origin': 'https://mp.weixin.qq.com',
            'Referer': 'https://mp.weixin.qq.com/cgi-bin/filepage?type=2&begin=0&count=10&t=media/list&token=%s&lang=zh_CN' % self.token,
            })
        ret = self._sendRequest(url, data, headers)
        if ret:
            return ret['content']
        else:
            print ret
            return False

    def delImg(self, file_id):
        """
        根据图片ID来删除图片
        """
        url = 'https://mp.weixin.qq.com/cgi-bin/modifyfile'
        data = {
            'fileid': file_id,
            'token': self.token,
            'oper': 'del'
            }
        ret = self._sendRequest(url, data)
        if ret:
            True
        else:
            print ret
            return False

    def uploadAppImg(self, img):
        """
        根据图片地址上传图片，专门用于图文中的图片，返回上传后的url，
        ensureLogin确保在线，已使url中的token是可用的
        """
        file_id = self.uploadImg(img)
        if file_id:
            items = self.getMsgIds(msgType='image', detail=True)
            for item in items:
                if str(item['file_id']) == str(file_id):
                    return items[0]['cdn_url']

        return False
        '''
        self.ensureLogin()
        url = 'https://mp.weixin.qq.com/cgi-bin/uploadimg2cdn?t=ajax-editor-upload-img&' \
            'lang=zh_CN&token=%s' % self.token
        files = {'upfile': open(img, "rb")}
        data, headers = poster.encode.multipart_encode(files)
        headers.update({
            'Accept': '*/*', 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6', 'Connection': 'keep-alive', 'Cache-Control': 'no-cache', 'Host': 'mp.weixin.qq.com',
             'Origin': 'https://mp.weixin.qq.com',
             'Referer': 'https://mp.weixin.qq.com/mpres/htmledition/ueditor/dialogs/image/image.html',
             })

        ret = self._sendRequest(url, data, headers, jsonformat=False)
        ret = json.loads(ret)
        print ret
        if ret['errcode'] == 0:
            return ret['url']

        # ret = requests.post(url,files=files,headers=headers,cookies=self.jar,verify=False)
        # if ret.json()['state'] == 'SUCCESS': return ret.json()['url']
        # else: return False
        '''

    def getMsgInfo(self, appMsg, index):
        """
        根据图文信息合成发送格式
        """
        soup = BeautifulSoup(appMsg.get('content', ''), 'html5lib')
        imgs = soup.find_all('img')
        for img in imgs:
            url = img.get('src', img.get('data-src'))
            if not url:
                continue
            if urlparse.urlparse(url).netloc == 'mmbiz.qlogo.cn':
                continue
            data = urllib2.urlopen(url).read()
            im = Image.open(StringIO(data))
            width = im.size[0]
            ratio = im.size[1]/float(width)
            filename = '/tmp/%s.%s' % (uuid.uuid4().hex, im.format.lower())
            with open(filename, 'wb') as fp:
                fp.write(data)
            src = self.uploadAppImg(filename)
            os.remove(filename)
            if src:
                img.attrs['src'] = src
                img.attrs['data-src'] = src
                img.attrs['data-ratio'] = ratio
                img.attrs['data-w'] = width
        appMsg['content'] = soup.body.renderContents()

        # 使用getAppMsg时，返回的参数中，fileid为file_id, sourceurl为source_url
        return {
            'title%d' % index:                      tornado.escape.xhtml_unescape(appMsg.get('title', '')),
            'content%d' % index:                    tornado.escape.xhtml_unescape(appMsg.get('content', '')),
            'digest%d' % index:                     tornado.escape.xhtml_unescape(appMsg.get('digest', '')),
            'author%d' % index:                     tornado.escape.xhtml_unescape(appMsg.get('author', '')),
            'fileid%d' % index:                     appMsg.get('file_id', appMsg.get('fileid', '')),
            'sourceurl%d' % index:                  appMsg.get('source_url', appMsg.get('sourceurl', '')),
            'show_cover_pic%d' % index:             appMsg.get('show_cover_pic', 0),
            'shortvideofileid%d' % index:           appMsg.get('shortvideofileid', ''),
            'copyright_type%d' % index:             appMsg.get('copyright_type', 0),
            'can_reward%d' % index:                 appMsg.get('can_reward', 0),
            'reward_wording%d' % index:             appMsg.get('reward_wording', ''),
            'releasefirst%d' % index:               appMsg.get('releasefirst', 0),
            'can_reward%d' % index:                 appMsg.get('can_reward', 0),
            'reward_wording%d' % index:             appMsg.get('reward_wording', ''),
            'reprint_permit_type%d' % index:        appMsg.get('reprint_permit_type', 0),
            'original_article_type%d' % index:      appMsg.get('original_article_type', ''),
            'need_open_comment%d' % index:          appMsg.get('need_open_comment', 1),
        }

    def packetMsg(self, appMsgs):
        """
        打包图文
        """
        ret = {}
        if isinstance(appMsgs, dict):
            appMsgs = [appMsgs]
        for index in xrange(len(appMsgs)):
            appMsg = appMsgs[index]
            if not appMsg.get('file_id', None):
                if not (appMsg.get('title') and appMsg.get('content') and appMsg.get('cover')):
                    self.logger.info("必须要有一张标题、内容和封面图片")
                    continue
                file_id = self.uploadImg(appMsg['cover'])
                appMsg['file_id'] = file_id

            ret.update(self.getMsgInfo(appMsg, index))
        return ret

    def getAppMsg(self, AppMsgId, isMul=0):
        """
        获取id为AppMsgId的图文信息
        isMul表示是否是多图文
        返回内容为appMsg类型的图文信息
        """
        url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        data = {
            'appmsgid': AppMsgId,
            'isMul': isMul,
            'type': 10,
            't': 'media/appmsg_edit',
            'action': 'edit'
            }
        ret = self._sendRequest(url, data, method="GET")
        if ret:
            app_msgs = json.loads(ret['app_msg_info'])['item'][0]['multi_item']
            return app_msgs

    def addAppMsg(self, appMsgs, AppMsgId=''):
        """
        如果AppMsgId为空，则是增加图文，不为空，则是预览后保存图文
        appMsgs里面包含如下内容:封面img(不可少),标题title,内容content,预览digest,
        是否显示封面图片show_cover,作者author,来源sourceurl,是一个list,成员为dict
        返回这个图文的id
        """
        url = 'https://mp.weixin.qq.com/cgi-bin/operate_appmsg'
        data = {
            'AppMsgId': AppMsgId,
            'count': len(appMsgs) if isinstance(appMsgs, list) else 1,
            'sub': 'update' if AppMsgId else 'create',
            'type': 10
            }
        data.update(self.packetMsg(appMsgs))
        ret = self._sendRequest(url, data)
        if ret:
            if AppMsgId:
                return AppMsgId
            else:
                msgIds = self.getMsgIds()
                if msgIds and len(msgIds):
                    return msgIds[0]
        return False

    def delAppMsg(self, AppMsgId):
        """
        根据id删除图文
        """
        url = 'https://mp.weixin.qq.com/cgi-bin/operate_appmsg'
        data = {
            'AppMsgId': AppMsgId,
            'sub': 'del'
            }
        ret = self._sendRequest(url, data)
        if ret:
            return True
        else:
            print ret
            return False

    def _sendMsg(self, sendTo, body):
        """
        基础发送信息的方法,可以发送图片，文字，图文等
        """
        if not body:
            return False
        if isinstance(sendTo, list):
            for _sendTo in sendTo:
                self._sendMsg(_sendTo, body)
            return True

        self.opener.addheaders += [
            ('Referer',
             'https://mp.weixin.qq.com/cgi-bin/singlesendpage?t=message/send&action=index&'
             'tofakeid=%s&token=%s&lang=zh_CN' % (sendTo, self.token))]
        url = "https://mp.weixin.qq.com/cgi-bin/singlesend"
        data = {'tofakeid': sendTo}
        data.update(body)
        ret = self._sendRequest(url, data)
        if ret:
            return True
        else:
            print ret
            return False

    def sendTextMsg(self, sendTo, content):
        """
        发送文字内容，成功返回True，使用时注意两次发送间隔，不能少于2s
        """
        ret = self._sendMsg(sendTo, {
            'type': 1,
            'content': content.strip()
        })
        return ret

    def sendImgMsg(self, sendTo, img):
        """
        发送图片信息，先上传图片
        """
        file_id = self.uploadImg(img)
        if not file_id:
            return False

        ret = self._sendMsg(sendTo, {
            'type': 2,
            'content': '',
            'fid': file_id,
            'fileid': file_id
        })
        return ret

    def send(self, sendTo, data):
        if isinstance(data, str) or isinstance(data, unicode):
            if os.path.exists(data):
                return self.sendImgMsg(sendTo, data)
            else:
                return self.sendTextMsg(sendTo, data)
        else:
            return self.sendAppMsg(sendTo, data)

    def getMedia(self, mediaId, path):
        url = "https://mp.weixin.qq.com/cgi-bin/downloadfile"
        data = {
            'msgid': mediaId
        }
        ret = self._sendRequest(url, data, method="GET", jsonformat=False)
        with open(path, 'wb') as fp:
            fp.write(ret)
        return True

    def getMsgIds(self, msgType='news', begin=0, count=None, detail=False):
        """
        获取素材ID，type为'news','image','audio','video'
        """
        if msgType == 'news':
            url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
            data = {'t': 'media/appmsg_list2',
                    'action': 'list_card',
                    'count': count or 10}
        elif msgType == 'video':
            url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
            data = {'t': 'media/appmsg_list',
                    'action': 'list',
                    'count': count or 9}
        elif msgType == 'image':
            url = "https://mp.weixin.qq.com/cgi-bin/filepage"
            data = {'1': 1,
                    't': 'media/img_list',
                    'count': count or 12}
        else:
            url = "https://mp.weixin.qq.com/cgi-bin/filepage"
            data = {'t': 'media/list',
                    'count': count or 21}

        data.update({
            'type': self.msgType[msgType],
            'begin': begin,
        })
        ret = self._sendRequest(url, data, method="GET")
        if ret:
            if msgType in ['news', 'video']:
                msgs = ret['app_msg_info']['item']
                ids = [item['app_id'] for item in msgs]
            else:
                msgs = ret['page_info']['file_item']
                ids = [item['file_id'] for item in msgs]
            if detail:
                return msgs
            else:
                return ids
        else:
            return False

    def sendAppMsgById(self, sendTo, AppMsgId):
        """
        通过图文ID发送图文
        """
        ret = self._sendMsg(sendTo, {
            'type': 10,
            'app_id': AppMsgId,
            'appmsgid': AppMsgId
            })
        return ret

    def sendAppMsg(self, sendTo, appMsgs, delete=True):
        """
        主动推送图文
        """
        AppMsgId = self.addAppMsg(appMsgs)
        if not AppMsgId:
            return False
        ret = self.sendAppMsgById(sendTo, AppMsgId)
        if delete:
            self.delAppMsg(AppMsgId)
        return ret

    def sendPreAppMsgById(self, preusername, AppMsgId, isMul=0):
        appMsgs = self.getAppMsg(AppMsgId, isMul)
        if not appMsgs:
            return False
        return self.sendPreAppMsg(preusername, appMsgs, AppMsgId=AppMsgId)

    def sendPreAppMsg(self, preusername, appMsgs, AppMsgId=None):
        """
        给微信号为preusername的粉丝发送图文消息。先保存，再发送预览
        """
        url = 'https://mp.weixin.qq.com/cgi-bin/operate_appmsg'
        data = {
            'AppMsgId': AppMsgId if AppMsgId else '',
            'count': len(appMsgs) if isinstance(appMsgs, list) else 1,
            'preusername': preusername,
            'vid': '',
            'imgcode': '',
            't': 'ajax-appmsg-preview',
            'sub': 'preview',
            'type': 10
            }
        data.update(self.packetMsg(appMsgs))
        ret = self._sendRequest(url, data)
        if ret and ret['appMsgId']:
            return ret['appMsgId']
        else:
            print ret
            return False

    def massSend(self, appmsgid, groupid=-1, sex=0):
        """
        群发图文,sex:0表示全部，1表示男，2表示女,groupid为-1表示发送给全部用户
        """
        url = "https://mp.weixin.qq.com/cgi-bin/masssend?t=ajax-response&token=%s&lang=zh_CN" % self.token
        data = {
            "type": 10,
            "appmsgid": appmsgid,
            "cardlimit": "1",
            "sex": sex,
            "groupid": groupid,
            "synctxweibo": "0",
            "enablecomment": "0",
            "country": "",
            "province": "",
            "city": "",
            "imgcode": "",
            #"operation_seq": "225548905",
        }
        self.opener.addheaders += [('Referer', 'https://mp.weixin.qq.com/cgi-bin/masssendpage?t=mass/send&token=%s&lang=zh_CN' % self.token)]
        ret = self._sendRequest(url, data)
        data = {
            "type": 10,
            "appmsgid": appmsgid,
            "cardlimit": "1",
            "sex": sex,
            "groupid": groupid,
            "synctxweibo": "0",
            "enablecomment": "0",
            "country": "",
            "province": "",
            "city": "",
            "imgcode": "",
            "direct_send": "1",
            "copy_msgid": appmsgid,
            "reprint_allow_list": "",
        }
        ret = self._sendRequest(url, data)
        if ret:
            return True
        else:
            return False

    def getUserInfo(self, fakeid):
        """
        根据fakeid获取用户信息,获取成功返回用户信息
        """
        url = 'https://mp.weixin.qq.com/cgi-bin/getcontactinfo'
        data = {
            't': 'ajax-getcontactinfo',
            'fakeid': fakeid
            }
        ret = self._sendRequest(url, data)
        if ret:
            return ret['contact_info']
        else:
            return False

    def getUserAvatar(self, fakeid, path):
        """
        获取用户头像并保存到path目录
        """
        url = "https://mp.weixin.qq.com/misc/getheadimg"
        data = {
            'fakeid': fakeid
            }
        ret = self._sendRequest(url, data, method="GET", jsonformat=False)
        if ret:
            try:
                Image.open(StringIO(ret))
                open(path, "w").write(ret)
                return True
            except:
                return False
        else:
            return False

    def changeUserGroup(self, fakeid, groupId):
        """
        根据fakeid给用户重新分组
        """
        url = 'https://mp.weixin.qq.com/cgi-bin/modifycontacts'
        data = {
            'contacttype': groupId,
            'tofakeidlist': fakeid,
            'action': 'modifycontacts',
            't': 'ajax-putinto-group'
            }
        ret = self._sendRequest(url, data)
        if ret:
            return True
        else:
            return False

    def getUserMsg(self, fakeid):
        """
        获取和用户的对话列表,用于获取用户的fakeid
        """
        url = "https://mp.weixin.qq.com/cgi-bin/singlesendpage"
        data = {
            't': 'message/send',
            'action': 'index',
            'tofakeid': fakeid
            }
        ret = self._sendRequest(url, data, method="GET")
        if ret:
            return ret['page_info']
        else:
            return []

    def getUserList(self, pagesize=10, groupid=0, pageidx=0):
        """
        获取用户列表,groupid表示分组，0：未分组，1：黑名单，2：星标组
        返回用户列表
        """
        url = "https://mp.weixin.qq.com/cgi-bin/contactmanage"
        data = {
            't': 'user/index',
            'pagesize': pagesize,
            'pageidx': pageidx,
            'type': 0,
            'groupid': groupid
            }

        ret = self._sendRequest(url, data, method="GET")
        if ret:
            return json.loads(ret['contact_list'])['contacts']
        else:
            return []

    def getMsgList(self, count=20, day=7, offset=0):
        """
        获取最新的消息
        """
        url = "https://mp.weixin.qq.com/cgi-bin/message"
        data = {
            't': 'message/list',
            'offset': offset,
            'count': count,
            'day': day
            }

        ret = self._sendRequest(url, data, method="GET")
        if ret:
            return json.loads(ret['msg_items'])['msg_item']
        else:
            return []

    def getInfo(self):
        url = "https://mp.weixin.qq.com/cgi-bin/home"
        data = {
            't': 'home/index'
            }
        ret = self._sendRequest(url, data, method="GET")
        if ret:
            return ret['home_info']
        else:
            return None

    def getFakeId(self, code, new_user=True):
        """
        获取openId对应的fakeid，向未获取到的用户(在未分组里)发送消息后立即调用这个函数
        """
        fakeids = set()
        if new_user:
            newUsers = self.getUserList(pagesize=10, groupid=0)
            for item in newUsers:
                fakeids.add(item['id'])
        else:
            msg = self.getMsgList(count=20, day=7)
            for item in msg:
                fakeids.add(item['fakeid'])

        for fakeid in fakeids:
            self.logger.info('%s' % fakeid)
            msg = self.getUserMsg(fakeid)
            if not msg:
                continue
            toNickName = msg['to_nick_name']
            msgList = msg['msg_items']['msg_item']
            for message in msgList:
                if message['nick_name'] != toNickName and message.get('content', '').find(code) >= 0:
                    return fakeid

    def ensureLogin(self):
        if not self.redisdb.exists(self.key):
            self.checkNotice()

    def checkNotice(self):
        """
        获取系统通知
        """
        url = "https://mp.weixin.qq.com/cgi-bin/sysnotify"
        data = {
            'count': 5,
            'begin': 0,
            'ajax': 1,
            'random': random.random()
            }

        ret = self._sendRequest(url, data, method="GET")
        return ret


if __name__ == "__main__":
    client = mpClient(user='movie')
    msg = client.checkNotice()
    if msg['Count'] > 0:
        for item in msg['List']:
            for key in item:
                print key, item[key]
    #items = client.getMsgIds(msgType='image', detail=True)
    # for item in items:
    #    print item['file_id'], item['cdn_url']
