# -*- coding: utf-8 -*-
"""
Created on Fri Nov 14 21:54:18 2014

@author: duhan
"""

#%%
from ticketpitcher import pitcher
from BeautifulSoup import BeautifulSoup

#%% 登录
pitcher.login('xmjf001','123456')
#%%
ticketInfo = pitcher.getTicketInfo('2014-11-29')
pitcher.printTicketInfo(ticketInfo)




#%% ----------------------------------------

pitcher.login('xmjf001','123456')

#%%
content = pitcher.orderTicket(5579,1)

#%%
soup = BeautifulSoup(content) 
form = soup.find(attrs={'id':'confirmPassenger'})
dict(form.find(attrs={'name':'ticketName_1'}).attrs)[u'value']



#%% ----------------------------------------

pitcher.login('xmjf001','123456')

#%%
pitcher.orderTicket(5579,1)




