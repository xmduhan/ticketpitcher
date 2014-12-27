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
ticketInfo = pitcher.getTicketInfo('2014-12-14')
ticketInfo

#%%
c1 = ticketInfo[u'出发码头'] == u'邮轮中心厦鼓码头'
c2 = ticketInfo[u'抵达码头'] == u'三丘田码头'
c3 = ticketInfo[u'余票'].apply(lambda x:int(x))>0
#%%
ticketInfo[ c1 & c2 & c3 ]
#%%
ticketInfo[ c1 & c2 ]
#%% --------------------------- 订票 ---------------------------

pitcher.login('xmjf001','123456')

#%%
pitcher.orderTicket(6762,1)
#%%
pitcher.orderTicket(8129,1)


