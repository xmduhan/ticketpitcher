# -*- coding: utf-8 -*-
"""
Created on Fri Nov 14 21:54:18 2014

@author: duhan
"""

#%%
from ticketpitcher import pitcher
#from BeautifulSoup import BeautifulSoup


#%% --------------------------- 获取剩余票数 ---------------------------
pitcher.login('xmjf001','123456')
#%%
ticketInfo = pitcher.getTicketInfo('2014-12-09')
ticketInfo

#%%
ticketInfo[ticketInfo[u'余票'].apply(lambda x:int(x))>0]

#%% --------------------------- 订票 ---------------------------

pitcher.login('xmjf001','123456')

#%%
pitcher.orderTicket(6762,1)


#%%
from pandas import DataFrame
records = []
header = [u'序号',u'出发码头',u'抵达码头',u'航班号',u'开航时间',u'票价',u'余票',u'航班ID'] 
df = DataFrame(records,columns=header)
