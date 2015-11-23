
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
tokenNum='2134338630'
app_id='400443549'
appmsgid='400443549'
paras2={'type':'10','error':'false','imgcode':'','tofakeid':'2817371308','token':tokenNum,'ajax':'1','app_id':app_id,'appmsgid':appmsgid}
req2=urllib2.Request('https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&f=json&token=2134338630&lang=zh_CN\\',urllib.urlencode(paras2)) 
req2.add_header('Accept','application/json, text/javascript, */*; q=0.01') 
req2.add_header('Accept-Encoding','gzip, deflate') 
req2.add_header('Accept-Language','zh-CN,zh;q=0.8') 
req2.add_header('Connection','keep-alive')  
req2.add_header('Content-Type','application/x-www-form-urlencoded; charset=UTF-8') 
req2.add_header('Host','mp.weixin.qq.com') 
req2.add_header('Origin','https://mp.weixin.qq.com') 
req2.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/singlesendpage?t=message/send&action=index&tofakeid=2817371308&token=%s&lang=zh_CN'%tokenNum) 
req2.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36') 
req2.add_header('X-Requested-With','XMLHttpRequest') 
#不加cookie也可发送 
#req2.add_header('Cookie',cookie2) 
ret2=urllib2.urlopen(req2) 
#ret2=opener.open(req2) 
print 'x',ret2.read() 
