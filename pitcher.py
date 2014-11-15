# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 20:03:21 2014

@author: duhan
"""
#%%
import cookielib, urllib2, urllib
from PIL import Image
#from ticketpitcher.checkcode import readCodeFromFile
from checkcode import readCodeFromFile
from config import username,password,tempPath
from BeautifulSoup import BeautifulSoup,NavigableString
import string
from pandas import DataFrame

#%% 初始化全局变量
imageFile = tempPath + 'generateCode.jpg'
#htmlFile = r'd:\pydev\ticketpitcher\tmp.html'
codeUrl = 'http://e.gly.cn/checkCode/generateCode.do'
homeUrl = 'http://e.gly.cn/guide/guideIndex.do'
loginUrl = 'http://e.gly.cn/j_spring_security_check'
queryUrl = 'http://e.gly.cn/guide/guideQuery.do'


loginData = {
    'loginTarget':'targetGuide',
    'username': username,
    'j_username':'GUIDE_' + username,
    'j_password':password,
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


def getTicketInfo(day):
    '''    
    按日期获取所有的船票信息
    day 输入的日期，格式为:yyyy-mm-dd
    '''
    queryData={
        #'flightLineName':'邮轮中心厦鼓码头-三丘田码头',
        'flightDate':day
    }
    postData = urllib.urlencode(queryData)
    request = urllib2.Request(queryUrl, postData)
    response = urllib2.urlopen(request)
    content = response.read()    
    #header = ['序号','出发码头','抵达码头','航班号','开航时间','票价','余票']   
    soup = BeautifulSoup(content) 
    records = []
    for tr in soup.findAll(attrs={"class": "passenger_class"}):
        record = []
        for td in tr.findAll('td'):
            if type(td.string) == NavigableString:
                record.append(td.string.strip())
        records.append(record)    
    return records

def login():
    '''
    登录
    '''
    loginData['guiderand'] = readCode()
    postData = urllib.urlencode(loginData)
    request = urllib2.Request(loginUrl, postData)
    response = urllib2.urlopen(request)
    content = response.read()
        

def printTicketInfo(ticketInfo):
    '''
    打印船票信息
    ticketInfo 船票信息的list
    '''
    for record in ticketInfo:
        for rd in record:
            print rd,
        print 
