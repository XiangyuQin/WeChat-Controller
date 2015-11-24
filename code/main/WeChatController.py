#!/usr/bin/env python
# -*- coding:utf-8 -*-

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
        ����ƽ̨��ʼ��
        """
        self.test_appmsg = {
            'author':'test',
            'title':'test_merge',
            'sourceurl':'www.baidu.com',
            'cover':'/home/pythonDir/cover.jpg',
            'content':'<p style="line-height: 25.6px; white-space: normal;"><em><span style="word-wrap: break-word; font-weight: 700;">��ף�'\
			'�������������ÿ����һ�����ж��ᴥ����һ����Ϊ��' \
			'�󲿷�����Ϊ����Ǹ�Ů��ȷ��������ϵ�ǳ���Ч��һ�ַ����������ĺ����ӽ������ε���ϵ�в������Ӳ����������������ӽ� ' \
			'�ܵĸ���ͻ������ʵ��äĿ�ı����ᷢ�����������û���κ�Ч����</span></em></p><p style="line-height: 25.6px; white-spac' \
			'e: normal;"><span style="line-height: 1.6;">   �и����ѣ�����һ��ʵ�飬������¼�Ƴ���һ����Ƶ���������ݴ���������ģ����ռ�' \
			'����ʵ�����н���50�����˵ı���ֳ�ʵ¼���е���������㳡�����������۽��ĵ������е����Ӱ���������ں��и�������������е����ھưɣ��е������� ' \
			'�Ѿۻᣬ���п���һ��ģ����ǿ��ܶ��벻������������������ֳ���</span></p><p style="line-height: 25.6px; white-space: normal;">���Ľ�������ˣ��ɹ��ʼ��� '\
			'ֻ��5%�������Եģ���û����������ô�͡��ܶ��ֵܾ��ò���˼�飬��ô���������͵��ӵ�Ӱ�����ȫ��һ�������Ǻǣ���Ϊ�������ʵ��ΪʲôŮ�˵ķ�Ӧ�������Ǿܾ�����ȫ���˼�' \
			'���˵����ӣ�Ҳ��ȫû�б��ж��ĸϽš�</p><p style="line-height: 25.6px; white-space: normal;">��ô���������ֵ��ǣ���������ģ���Ϊ��������£�Ů�˻᱾�ܵĲ���һ��ѹ��' \
			'�У�����˵�ǲ���ȫ�У����ǻ���������ʽ��ȥ�ܾ���</p><p style="line-height: 25.6px; white-space: normal;">��Ϊ�ڽ���ѧ������Զ��ʱ�������������Ȼ���ִ��˵Ļ�������' \
			'�������ڹŴ���Ů�ˣ�����һ��ѡ��һ�����ˣ����������͸�������˰�����һ�𣬻��仰˵�����������˲����ṩ�㹻��ʳ����Ů���ڻ����ڼ�ͻᱻ������</p><p style="lin' \
			'e-height: 25.6px; white-space: normal;">����ѡ���˶����Ҫ�����������۵Ļ���һֱ�����������ԣ�Ů��һ��������˱�����������ʱ�򣬾ͻ��Զ��л�������˼��ģʽ���������ٵ��Ƿ��գ����ܾ�����' \
			'���յ�������Ů�˲�ɵ�����ԣ����ǻ�ѡ��ܾ��Ͳ�������ˡ�<span style="line-height: 1.6;">�����ֵ��Ƕ�������������е��ֵ�Ҫ˵�ˣ���Ȼ��������ȥ��ף���ô׷��Ů��' \
			'���ѵ���Ů�˶�����ô��������Ů�˱��Ҳ���ǲ����ܵģ����Ǽҵķ����Ϳ���������������Ů�˵�׷�㣬�����е��Ƿ�����</span></p><p style="line-height: 25.6px; white-s' \
			'pace: normal;">��������Ǽ���������������ģʽ�������������Ů�˵Ļ�������֮����Ů��ϲ�����㣬��Ů����������ʾ�ã������ס����ڸ���ô����ֻ��Ҫ��ע����' \
			'��΢�Ź��ںţ��������иɻ�������㡣</p><p><br/></p>',
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
        ��½����ƽ̨��ʧ�ܽ��׳��쳣��token�Ǿ��������ģ���¼�ɹ���Ҫ��ͣһ�ᣬ����cookie�ᱻ���
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
        ��ȡϵͳ֪ͨ
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

        # ��json��ʽֱ�ӷ���msg
        if jsonformat:
            msg = json.loads(msg)
        else:
            return msg

        # �����json��ʽ���жϷ��͵Ľ��������ֻ������
        if 'base_resp' in msg:
            ret = int(msg['base_resp']['ret'])
        else:
            ret = int(msg['ret'])

        # �жϷ��صĽ��
        if ret == 0:
            return msg
        else:
            time.sleep(1)
            if ret == -3:
                # token���ڣ����µ�¼
                print "token expired, relogin"
                self.login(force=True)
                return self._send_request(url, data, headers, method, jsonformat)
            elif ret == -18:
                # ticket���ڣ����»�ȡ
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
        ����ͼ����Ϣ�ϳɷ��͸�ʽ
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

        # ʹ��getAppMsgʱ�����صĲ����У�fileidΪfile_id, sourceurlΪsource_url
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
        ���ͼ��
        """
        ret = {}
        if isinstance(appMsgs, dict):
            appMsgs = [appMsgs]
        for index in xrange(len(appMsgs)):
            appMsg = appMsgs[index]
            if not appMsg.get('file_id', None):
                if not (appMsg.get('title') and appMsg.get('content') and appMsg.get('cover')):
                    self.logger.info("����Ҫ��һ�ű��⡢���ݺͷ���ͼƬ")
                    continue
                file_id = self.upload_img(appMsg['cover'])
                appMsg['file_id'] = file_id
            ret.update(self.merge_appmsg_info(appMsg, index))
        return ret

    def get_appmsg(self, AppMsgId, isMul=0):
        """
        ��ȡidΪAppMsgId��ͼ����Ϣ
        isMul��ʾ�Ƿ��Ƕ�ͼ��
        ��������ΪappMsg���͵�ͼ����Ϣ
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
        ���AppMsgIdΪ�գ���������ͼ�ģ���Ϊ�գ�����Ԥ���󱣴�ͼ��
        appMsgs���������������:����img(������),����title,����content,Ԥ��digest,
        �Ƿ���ʾ����ͼƬshow_cover,����author,��Դsourceurl,��һ��list,��ԱΪdict
        �������ͼ�ĵ�id
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
                msgIds = self.getMsgIds()
                if msgIds and len(msgIds):
                    return msgIds[0]
        return False

    def del_appmsg(self, AppMsgId):
        """
        ����idɾ��ͼ��
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
        ͨ��ͼ��ID����ͼ��
        """
        ret = self._sendMsg(sendTo, {
            'type': 10,
            'app_id': AppMsgId,
            'appmsgid': AppMsgId
            })
        return ret

    def send_app_msg(self, sendTo, appMsgs, delete=True):
        """
        ��������ͼ��
        """
        AppMsgId = self.addAppMsg(appMsgs)
        if not AppMsgId:
            return False
        ret = self.sendAppMsgById(sendTo, AppMsgId)
        if delete:
            self.delAppMsg(AppMsgId)
        return ret


    def getMsgIds(self, msgType='news', begin=0, count=None, detail=False):
        """
        ��ȡ�ز�ID��typeΪ'news','image','audio','video'
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