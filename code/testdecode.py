# -*- coding:utf-8 -*-
#!/usr/bin/env python

__all__ = ['weChatController']

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
from bs4 import BeautifulSoup
import uuid

#cookie = cookielib.MozillaCookieJar()
#_opener=poster.streaminghttp.register_openers()
#_openerreload(sys)
reload(sys)
sys.setdefaultencoding( "utf-8" )
class WeChatControllerException(Exception):
    pass


class WeChatController(object):

    def __init__(self, user='tool', redisdb=None, force=False, config=None):
        """
        公众平台初始化
        """  
        self.test_appmsg = {
            'author':'test',
            'title':'test_merge2',
            'sourceurl':'www.baidu.com',
            'cover':'/home/pythonDir/cover.jpg',
            'digest':"你好",
            'content':'<p style="line-height: 25.6px; white-space: normal;"><em><span style="word-wrap: break-word; font-weight: 700;">表白，'\
			'相信这个动作是每个人一生当中都会触发的一个行为，' \
			'大部分人认为表白是跟女孩确定恋爱关系非常有效的一种方法，有耐心和妹子建立深层次的联系感并对妹子产生了吸引力，妹子接 ' \
			'受的概念就会大增其实，盲目的表白你会发现往往到最后没有任何效果。</span></em></p><p style="line-height: 25.6px; white-spac' \
			'e: normal;"><span style="line-height: 1.6;">   有个朋友，做个一个实验，并把它录制成了一个视频剪辑，内容大概是这样的，他收集' \
			'了现实生活中将近50个男人的表白现场实录，有的是在人民广场这样人流量聚焦的地区，有的像电影里那样是在很有格调的西餐厅，有的是在酒吧，有的是在朋 ' \
			'友聚会，更有夸张一点的，你们可能都想不到，是在足球比赛的现场。</span></p><p style="line-height: 25.6px; white-space: normal;">最后的结果出来了，成功率几乎 '\
			'只有5%不到，对的，你没看错，就是这么低。很多兄弟觉得不可思议，怎么会这样，和电视电影里的完全不一样啊，呵呵，因为这才是现实。为什么女人的反应都几乎是拒绝，完全不顾及' \
			'男人的面子，也完全没有被感动的赶脚。</p><p style="line-height: 25.6px; white-space: normal;">那么我来告诉兄弟们，问题出在哪，因为这种情况下，女人会本能的产生一种压迫' \
			'感，或者说是不安全感，她们会条件反射式的去拒绝。</p><p style="line-height: 25.6px; white-space: normal;">因为在进化学来看，远古时代的人类基因，仍然在现代人的基因里有' \
			'保留，在古代的女人，她们一旦选定一个男人，她的生命就跟这个男人绑定在了一起，换句话说，如果这个男人不能提供足够的食物，这个女人在怀孕期间就会被饿死。</p><p style="lin' \
			'e-height: 25.6px; white-space: normal;">这种选错了对象就要付出生命代价的基因一直延续至今，所以，女人一旦面对男人表白这种事情的时候，就会自动切换到理性思考模式，接受面临的是风险，而拒绝是最' \
			'保险的做法，女人不傻，所以，她们会选择拒绝就不难理解了。<span style="line-height: 1.6;">现在兄弟们懂了这个道理，那有的兄弟要说了，既然这样，不去表白，怎么追到女人' \
			'，难道让女人对你表白么？恩，让女人表白也不是不可能的，我们家的方法就可以让你做到，让女人倒追你，我们有的是方法。</span></p><p style="line-height: 25.6px; white-s' \
			'pace: normal;">这就是我们家自主开发的男神模式，它可以让你和女人的互动交流之后，让女人喜欢上你，让女人主动对你示好，对你表白。至于该怎么做，只需要关注我们' \
			'的微信公众号，那里面有干货会告诉你。</p><p><br/></p>',
        }
        self.lastMsg = None
        self._opener = None
        self.user = user
        self.key = "mp_%s" % user
        self.ticket = None
        self.ticket_id = None
        self.token = None
        self.email = "xjmjyqxy@sina.com"
        self.password = "b3ca2251f5f48978f9e9c32aeb5fde26"
        self.msgType = {'text': 1, 'image': 2, 'audio': 3, 'news': 10, 'video': 15}
        self.login(force=force)
        #print self.upload_img(img_url='/home/pythonDir/imagestest3.jpg')
        self.add_appmsg(self.test_appmsg)
        

    def _set_opener(self):
        self._opener = poster.streaminghttp.register_openers()
        self._opener.addheaders = [
            ('Accept', 'application/json, text/javascript, */*; q=0.01'),
            ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
            ('Referer', 'https://mp.weixin.qq.com'), 
            ('Cache-Control', 'max-age=0'),
            ('Connection', 'keep-alive'), 
            ('Host', 'mp.weixin.qq.com'),
            ('Origin', 'https://mp.weixin.qq.com'), 
            ('X-Requested-With', 'XMLHttpRequest'),
            ('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36')
            ]
    
    def login(self, force=False):
        """
        登陆公众平台，失败将抛出异常，token是经常更换的，登录成功后要暂停一会，否则cookie会被清空
        """
        email = self.email
        password = self.password
        cookie = cookielib.MozillaCookieJar()
        self._set_opener()

        if force:
            self._opener.add_handler(urllib2.HTTPCookieProcessor(cookie))
            url = "https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN"
            
            body = {'username': email, 'pwd': password, 'imgcode': '', 'f': 'json'}
            req = self._opener.open(url, urllib.urlencode(body), timeout=30)
            resp = req.read()
            msg = json.loads(resp)
            print msg
            if 'base_resp' in msg and msg['base_resp']['ret'] == 0:
                self.token = msg['redirect_url'].split("=")[-1]
                print "token:%s" %self.token
            else:
                print 'login fail'
            time.sleep(1)
        else:
            try:
                print "force:%s" %force
            except:
                self.login(force=True)

    def _ensure_login(self):
        if not self.token==None:
            self.check_notice()

    def check_notice(self):
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

        ret = self._send_request(url, data, method="GET")
        return ret

    def _get_ticket(self):
        url = "https://mp.weixin.qq.com/cgi-bin/message"
        data = {
            't': 'message/list',
            'count': 20,
            'day': 0
            }
        ret = self._send_request(url, data, method="GET")
        if ret:
            ticket_id = ret['user_info']['user_name']
            ticket = ret['base_resp']['media_ticket']
            print ticket
            print ticket_id
            return ticket, ticket_id
        else:
            return None, None


    def _send_request(self, url, data={}, headers={}, method='POST', jsonformat=True):
        for i in xrange(3):
            try:
                if method == "POST":
                    print isinstance(data, dict)
                    if(isinstance(data, dict)):
                        data.update({'f': 'json',
                            'lang': 'zh_CN',
                            'ajax': 1,
                            'token': self.token,
                            'random': random.random()})
                        if 't' not in data.keys():
                            data.update({'t': 'ajax-response'})
                        resp = self._opener.open(url, urllib.urlencode(data))
                    else:
                        req = urllib2.Request(url, data, headers)
                        resp = urllib2.urlopen(req)
                else:
                    data.update({'token': self.token, 'f': 'json', 'lang': 'zh_CN'})
                    resp = self._opener.open(url + "?" + urllib.urlencode(data))

                if resp.getcode() in [200, 302, 304]:
                    msg = resp.read()
                    break
            except:
                print traceback.format_exc()
                time.sleep(1)
				
        if not msg:
            return False

        self.lastMsg = msg

        # 非json格式直接返回msg
        print 'msg', msg, type(msg)
        if jsonformat:
            try:
                msg = json.loads(msg)
            except:
                import chardet
                msg = json.loads( msg.decode( chardet.detect(msg)['encoding'] ) )
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
                print "token expired, relogin"
                self.login(force=True)
                return self._send_request(url, data, headers, method, jsonformat)
            elif ret == -18:
                # ticket过期，重新获取
                self.getTicket(force=True)
                print "ticket expired,reget"
                return self._send_request(url, data, headers, method, jsonformat)
            else:
                #error
                print str(msg)
                return False

    def upload_img(self, img_url=""):
        self._ensure_login()
        ticket, ticket_id = self._get_ticket()
        if not ticket:
            return False

        url = 'https://mp.weixin.qq.com/cgi-bin/filetransfer?action=upload_material&f=json' \
            '&writetype=doublewrite&groupid=1&ticket_id={0}&ticket={1}&token={2}&lang=zh_CN'.format(
                ticket_id,
                ticket,
                self.token)
        params = {'file': open(img_url, "rb")}
        data, headers = poster.encode.multipart_encode(params)
        headers.update({
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'mp.weixin.qq.com',
            'Origin': 'https://mp.weixin.qq.com',
            'Referer': 'https://mp.weixin.qq.com/cgi-bin/filepage?type=2&begin=0&count=10&t=media/list&token=%s&lang=zh_CN' % self.token,
            })
        ret = self._send_request(url, data, headers)
        if ret:
            return ret['content']
        else:
            print ret
            return False

    def merge_appmsg_info(self, appMsg, index):
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
		
    def packet_appmsg(self, appMsgs):
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
                file_id = self.upload_img(appMsg['cover'])
                appMsg['file_id'] = file_id
            ret.update(self.merge_appmsg_info(appMsg, index))
        return ret

    def get_appmsg(self, AppMsgId, isMul=0):
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
        ret = self._send_request(url, data, method="GET")
        if ret:
            app_msgs = json.loads(ret['app_msg_info'])['item'][0]['multi_item']
            return app_msgs

    def add_appmsg(self, appMsgs, AppMsgId=''):
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
        data.update(self.packet_appmsg(appMsgs))
        ret = self._send_request(url, data)
        if ret:
            if AppMsgId:
                return AppMsgId
            else:
                msgIds = self.get_msg_Ids()
                if msgIds and len(msgIds):
                    return msgIds[0]
        return False

    def del_appmsg(self, AppMsgId):
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

    def send_appmsg_by_id(self, sendTo, AppMsgId):
        """
        通过图文ID发送图文
        """
        ret = self._sendMsg(sendTo, {
            'type': 10,
            'app_id': AppMsgId,
            'appmsgid': AppMsgId
            })
        return ret

    def send_app_msg(self, sendTo, appMsgs, delete=True):
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


    def get_msg_Ids(self, msgType='news', begin=0, count=None, detail=False):
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
        ret = self._send_request(url, data, method="GET")
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

if __name__ == "__main__":
    client = WeChatController(user='weChatController',force=True)
    msg = client.check_notice()
    print msg
