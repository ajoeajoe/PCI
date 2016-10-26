#!/usr/bin/env python
# -*- coding: utf-8 -*-

# time : 2016.6.20


class matchrow:
    def __init__(self, row, allnum=False):
        if allnum:
            self.data = [float(row[i]) for i in range(len(row) - 1)]
        else:
            self.data = row[0: len(row) - 1]
        self.match = int(row[len(row) - 1])  # match表示是否配对成功的1或者0


# allnum参数表示是只加载年龄还是加载全部数据
def loadmatch(f, allnum=False):
    rows = []
    for line in file(f):
        rows.append(matchrow(line.split(','), allnum))
    return rows


agesonly = loadmatch('../data/agesonly.csv', allnum=True)
matchmaker = loadmatch('../data/matchmaker.csv')

'''决策树分类器'''
from pylab import *


def plotagematches(rows):
    # 读出配对成功的x坐标和y坐标
    xdm, ydm = [r.data[0] for r in rows if r.match == 1], \
               [r.data[1] for r in rows if r.match == 1]
    # 读出不配对成功的x坐标和y坐标
    xdn, ydn = [r.data[0] for r in rows if r.match == 0], \
               [r.data[1] for r in rows if r.match == 0]

    # 画绿点
    plot(xdm, ydm, 'go')
    # 画红点
    plot(xdn, ydn, 'ro')

    show()


# plotagematches(agesonly)


'''基本的线性分类'''


def lineartrain(rows):
    averages = {}
    counts = {}

    for row in rows:
        # 得到该坐标点所属的分类
        c1 = row.match

        # 下面两句应该只有第一次出现的时候才会有用吧
        averages.setdefault(c1, [0.0] * (len(row.data)))
        counts.setdefault(c1, 0)

        # 将该坐标点加入averages中
        for i in range(len(row.data)):
            averages[c1][i] += float(row.data[i])

        # 记录每个分类中有多少坐标点
        counts[c1] += 1

        # 将总和除以计数值以求得平均值
        for c1, avg in averages.items():
            for i in range(len(avg)):
                avg[i] /= counts[c1]

        return averages


# avgs = lineartrain(agesonly)
# print avgs



'''两个向量的点积'''


def dotproduct(v1, v2):
    return sum([v1[i] * v2[i] for i in range(len(v1))])


'''点积分类函数'''


def dpclassify(point, avgs):
    # 这里之所以avgs[1]是代表分类点0的，因为在去读agesonly的数据时，分类1先被读进去来了。
    b = (dotproduct(avgs[1], avgs[1]) - dotproduct(avgs[0], avgs[0])) / 2
    y = dotproduct(point, avgs[0]) - dotproduct(point, avgs[1]) + b
    if y > 0:
        return 0
    else:
        return 1


avgs = lineartrain(agesonly)

print "两位是30岁", dpclassify([30, 30], avgs)
print "男25岁和女40岁", dpclassify([25, 40], avgs)



'''分类特征处理：是否问题'''


def yesno(v):
    if v == 'yes':
        return 1
    elif v == 'no':
        return -1
    else:
        return 0

'''
兴趣列表：
    以浮点数的形式返回列表中匹配项的数量
    '''

def matchcount(interest1, interest2):
    l1 = interest1.split(':')
    l2 = interest2.split(':')
    x = 0
    for v in l1:
        if v in l2:
            x += 1
    return x



'''利用Yahoo！ Maps来确定距离： 若无法使用Yahoo！API 时'''
def milesdistance(a1, a2):
    return 0


