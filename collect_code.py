#!/usr/bin/env python
# encoding: utf-8

"""
收集验证码数据
用spyder打开
"""

#%%
import urllib2
import pickle
from PIL import Image
from ticketpitcher.checkcode import splitImage
from ticketpitcher.checkcode import imageToArray
from ticketpitcher.checkcode import printArrayAsImage
from ticketpitcher.checkcode import readCodeFromImage


#%% 读取验证码
codeUrl = 'http://e.xmferry.com/checkCode/generateCode.do'
imageFile = '/tmp/1.jpg'
request = urllib2.Request(codeUrl)
response = urllib2.urlopen(request)
f = open(imageFile, 'wb')
f.write(response.read())
f.close()
# print imageFile
image = Image.open(imageFile)
# print 'code:', result
image


#%%
code = readCodeFromImage(image)
print code


#%% 读取字符
sl = splitImage(image)
im = sl[3]
a = imageToArray(im)
im


#%% 编辑
printArrayAsImage(a)



#%% 保存
fn = '/usr/local/lib/python2.7/dist-packages/ticketpitcher/data/4/' + 'P.pk'
pickle.dump(a, open(fn, "wb"))
