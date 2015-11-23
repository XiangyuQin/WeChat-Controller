#-*- coding:utf-8 -*- 
import urllib 
import urllib2 
import cookielib
import time 
import json
import traceback
import poster
from poster.encode import multipart_encode, MultipartParam

#cj=cookielib.LWPCookieJar() 
#opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) 
#urllib2.install_opener(opener) 
cookie = cookielib.MozillaCookieJar()
opener=poster.streaminghttp.register_openers()
opener.add_handler(urllib2.HTTPCookieProcessor(cookie))

paras={'username':'xjmjyqxy@sina.com','pwd':'b3ca2251f5f48978f9e9c32aeb5fde26','imgcode':'','f':'json'} 
req=urllib2.Request('https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN\\',urllib.urlencode(paras)) 
req.add_header('Accept','*/*') 
req.add_header('Accept-Encoding','gzip, deflate') 
req.add_header('Accept-Language','zh-CN,zh;q=0.8') 
req.add_header('Connection','keep-alive') 
req.add_header('Content-Length','81') 
req.add_header('Content-Type','application/x-www-form-urlencoded; charset=UTF-8')
req.add_header('Host','mp.weixin.qq.com') 
req.add_header('Origin','https://mp.weixin.qq.com') 
req.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN') 
req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36')  
req.add_header('X-Requested-With','XMLHttpRequest')
ret=urllib2.urlopen(req) 
retread=ret.read() 
print retread 
token=json.loads(retread) 
print token

tokenNum='2134338630'
ticket_id='AboutLoveCollege'
ticket='8f115c601d0e8ca2c56b55ad8a2d7528c3740125'
img='/home/pythonDir/imagestest3.jpg'
requestUrl='https://mp.weixin.qq.com/cgi-bin/filetransfer?action=upload_material&f=json&scene=1&groupid=1' \
            '&writetype=doublewrite&groupid=1&ticket_id={0}&ticket={1}&token={2}&lang=zh_CN'.format(
                ticket_id,
                ticket,
                tokenNum)
print requestUrl

params = {'file': open(img, "rb")}
data, headers = poster.encode.multipart_encode(params)
headers.update({
	'Accept': '*/*',
	'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
	'Connection': 'keep-alive',
	'Host': 'mp.weixin.qq.com',
	'Origin': 'https://mp.weixin.qq.com',
	'Referer': 'https://mp.weixin.qq.com/cgi-bin/filepage?type=2&begin=0&count=10&t=media/list&token=%s&lang=zh_CN' % tokenNum,
})
#req2.add_header('Accept','*/*') 
#req2.add_header('Accept-Encoding','gzip, deflate') 
#req2.add_header('Accept-Language','zh-CN,zh;q=0.8') 
#req2.add_header('Connection','keep-alive')  
#req2.add_header('Content-Type','multipart/form-data; boundary=----WebKitFormBoundarylQm5tNRV1bhEjDpb') 
#req2.add_header('Host','mp.weixin.qq.com') 
#req2.add_header('Origin','https://mp.weixin.qq.com') 
#req2.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/filepage?type=2&begin=0&count=12&t=media/img_list&group_id=1&token=2134338630&lang=zh_CN') 
#req2.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36')
method="POST"
sendTo='2817371308'

opener.addheaders = [
            ('Accept', 'application/json, text/javascript, */*; q=0.01'),
            ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'),
            ('Referer', 'https://mp.weixin.qq.com'), ('Cache-Control', 'max-age=0'),
            ('Connection', 'keep-alive'), ('Host', 'mp.weixin.qq.com'),
            ('Origin', 'https://mp.weixin.qq.com'), ('X-Requested-With', 'XMLHttpRequest'),
            ('User-Agent',
             'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36')]
opener.addheaders += [
            ('Referer',
             'https://mp.weixin.qq.com/cgi-bin/filepage?type=2&begin=0&count=12&t=media/img_list&group_id=1&token=2134338630&lang=zh_CN')]
for i in xrange(3):
	try:
		if method == "POST":
			print isinstance(data, dict)
			if(isinstance(data, dict)):
				data.update({'f': 'json',
					'lang': 'zh_CN',
					'ajax': 1,
					'token': tokenNum,
					'random': random.random()})
				if 't' not in data.keys():
					data.update({'t': 'ajax-response'})
					print "hello2"
				print "hello"
				resp = opener.open(requestUrl, urllib.urlencode(data))
			else:
				print 'test'
				req2 = urllib2.Request(requestUrl, data, headers)
				resp = urllib2.urlopen(req2)
		else:
			data.update({'token': tokenNum, 'f': 'json', 'lang': 'zh_CN'})
			resp = opener.open(requestUrl + "?" + urllib.urlencode(data))

		if resp.getcode() in [200, 302, 304]:
			msg = resp.read()
			print resp.getcode()
			print "hahahah:"+msg
			break
	except:
		print traceback.format_exc()
		time.sleep(1)
#不加cookie也可发送 
#req2.add_header('Cookie',cookie2) 
#ret2=urllib2.urlopen(req2) 
#ret2=opener.open(req2) 
#print 'x',ret2.read() 
