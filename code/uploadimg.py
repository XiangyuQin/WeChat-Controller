#-*- coding:utf-8 -*- 
import urllib 
import urllib2 
import cookielib 
import json 

cj=cookielib.LWPCookieJar() 
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) 
urllib2.install_opener(opener) 

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


requestUrl='https://mp.weixin.qq.com/cgi-bin/filetransfer?action=upload_material&f=json&token=1999601929&lang=zh_CN\\'
tokenNum='1999601929'
app_id='400443549'
appmsgid='400443549'
parasUpload={'action':'upload_material',
'f':'json',
'scene':'1',
'writetype':'doublewrite',
'groupid':'1',
'ticket_id':'AboutLoveCollege',
'ticket':'549f9f8a053ee892afc16afe863b07bf023a0a41',
'token':'1999601929',
'lang':'zh_CN'}
req2=urllib2.Request(requestUrl,urllib.urlencode(parasUpload)) 
req2.add_header('Accept','*/*') 
req2.add_header('Accept-Encoding','gzip, deflate') 
req2.add_header('Accept-Language','zh-CN,zh;q=0.8') 
req2.add_header('Connection','keep-alive')  
req2.add_header('Content-Type','multipart/form-data; boundary=----WebKitFormBoundarylQm5tNRV1bhEjDpb') 
req2.add_header('Host','mp.weixin.qq.com') 
req2.add_header('Origin','https://mp.weixin.qq.com') 
req2.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/filepage?type=2&begin=0&count=12&t=media/img_list&group_id=1&token=1999601929&lang=zh_CN') 
req2.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36') 
#不加cookie也可发送 
#req2.add_header('Cookie',cookie2) 
ret2=urllib2.urlopen(req2) 
#ret2=opener.open(req2) 
print 'x',ret2.read() 
