# -*- coding: utf-8 -*-
"""
Created on Fri Nov 14 21:54:18 2014

@author: duhan
"""

#%%
from ticketpitcher import pitcher
from BeautifulSoup import BeautifulSoup

#%% --------------------------- 获取剩余票数 ---------------------------
pitcher.login('xmjf001','123456')
#%%
ticketInfo = pitcher.getTicketInfo('2014-11-29')
ticketInfo

#%%
ticketInfo[ticketInfo[u'余票'].apply(lambda x:int(x))>0]

#%% --------------------------- 订票 ---------------------------

pitcher.login('xmjf001','123456')

#%%
pitcher.orderTicket(6762,1)

