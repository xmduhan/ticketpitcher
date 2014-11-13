# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 20:03:21 2014

@author: duhan
"""
#%%
import cookielib, urllib2, urllib;
from PIL import Image
from ticketpitcher.checkcode import readCodeFromFile

#%% 初始化全局变量
imageFile = r'd:\pydev\ticketpitcher\generateCode.jpg'
htmlFile = r'd:\pydev\ticketpitcher\tmp.html'
codeUrl = 'http://e.gly.cn/checkCode/generateCode.do'
homeUrl = 'http://e.gly.cn/guide/guideIndex.do'
loginUrl = 'http://e.gly.cn/j_spring_security_check'
queryUrl = 'http://e.gly.cn/guide/guideQuery.do'
username = 'xmjf001'
password = '123456'

loginData = {
    'loginTarget':'targetGuide',
    'username': username,
    'j_username':'GUIDE_' + username,
    'j_password':'123456',
    'guiderand':'****'
}

#%% 增加cookie支持
ckjar = cookielib.CookieJar();
ckproc = urllib2.HTTPCookieProcessor(ckjar);
opener = urllib2.build_opener(ckproc);
urllib2.install_opener(opener);


#%%
def readCode():
    '''
    从url中读取验证码图片存盘到文件，并调用验证码解析过程获取验证码
    '''
    request=urllib2.Request(codeUrl)
    response=urllib2.urlopen(request)
    f=open(imageFile,'wb')
    f.write(response.read())
    f.close()
    return readCodeFromFile(imageFile)        


#%% 登录
loginData['guiderand'] = readCode()
postData = urllib.urlencode(loginData)
request = urllib2.Request(loginUrl, postData)
response = urllib2.urlopen(request)
content = response.read()
        
#%% 读取首页信息
request = urllib2.Request(homeUrl)      
response=urllib2.urlopen(request)  
content = response.read()
       

#%%
queryData={
    'flightLineName':'邮轮中心厦鼓码头-三丘田码头',
    'flightDate':'2014-11-14'
}
postData = urllib.urlencode(queryData)
request = urllib2.Request(queryUrl, postData)
response = urllib2.urlopen(request)
content = response.read()

#%%
f=open(htmlFile,'wb') 
f.write(content)
f.close()

