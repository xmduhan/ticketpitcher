# -*- coding: utf-8 -*-
"""
Created on Fri Nov 14 21:54:18 2014

@author: duhan
"""

#%%
from ticketpitcher import pitcher

#%% --------------------------- 登录 ---------------------------
pitcher.login('xmjf001', '123456')

#%% ------------------------ 获取余票 --------------------------
ticketInfo = pitcher.getTicketInfo('2014-12-31')
c1 = ticketInfo[u'出发码头'] == u'邮轮中心厦鼓码头'
c2 = ticketInfo[u'抵达码头'] == u'三丘田码头'
c3 = ticketInfo[u'余票'].apply(lambda x: int(x)) > 0
ticketInfo[c1 & c2 & c3]

#%% ------------------------ 订票 -----------------------------
pitcher.orderTicket('11051', 1)


#%% -------------------- 获取预订信息 --------------------------
reserveInfo = pitcher.getReserveInfo()
reserveInfo

#%% ---------------------- 取消预订 --------------------------
pitcher.cancelReserve(40925)

#%% -------------- 通过预订信息获取航班信息 -------------------
i = 0
beginDay = reserveInfo.irow(i)[u'开航日期']
beginTime = reserveInfo.irow(i)[u'开航时间']
departure = reserveInfo.irow(i)[u'出发码头']
arrival = reserveInfo.irow(i)[u'抵达码头']
pitcher.getDailyFlightId(beginDay, beginTime, departure, arrival)


#%% ---------------------- 更新预订信息L --------------------------
pitcher.refreshReserve(40872)


