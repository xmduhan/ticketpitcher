# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 18:23:36 2015

@author: duhan
"""

#%%
from __future__ import division
from ticketpitcher import checkcode
from ticketpitcher.checkcode import *
from pandas import DataFrame



#%% 核对目录中的验证码识别率
import os
from os import listdir
from os.path import isfile,join,split
rootPath = r'D:\temp\code'
cnt = 0
succ = 0
for path in [x[0] for x in os.walk(rootPath)]:
    fileList = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) and f[-4:] == '.jpg'  ]
    for filename in fileList :
        fn = split(filename)[-1]
        cnt += 1        
        #print fn[:4], readCodeFromFile(filename)
        if fn[:4] == readCodeFromFile(filename):
            succ += 1
print u'识别率:%.2f%%' % (succ/cnt*100)

#%% 核对那些字母读取值是错误的
import os
from os import listdir
from os.path import isfile,join,split
rootPath = r'D:\temp\code'

result = []
for path in [x[0] for x in os.walk(rootPath)]:
    fileList = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) and f[-4:] == '.jpg'  ]
    for filename in fileList :
        # 读取文件名和验证码值        
        fn = split(filename)[-1]
        code = fn[:4]
        # 图片文件并切片
        image = Image.open(filename)
        cleanBackGround(image)
        imList = splitImage(image)
        for c,im in zip(code,imList) :
            try:
                cr = readCharFromImage(im)
            except:
                cr = ''
            if c == cr :
                result.append([c,1,1])
            else:
                result.append([c,1,0])
                        
df = DataFrame(result,columns=['ch','cnt','succ'])
df = df.groupby('ch').sum()
df['pct'] =  df.succ / df.cnt * 100
df = df[df.pct != 100]       
df
