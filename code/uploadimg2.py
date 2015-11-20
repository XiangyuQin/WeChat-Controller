#-*- coding:utf-8 -*- 
import urllib 
import urllib2 
import cookielib 
import json 
#buld post body data
        boundary = '----------%s' % hex(int(time.time() * 1000))
		print boundary
        data = []
        data.append('--%s' % boundary)
        
        data.append('Content-Disposition: form-data; name=%s\r\n' % 'id')
        data.append('WU_FILE_0')
        data.append('--%s' % boundary)
        
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'name')
        data.append('test_img_upload.jpg')
        data.append('--%s' % boundary)
        
        fr=open(r'D:\WeChatControler\WeChat-Controller\test_img_upload.jpg','rb')
        data.append('Content-Disposition: form-data; name="%s"; filename="test_img_upload.jpg"' % 'profile')
        data.append('Content-Type: %s\r\n' % 'image/jpeg')
        data.append(fr.read())
        fr.close()
        data.append('--%s--\r\n' % boundary)
    
        http_url='http://remotserver.com/page.php'
        http_body='\r\n'.join(data)
        try:
            #buld http request
            req=urllib2.Request(http_url, data=http_body)
            #header
            req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
            req.add_header('User-Agent','Mozilla/5.0')
            req.add_header('Referer','http://remotserver.com/')
            #post data to server
            resp = urllib2.urlopen(req, timeout=5)
            #get response
            qrcont=resp.read()
            print qrcont
            
            
        except Exception,e:
            print 'http error'