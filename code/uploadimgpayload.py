#-*- coding:utf-8 -*- 
import urllib 
import urllib2 
import cookielib
import time 
import json
import traceback
import poster
from poster.encode import multipart_encode, MultipartParam

cj=cookielib.LWPCookieJar() 
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) 
urllib2.install_opener(opener) 

paras={'username':'xjmjyqxy@sina.com','pwd':'b3ca2251f5f48978f9e9c32aeb5fde26','imgcode':'','f':'json'} 
req1=urllib2.Request('https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN\\',urllib.urlencode(paras)) 
req1.add_header('Accept','*/*') 
req1.add_header('Accept-Encoding','gzip, deflate') 
req1.add_header('Accept-Language','zh-CN,zh;q=0.8') 
req1.add_header('Connection','keep-alive') 
req1.add_header('Content-Length','81') 
req1.add_header('Content-Type','application/x-www-form-urlencoded; charset=UTF-8')
req1.add_header('Host','mp.weixin.qq.com') 
req1.add_header('Origin','https://mp.weixin.qq.com') 
req1.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN') 
req1.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36')  
req1.add_header('X-Requested-With','XMLHttpRequest')
ret=urllib2.urlopen(req1) 
retread=ret.read() 
print retread 
token=json.loads(retread) 
print token

tokenNum='2134338630'
ticket_id='AboutLoveCollege'
ticket='3e7154c5d869211a97c1dc605bcc437aaf2a2742'
img=r'/home/pythonDir/test2.jpg'
requestUrl='https://mp.weixin.qq.com/cgi-bin/filetransfer?action=upload_material' \
			'&f=json&scene=1&writetype=doublewrite&groupid=1&ticket_id=AboutLoveCollege&ticket=3e7154c5d869211a97c1dc605bcc437aaf2a2742&svr_time=1448268300&token=2134338630&lang=zh_CN'

#buld post body data
boundary = '------WebKitFormBoundarysaBYvQAFs3QrkSu2'
print '%s' %(boundary)
data = []
data.append('%s' % boundary)

data.append('Content-Disposition: form-data; name="%s"\r\n' % 'id')
data.append('WU_FILE_0')
data.append('%s' % boundary)

data.append('Content-Disposition: form-data; name="%s"\r\n' % 'name')
data.append('test2.jpg')
data.append('%s' % boundary)

data.append('Content-Disposition: form-data; name="%s"\r\n' % 'type')
data.append('image/jpeg')
data.append('%s' % boundary)

data.append('Content-Disposition: form-data; name="%s"\r\n' % 'lastModifiedDate')
data.append('Mon Nov 23 2015 15:18:47 GMT+0800')
data.append('%s' % boundary)

data.append('Content-Disposition: form-data; name="%s"\r\n' % 'size')
data.append('199415')
data.append('%s' % boundary)

fr=open(img,'rb')
data.append('Content-Disposition: form-data; name="%s"; filename="test2.jpg"' % 'file')
data.append('Content-Type: %s\r\n' % 'image/jpeg')
data.append(fr.read())
fr.close()
data.append('--%s--\r\n' % boundary)
http_body='\r\n'.join(data)
print type(http_body)

try:
	req=urllib2.Request(requestUrl, data=http_body)
	req.add_header('Accept','*/*')
	req.add_header('Accept-Encoding','gzip, deflate')
	req.add_header('Accept-Language','zh-CN,zh;q=0.8')
	req.add_header('Connection','keep-alive')
	req.add_header('Content-Type','multipart/form-data; boundary=----WebKitFormBoundarylQm5tNRV1bhEjDpb')
	req.add_header('Host','mp.weixin.qq.com')
	req.add_header('Origin','https://mp.weixin.qq.com')
	req.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/filepage?type=2&begin=0&count=12&t=media/img_list&group_id=1&token=2134338630&lang=zh_CN')
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36')
    #post data to server
	resp = urllib2.urlopen(req, timeout=5)
    #get response
	qrcont=resp.read()
	print qrcont
except Exception,e:
	print e