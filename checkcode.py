# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 22:19:38 2014

@author: duhan
"""

#%%
# 导入相关模块
from __future__ import division
import numpy as np
#import matplotlib.pyplot as plt
#import pytesseract
from PIL import Image
from sklearn.cluster import KMeans
import pandas as pd
from copy import copy
#from matplotlib.colors import ColorConverter
import string
import os
import sys
import pickle
from config import arrayMapPath, tempPath
from os import listdir
from os.path import isfile, join, split

# 设置当前目录
#os.chdir(r"d:\pydev\ticketpitcher")
#srcImageFile = 'generateCode.jpg'
#tmpImageFile = 'tmp_image.jpg'
#tmpTextFile = 'tmp_text'

#%% 定义处理过程
def imageToDataFrame(image):
    '''
    将一个Image的像素数据转化为对应的数据集形式
    iamge 需要转化的Image对象
    '''
    #print image.size[0],image.size[1]
    pixels = image.load()
    data = []
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            rec = (x, y) + copy(pixels[x, y])
            data.append(rec)
    df = pd.DataFrame(data)
    df.columns = ('x', 'y', 'r', 'g', 'b')
    return df


def cleanBackGround(image, bgColor=(255, 255, 255)):
    '''
    将图片背景涂成统一的颜色
    image   要处理的Image对象
    bgColor 背景要涂成的颜色
    '''
    # 读取像素数据转化为数据集格式
    pixels = image.load()
    df = imageToDataFrame(image)

    # 将所有像素数据分成2类(前景/背景)
    estimator = KMeans(init='k-means++', n_clusters=2)
    estimator.fit(df[['r', 'g', 'b']])
    df['label'] = estimator.predict(df[['r', 'g', 'b']])

    # 通过标签区分出前景和背景
    # labelCount = df.groupby('label').x.count().order(ascending=False).reset_index()
    labelCount = df.groupby('label').x.count().sort_values(ascending=False).reset_index()
    bgLabel = labelCount.label[0]
    df['bg'] = df.label.apply(lambda x: True if x == bgLabel else False)

    # 先把背景涂成指定颜色
    bg = df[df.bg]
    for i in range(len(bg)):
        # row = bg.irow(i)
        row = bg.iloc[i]
        pixels[int(row.x), int(row.y)] = bgColor


def splitImage(image):
    '''
    将图片按字符分开
    image    要切片Image对象
    '''
    pixels = image.load()
    result = []
    for i in range(4):
        smallImage = Image.new('RGB', (20, 20), "black")
        smallPixels = smallImage.load()
        for x in range(20):
            for y in range(20):
                smallPixels[x, y] = pixels[i * 20 + x, y]
        result.append(smallImage)
    return result


def imageToArray(image, bgColor=(255, 255, 255)):
    '''
    将一个image转化为黑白（1,0)的二维数组
    '''
    pixels = image.load()
    xRange = image.size[0]
    yRange = image.size[1]
    result = np.array(range(xRange * yRange))
    result.resize(xRange, yRange)
    for x in range(xRange):
        for y in range(yRange):
            # if pixels[x, y] == bgColor:
            if sum(pixels[x, y]) > 600:
                result[x, y] = 0
            else:
                result[x, y] = 1
    return result


def printArrayAsImage(array):
    '''
    给定一个位图数组将其打印出来
    array 要打印的数组
    '''

    xRange = array.shape[0]
    yRange = array.shape[1]
    for y in range(yRange):
        for x in range(xRange):
            print array[x, y],
        print


def readImageArrayMap(datapath):
    '''
    读取一个目录下的所有位图文件数据
    datapath  为数据文件存放的目录
    '''
    #result = {}

    #for fn in os.listdir(datapath):
    #    filename = os.path.join(datapath, fn)
    #    if len(fn) == 4 and fn.endswith('.pk'):
    #        #result[fn[0]] = pickle.load(open(filename, "rU" ))
    #        result.append([fn[0], pickle.load(open(filename, "rU"))])

    # 遍历目录下的所有文件导入内存
    result = []
    for path in [x[0] for x in os.walk(datapath)]:
        fileList = [join(path, f) for f in listdir(path) if isfile(join(path, f)) and f[-3:] == '.pk' and len(f) == 4]
        for filename in fileList:
            fn = split(filename)[-1]
            if len(fn) == 4 and fn.endswith('.pk'):
                result.append([fn[0], pickle.load(open(filename, "rU"))])
    return result


#arrayMapPath = '\\'.join(__file__.split('\\')[:-1]) + '\\data'
# 读取所有位图数据供readCharFromImage使用
imageArrayMap = readImageArrayMap(arrayMapPath)


def readCharFromImage(image):
    '''
    从图像文件中读取一个字符，这里假设图像文件中仅有一个字符，既在调用tesseract的时
    候使用,使用-psm选项
    image 需要读取的Image对象
    '''
    curImageArray = imageToArray(image)
    matchdata = []
    for char, array in imageArrayMap:
        cnt = 0
        match = 0
        for x in range(array.shape[0]):
            for y in range(array.shape[1]):
                if array[x, y] == 1:
                    cnt += 1
                    if curImageArray[x, y] == 1:
                        match += 1
        matchdata.append([char, match / cnt, cnt])
    df = pd.DataFrame(matchdata, columns=['char', 'rate', 'cnt'])
    # 由于背景处理可能会造成前景色的部分损耗，所以匹配率不一定是100%
    # 所以设定规则:匹配率在95%以上，取匹配点数最多的数据。
    # return df[df.rate > .95].sort('cnt', ascending=False).irow(0).char
    # return df[df.rate > .9].sort_values('cnt', ascending=False).irow(0).char
    return df.sort_values(['rate', 'cnt'], ascending=False).iloc[0].char


def readCodeFromImage(image):
    '''
    图像文件读取验证码全文(4个字符)
    image 需要读取的Image对象
    '''
    # 处理背景
    cleanBackGround(image)
    # 切割文字
    smallImageList = splitImage(image)
    # 读取验证码
    code = ''
    for im in smallImageList:
        code += readCharFromImage(im)
    return code


def readCodeFromFile(filepath):
    '''
    读取一个文件中的验证码
    filepath 图片文件的路径
    '''
    #image = Image.open(tempPath+'generateCode.jpg')
    image = Image.open(filepath)
    try:
        result = readCodeFromImage(image)
    except Exception:
        # raise
        result = ''
    return result


def printFilePath():
    print arrayMapPath


#%% 读取图像文件
#image = Image.open(r'd:\pydev\ticketpitcher\generateCode.jpg')
#plt.imshow(image)

#%% 获取验证码
#print readCodeFromImage(image)

