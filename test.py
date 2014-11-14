# -*- coding: utf-8 -*-
"""
Created on Fri Nov 14 21:54:18 2014

@author: duhan
"""

#%%
from ticketpitcher import pitcher


#%% 登录
pitcher.login()

#%%
ticketInfo = pitcher.getTicketInfo('2014-11-29')
pitcher.printTicketInfo(ticketInfo)

#%%


