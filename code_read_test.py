# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 10:16:11 2015

@author: duhan
"""

#%%
from ticketpitcher import checkcode
from ticketpitcher.checkcode import *

#%% 读取位图文件，并清除背景
#filepath = r'D:\temp\d8da559e-b0c9-11e4-8838-3c970e8f6420.jpg'
filepath = r'D:\temp\code\EG9M.jpg'
image = Image.open(filepath)
cleanBackGround(image)
plt.imshow(image)


#%% 切出第n个字符的小图
sl = splitImage(image)[3]
plt.imshow(sl)

#%% 尝试解析字符从小图
checkcode.imageArrayMap = readImageArrayMap(arrayMapPath)
readCharFromImage(sl)

#%% 读取位图到数组，供编辑使用
array = imageToArray(sl)

#%%
path = r'C:\Python27\Lib\site-packages\ticketpitcher\data\2'
os.chdir(path)
pickle.dump( array, open( "M.pk", "wb" ) )

#%%
imageArrayMap = readImageArrayMap(r'C:\Python27\Lib\site-packages\ticketpitcher\data')



#%%

import os
from os import listdir
from os.path import isfile,join,split
rootPath = r'C:\Python27\Lib\site-packages\ticketpitcher\data'
fileList = []
for path in [x[0] for x in os.walk(rootPath)]:
    files = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) and f[-3:] == '.pk' and len(f) ==4 ]
    fileList.extend(files)

fileList    

  
   
#%%
filepath = r'D:\temp\code\52A8.jpg'
readCodeFromFile(filepath)


