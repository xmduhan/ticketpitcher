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
from config import tempPath
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
reserveUrl = 'http://e.gly.cn/guide/guideReserve.do?dailyFlightId=%s'


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
            else:
                record.append(dict(td.input.attrs)['onclick'].replace(')','').split(',')[-1])
        records.append(record)    
    return records


def isLogin():
    '''
    检查当前是否已经登录系统
    '''    
    #  读取首页信息
    request = urllib2.Request(homeUrl)
    response = urllib2.urlopen(request)
    content = response.read()
    soup = BeautifulSoup(content)
    pim_font = soup.find(attrs={'class': 'pim_font'})
    if pim_font == None:
        return False
    if pim_font.h3.string.split(u'，')[1] == u'欢迎您！':
        return True
    else:
        return False

    

def login(username,password):
    '''
    登录
    username 登录系统的用户名
    password 用户密码
    '''
    loginData = {
        'loginTarget':'targetGuide',
        'username': username,
        'j_username':'GUIDE_' + username,
        'j_password':password,
        'guiderand':'****'
    }
    loginData['guiderand'] = readCode()
    postData = urllib.urlencode(loginData)
    request = urllib2.Request(loginUrl, postData)
    response = urllib2.urlopen(request)
    content = response.read()
    return isLogin()
        


def printTicketInfo(ticketInfo):
    '''
    打印船票信息
    ticketInfo 船票信息的list
    '''
    for record in ticketInfo:
        for rd in record:
            print rd,
        print 


def readFormItemValue(form,name):
    '''
    从订票表单页面中读取数据
    form 订票表单(BeautifulSoup)
    name 要读取的信息项名称(input的name属性)
    
    '''
    try:
        result = dict(form.find(attrs={'name':name}).attrs)[u'value']
    except:
        result = None
    return result


# 表单信息项
formItemNameList=[
'ticketName_1','ticketId_1','price_1','count_1','childCount_1','totalAmt_1',
'ticketName_2','ticketId_2','price_2','count_2','childCount_2','totalAmt_2',
'ticketName_3','ticketId_3','price_3','count_3','childCount_3','totalAmt_3',
'ticketCounts','childCounts','ticketAmts','randCode',
'dailyFlightId','ticketCount','ticketMessage'
]

def getTicketMessage(formData):
    '''
    生成表单的ticketMessage项
    formData 表单数据
    猜测ticketMessage是一个表单的验证项，其生成的javascript代码为:
    var ticketMessage = ""
    for ( var i = 1; i <= ticketCounts; i++) {
        if (parseInt($("#count_" + i).val()) > 0) {
            ticketMessage += $("#ticketId_" + i).val();
            ticketMessage += ";";
            ticketMessage += $("#count_" + i).val();
            ticketMessage += ";";
            ticketMessage += $("#childCount_" + i).val();
            ticketMessage += "=";
        }
    }
    此过程实际将该代码翻译成python
    
    '''    
    ticketMessage = ''
    for i in range(1,int(formData['ticketCounts'])+1):
        if int(formData["count_" + str(i)]) > 0  :
            ticketMessage += formData["ticketId_" + str(i)]
            ticketMessage += ";"
            ticketMessage += formData["count_" + str(i)]
            ticketMessage += ";"
            ticketMessage += formData["childCount_" + str(i)]
            ticketMessage += "="
    return ticketMessage


def orderTicket(dailyFlightId,n):
    '''
    根据航班号标识预定船票
    dailyFlightId  航班的标识
    n  要预订票的数量(整型)
    返回True成功,False失败
    '''
    # 请求表单页面    
    url = reserveUrl % dailyFlightId
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read()
    # 读取表单对象
    soup = BeautifulSoup(content) 
    form = soup.find(attrs={'id':'confirmPassenger'})
    if not form:
        return False    
    # 读取各表单项的值
    formData = {}
    for itemName in formItemNameList:
        formData[itemName] = readFormItemValue(form,itemName)
    
    # 设置表单的信息
    formData['count_1'] = str(n)
    formData['ticketCounts'] = str(n)
    formData['ticketMessage'] = getTicketMessage(formData)
    formData['randCode'] = readCode() 
    return formData

#%%
'''
http://e.gly.cn/guide/guideReserve.do?dailyFlightId=5579

ticketName_1=团体票50
ticketId_1=3B00ED413ED344179A441269CCA55FFC
price_1=50.0
count_1=1
childCount_1=0
totalAmt_1=50

ticketName_2=儿童半价票25
ticketId_2=BED62B5557BF4229854F0571C3E8B519
price_2=25.0
count_2=0
childCount_2=0
totalAmt_2=0

ticketName_3=残军半价票25
ticketId_3=232BEEFA2BEC40FFB3C2378D13BBFD8F
price_3=25.0
count_3=0
childCount_3=0
totalAmt_3=0

ticketCounts=1
childCounts=0
ticketAmts=50
randCode=8C4K

dailyFlightId=5579
ticketCount=3
ticketMessage=3B00ED413ED344179A441269CCA55FFC%3B1%3B0%3D


'''