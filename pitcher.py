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
from BeautifulSoup import BeautifulSoup, NavigableString
from pandas import DataFrame
import re
from datetime import datetime
from dateutil import parser
import uuid

import warnings
warnings.simplefilter('ignore', FutureWarning)

#%% 初始化全局变量
imageFile = tempPath + str(uuid.uuid1()) + '.jpg'
#htmlFile = r'd:\pydev\ticketpitcher\tmp.html'

# 初始化域名
#domain = 'http://e.gly.cn'
domain = 'http://e.xmferry.com'

# 读取验证码
codeUrl = domain + '/checkCode/generateCode.do'
# 首页
homeUrl = domain + '/guide/guideIndex.do'
# 登录
loginUrl = domain + '/j_spring_security_check'
# 查询余票
queryUrl = domain + '/guide/guideQuery.do'
# 订票界面
reserveUrl = domain + '/guide/guideReserve.do?dailyFlightId=%s'
# 订票提交
submitUrl = domain + '/guide/submitGuideReserve.do'
# 获取已订的票的信息
queryReserveUrl = domain + '/guide/queryGuideReserve.do'
# 取消预定
cancelReserveUrl = domain + '/guide/saveCancelGuideReserve.do?reverseId=%s'
# 订单信息
orderUrl = domain + '/guide/guideSelect.do'
# 验证码检查url
checkCodeUrl = domain + '/guide/checkCode.do?randCheckCode=%s'

#%% 增加cookie支持
ckjar = cookielib.CookieJar()
ckproc = urllib2.HTTPCookieProcessor(ckjar)
opener = urllib2.build_opener(ckproc)
urllib2.install_opener(opener)


#%%
def readCode():
    '''
    从url中读取验证码图片存盘到文件，并调用验证码解析过程获取验证码
    '''
    request = urllib2.Request(codeUrl)
    response = urllib2.urlopen(request)
    f = open(imageFile, 'wb')
    f.write(response.read())
    f.close()
    # print imageFile
    result = readCodeFromFile(imageFile)
    # print 'code:', result
    return result


def isRightCode(code):
    """
    检查验证码是否正确
    """
    request = urllib2.Request(checkCodeUrl % code)
    response = urllib2.urlopen(request)
    result = response.read()
    print result
    if result == '1':
        return True
    else:
        return False


def getTicketInfo(day):
    '''
    按日期获取所有的船票信息
    day 输入的日期，格式为:yyyy-mm-dd
    '''
    # 提交请求并获取返回结果
    queryData = {
        #'flightLineName':'邮轮中心厦鼓码头-三丘田码头',
        'flightDate': day
    }
    postData = urllib.urlencode(queryData)
    request = urllib2.Request(queryUrl, postData)
    response = urllib2.urlopen(request)
    content = response.read()

    #localName = "d:/temp.html"
    #tmpfile=open(localName,'wb')
    #tmpfile.write(content)
    #tmpfile.close()

    # 解析返回结果到list形式
    soup = BeautifulSoup(content)
    table = soup.findAll(attrs={"class": "passenger_class"})
    #print 'table=',table
    if table:
        records = []
        for tr in table:
            record = []
            for td in tr.findAll('td'):
                if type(td.string) == NavigableString:
                    record.append(td.string.strip())
                else:
                    record.append(dict(td.input.attrs)['onclick'].replace(')', '').split(',')[-1])
            records.append(record)
    else:
        records = None
    # 将返回结果转化为pandas的DataFrame
    header = [u'序号', u'出发码头', u'抵达码头', u'航班号', u'开航时间', u'票价', u'余票', u'航班ID']
    df = DataFrame(records, columns=header)
    return df


def getReserveInfo():
    '''
    获取当前用户订到的票的信息
    返回已定票的信息pandas DataFrame格式
    '''
    request = urllib2.Request(queryReserveUrl)
    response = urllib2.urlopen(request)
    content = response.read()
    soup = BeautifulSoup(content)
    table = soup.findAll(attrs={"class": "passenger_class"})
    #print 'table=',table
    if table:
        records = []
        for tr in table:
            record = []
            for td in tr.findAll('td'):
                if type(td.string) == NavigableString:
                    record.append(td.string.strip())
                else:
                    match = re.search(r'\(\d+\)', dict(td.input.attrs)['onclick'])
                    if match:
                        record.append(match.group()[1:-1])
                    else:
                        record.append('')
            records.append(record)
    else:
        records = None
    # 将返回结果转化为pandas的DataFrame
    # header = [u'航线', u'航班时间', u'人数', u'携带儿童', u'金额', u'定金金额', u'预约时间', u'最后确认时间', u'状态', u'预订ID']
    header = [u'航线', u'航班时间', u'人数', u'金额', u'定金金额', u'预约时间', u'最后确认时间', u'状态', u'预订ID']
    df = DataFrame(records, columns=header)
    # 根据已订票的信息计算出航班的关键信息
    df[u'开航日期'] = df[u'航班时间'].apply(lambda x: datetime.strftime(parser.parse(x), "%Y-%m-%d"))
    df[u'开航时间'] = df[u'航班时间'].apply(lambda x: datetime.strftime(parser.parse(x), "%H:%M"))
    df[u'出发码头'] = df[u'航线'].apply(lambda x: x.split('-')[0])
    df[u'抵达码头'] = df[u'航线'].apply(lambda x: x.split('-')[1])
    return df


def getOrderInfo(beginDay,endDay):
    '''
    获得当前用户名下的订单信息
    beginDay  起始日期(yyyy-mm-dd)
    endDay    结束日期(yyyy-mm-dd)
    返回所有订单信息pandas DataFrame格式
    '''

    def _sendRequest(page):
        '''
        指定页数返回对应的网页内容
        '''
        queryData = {
            'dateType': '1',
            'bDate': beginDay,
            'eDate':	endDay,
            'state':	'0',
            'name' : '',
            'orderId' : '',
            'idNumber' : '',
            'page' : unicode(page),
            'dateType1' : '1',
            'state1' : '0',
            'bDate1' : beginDay,
            'eDate1' : endDay,
            'orderId1' : '',
            'idNumber1' : '',
            'name1' : ''
        }
        postData = urllib.urlencode(queryData)
        request = urllib2.Request(orderUrl, postData)
        response = urllib2.urlopen(request)
        content = response.read()
        return content

    # 定义订单信息项解析逻辑
    sw = {
        0:lambda x : x.string.split(':')[1],
        1:lambda x : x.string.split(':')[1].strip().split('.')[0],
        2:lambda x : ':'.join(x.string.split(':')[1:]).strip(),
        3:lambda x : x.string.split(':')[1].strip(),
        4:lambda x : x.string.split(':')[1].strip(),
        5:lambda x : x.string.split(':')[1].strip(),
        6:lambda x : x.string.split(':')[1].strip(),
        7:lambda x : x.string.split(':')[1].strip(),
        8:lambda x :':'.join(x.string.split(':')[1:]).strip().replace('  ',' ')
    }

    records = []
    page = 1
    orderList = True   # 使程序能够进入循环
    while orderList:
        content = _sendRequest(page)
        soup = BeautifulSoup(content)
        orderList = soup.findAll(attrs={"class": "jdan_tfont"})
        orderDetailList = soup.findAll(attrs={"class": "table_clist"})
        # 将本页的数据转化为记录
        for i,order in enumerate(orderList):
            # 读取订单基本信息
            orderInfo = order.findAll('li')
            getInfo=lambda x : sw[x](orderInfo[x])
            #record = [getInfo(coln) for coln in range(len(orderInfo))]
            record = [getInfo(coln) for coln in range(len(sw))]
            # 读取订单的状态和导游信息
            orderDetail = orderDetailList[i]
            orderDetailInfo = orderDetail.findAll('td')
            record.append(orderDetailInfo[0].string.split('&')[0].strip())
            record.append(orderDetailInfo[2].string.strip())
            # 完成1条新记录的添加
            records.append(record)
        page += 1

    # 数据转化为DataFrame格式
    header = [u'订单号', u'金额', u'订单时间', u'人数', u'携带儿童', u'发票', u'航线', u'航班号',u'启航时间',u'导游',u'订单状态']
    df = DataFrame(records if records else None, columns=header)
    return df


def getDailyFlightId(beginDay, beginTime, departure, arrival):
    '''
    根据航班信息获取航班ID
    beginDay  开航日期，格式:"%Y-%m-%d"
    beginTime 开航时间，格式:"%H:%M"
    departure 出发码头
    arrival 抵达码头
    成功返回航班的id，失败返回None
    '''
    ticketInfo = getTicketInfo(beginDay)
    c1 = ticketInfo[u'出发码头'] == departure
    c2 = ticketInfo[u'抵达码头'] == arrival
    c3 = ticketInfo[u'开航时间'] == beginTime
    data = ticketInfo[c1 & c2 & c3]
    if len(data) == 1:
        # return int(data[u'航班ID'].irow(0))
        return data[u'航班ID'].irow(0)[1:-1]
    else:
        return None


def cancelReserve(reverseId):
    '''
    提交的原始http协议格式
    reverseId   要取消的预订记录的ID
    POST /guide/saveCancelGuideReserve.do?reverseId=40931 HTTP/1.1
    randCode=ti0y&dailyFlightId=%24%7BdailyFlight.id%7D
    randCode=ti0y&dailyFlightId=${dailyFlight.id}
    '''
    url = cancelReserveUrl % (str(reverseId))

    # 提交请求并获取返回结果
    data = {
        'randCode': readCode(),  # 验证码,
        'dailyFlightId': '${dailyFlight.id}'
    }
    postData = urllib.urlencode(data)
    request = urllib2.Request(url, postData)
    response = urllib2.urlopen(request)
    content = response.read()
    # 检查取消是否成功
    soup = BeautifulSoup(content)
    try:
        if soup.strong.getText().split('&')[0] == u'取消预约成功！':
            return True
        else:
            return False
    except:
        return False


def refreshReserve(reverseId, reserveInfo=None):
    '''
    通过取消预订，再重新预订的方法刷新预订的最后确认时间
    reverseId   要刷新的预订记录的ID
    reserveInfo 当前用户的预订信息（通过调用getReserveInfo获得），如果为空将重新请求
    '''
    if reserveInfo == None:
        reserveInfo = getReserveInfo()

    # 读取当前预订数据
    c1 = reserveInfo[u'预订ID'] == str(reverseId)
    data = reserveInfo[c1]
    if len(data) != 1:
        return False

    # 通过预订数据获取航班ID
    beginDay = data.irow(0)[u'开航日期']
    beginTime = data.irow(0)[u'开航时间']
    departure = data.irow(0)[u'出发码头']
    arrival = data.irow(0)[u'抵达码头']
    dailyFlightId = getDailyFlightId(beginDay, beginTime, departure, arrival)


    # 取消预订
    if cancelReserve(reverseId) == False:
        return False

    # 重新预订
    cnt = int(data.irow(0)[u'人数'])
    if orderTicket(dailyFlightId, cnt) == False:
        return False

    return True


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


def login(username, password):
    '''
    登录
    username 登录系统的用户名
    password 用户密码
    '''
    loginData = {
        'loginTarget': 'targetGuide',
        'username': username,
        'j_username': 'GUIDE_' + username,
        'j_password': password,
        # 'guiderand': '****'
        'rand': '****'
    }
    code = readCode()
    # print 'code:', code
    loginData['rand'] = code
    postData = urllib.urlencode(loginData)
    request = urllib2.Request(loginUrl, postData)
    response = urllib2.urlopen(request)
    #content = response.read()
    response.read()
    return isLogin()


#def printTicketInfo(ticketInfo):
#    '''
#    打印船票信息
#    ticketInfo 船票信息的list
#    '''
#    for record in ticketInfo:
#        for rd in record:
#            print rd,
#        print


def readFormItemValue(form, name):
    '''
    从订票表单页面中读取数据
    form 订票表单(BeautifulSoup)
    name 要读取的信息项名称(input的name属性)

    '''
    try:
        result = dict(form.find(attrs={'name': name}).attrs)[u'value']
    except:
        result = None
    return result


# 表单信息项
formItemNameList = [
    'ticketName_1', 'ticketId_1', 'price_1', 'count_1', 'childCount_1', 'totalAmt_1',
    'ticketName_2', 'ticketId_2', 'price_2', 'count_2', 'childCount_2', 'totalAmt_2',
    'ticketName_3', 'ticketId_3', 'price_3', 'count_3', 'childCount_3', 'totalAmt_3',
    'ticketCounts', 'childCounts', 'ticketAmts', 'randCode','token',
    'dailyFlightId', 'ticketCount', 'ticketMessage'
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
    # print formData
    # 注意!!!!!!!
    # ticketCounts变量名出现重名
    # ticketCounts 这似乎不是总票数，是票项数 团队票35 儿童半价票18 残军半价票18  共3类票项
    ticketMessage = ''
    #for i in range(1,int(formData['ticketCounts'])+1):
    for i in range(1, 3 + 1):
        if int(formData["count_" + str(i)]) > 0:
            ticketMessage += formData["ticketId_" + str(i)]
            ticketMessage += ";"
            ticketMessage += formData["count_" + str(i)]
            # ticketMessage += ";"
            # ticketMessage += formData["childCount_" + str(i)]
            ticketMessage += "="
    return ticketMessage


def orderTicket(dailyFlightId, n):
    '''
    根据航班号标识预定船票
    dailyFlightId  航班的标识
    n  要预订票的数量(整型)
    返回True成功,False失败

    提交链接地址
    http://e.gly.cn/guide/submitGuideReserve.do
    提交表单的格式范例:
    ticketName_1=团体票50
    ticketId_1=3B00ED413ED344179A441269CCA55FFC
    price_1=50.0
    count_1=1
    childCount_1=0
    totalAmt_1=50
    -------------
    ticketName_2=儿童半价票25
    ticketId_2=BED62B5557BF4229854F0571C3E8B519
    price_2=25.0
    count_2=0
    childCount_2=0
    totalAmt_2=0
    ------------
    ticketName_3=残军半价票25
    ticketId_3=232BEEFA2BEC40FFB3C2378D13BBFD8F
    price_3=25.0
    count_3=0
    childCount_3=0
    totalAmt_3=0
    -------------
    ticketCounts=1
    childCounts=0
    ticketAmts=50
    randCode=8C4K
    -------------
    token=CC9028BE733A403E9F59F69B1B7408DB  # 2015-09-17增加
    dailyFlightId=5579
    ticketCount=3
    ticketMessage=3B00ED413ED344179A441269CCA55FFC%3B1%3B0%3D

    '''
    # 请求表单页面
    url = reserveUrl % dailyFlightId
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read()
    # 读取表单对象
    soup = BeautifulSoup(content)
    form = soup.find(attrs={'id': 'confirmPassenger'})
    if not form:
        return False
        # 读取各表单项的值
    formData = {}
    for itemName in formItemNameList:
        formData[itemName] = readFormItemValue(form, itemName)

    # 确定验证码正确再提交, 减少失败风险
    for _ in range(5):
        code = readCode()   # 验证码
        if isRightCode(code):
            break
    else:
        return False

    # 设置表单的信息
    formData['count_1'] = str(n)  # 票数
    formData['totalAmt_1'] = str(float(formData['price_1']) * n)  # 票价
    formData['ticketCounts'] = str(n)  # 总票数
    formData['ticketAmts'] = formData['totalAmt_1']  # 总票价
    formData['ticketMessage'] = getTicketMessage(formData)  # 校验信息
    formData['randCode'] = code

    # 将表单格式转化为utf-8格式
    strFormData = {}
    for key, value in formData.iteritems():
        strFormData[key] = unicode(value).encode('utf-8')


    # 提交预定请求
    postData = urllib.urlencode(strFormData)
    request = urllib2.Request(submitUrl, postData)
    response = urllib2.urlopen(request)
    content = response.read()

    # 判断预定的结果
    soup = BeautifulSoup(content)
    try:
        #if soup.strong.div.getText().split('&')[0] == u'预订成功!':
        if 'reserveId' in str(soup.form):
            return True
        else:
            return False
    except:
        return False

