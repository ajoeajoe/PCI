#!/usr/bin/env python
# -*- coding: utf-8 -*-

# time : 2016.6.14

from random import random, randint
import math

'''葡萄酒价格'''


def wineprice(rating, age):  # 酒的等级， 储藏年代
    peak_age = rating - 50  # 峰值年

    # 根据等级来计算价格
    price = rating / 2
    if age > peak_age:
        # 经过“峰值年”， 后继5年里其品质将会变差
        price = price * (5 - (age - peak_age))
    else:
        # 价格在接近“峰值年”时会增加到原值的5倍
        price = price * (5 * ((age + 1) / peak_age))
    if price < 0: price = 0
    return price


'''构造表示葡萄酒价格的数据集'''


def wineset1():
    rows = []
    for i in range(300):
        # 随机生成年代和等级
        rating = random() * 50 + 50
        age = random() * 50

        # 得到一个参考价值
        price = wineprice(rating, age)

        # 增加“噪声”
        price *= (random() * 0.4 + 0.8)

        # 加入数据集
        rows.append({'input': (rating, age), 'result': price})
    return rows


data = wineset1()
'''
print wineprice(95.0, 3.0)
print wineprice(95.0, 8.0)
print wineprice(99.0, 1.0)
data = wineset1()
print data[0]
print data[1]
'''

'''
kNN算法
    定义相似度：欧几里德距离
'''


def euclidean(v1, v2):
    d = 0.0
    for i in range(len(v1)):
        d += (v1[i] - v2[i]) ** 2
    return math.sqrt(d)


'''
print data[0]['input']
print data[1]['input']
print euclidean(data[0]['input'], data[1]['input'])
'''

'''计算给定商品与原数据集中任一其他商品间的距离'''


def getdistances(data, vec1):
    distancelist = []
    for i in range(len(data)):
        vec2 = data[i]['input']
        distancelist.append((euclidean(vec1, vec2), i))
    distancelist.sort()
    return distancelist


'''kNN函数，利用上述距离列表，并对其中的前k项结果求出了平均值'''


def knnestimate(data, vec1, k=5):
    # 得到经过排序的距离值
    dlist = getdistances(data, vec1)
    avg = 0.0  # 平均值

    # 对前k项结果求平均
    for i in range(k):
        idx = dlist[i][1]
        avg += data[idx]['result']
    avg = avg / k
    return avg

'''
print knnestimate(data, (95.0, 3.0))
print knnestimate(data, (99.0, 3.0))
print knnestimate(data, (99.0, 5.0))  # 估计价格
print wineprice(99.0, 5.0)  # 实际价格
print knnestimate(data, (95.0, 3.0), k=1)
'''


'''为近邻分配权重'''
def inverseweight(dist, num=1.0, const=0.1): # 权重反函数
    return num / (dist + const)

'''
减法权重函数:
    用一个常量值减去距离，如果相减的结果大于0，则权重为相减的结果，否则，结果为0
'''
def subtractweight(dist, const=1.0):
    if dist > const:
        return 0
    else:
        return const - dist


'''高斯权重函数'''
def gaussian(dist, sigma=10.0):
    return math.e ** (-dist ** 2 / (2 * sigma ** 2))


'''
print subtractweight(0.1)
print inverseweight(0.1)
print gaussian(0.1)
print gaussian(1.0)
print subtractweight(1)
print inverseweight(1)
print gaussian(3.0)
'''


'''加权kNN'''
def weightedknn(data, vec1, k=5, weightf=gaussian):
    # 得到距离值
    dlist = getdistances(data, vec1)
    avg = 0.0
    totalweight = 0.0

    # 得到加权平均值
    for i in range(k):
        dist = dlist[i][0]
        idx = dlist[i][1]
        weight = weightf(dist)
        avg += weight * data[idx]['result']
        totalweight += weight
    avg = avg / totalweight
    return avg


'''
print wineprice(99.0, 5.0)  # 实际价格
print weightedknn(data, (99.0, 5.0))
print knnestimate(data, (99.0, 5.0))  # 估计价格
'''


'''
交叉验证：
    将数据拆分成训练集与测试集
'''
def devidedata(data, test=0.05):
    trainset = []
    testset = []
    for row in data:
        if random() < test:
            testset.append(row)
        else:
            trainset.append(row)
    return trainset, testset



'''测试算法'''
def testalgorithm(algf, trainset, testset):
    error = 0.0
    for row in testset:
        guess = algf(trainset, row['input'])
        error += (row['result'] - guess) ** 2
    return error / len(testset)


'''交叉验证'''
def crossvalidate(algf, data, trials=100, test=0.05):
    error = 0.0
    for i in range(trials):
        trainset, testset = devidedata(data, test)
        error += testalgorithm(algf, trainset, testset)
    return error / trials


'''
print crossvalidate(knnestimate, data)
def knn3(d, v):
    return knnestimate(d, v, k=3)
print crossvalidate(knn3, data)
def knn1(d, v):
    return knnestimate(d, v, k=1)
print crossvalidate(knn1, data)
print crossvalidate(weightedknn, data)
def knninverse(d, v):
    return weightedknn(d, v, weightf=inverseweight)
print crossvalidate(knninverse, data)
'''


def wineset2():
    rows = []
    for i in range(300):
        # 随机生成年代和等级
        rating = random() * 50 + 50
        age = random() * 50

        aisle = float(randint(1, 20))
        bottlesize = [375.0, 750.0, 1500.0, 3000.0] [randint(0, 3)]

        # 得到一个参考价值
        price = wineprice(rating, age)

        price *= (bottlesize / 750)

        # 增加“噪声”
        price *= (random() * 0.9 + 0.2)

        # 加入数据集
        rows.append({'input': (rating, age), 'result': price})
    return rows


'''
data2 = wineset2()
print "------------------------"
print crossvalidate(knn3, data2)
print crossvalidate(weightedknn, data2)
'''


'''按比例缩放'''
def rescale(data, scale):
    scaleddata = []
    for row in data:
        scaled = [scale[i] * row['input'][i] for i in range(len(scale))]
        scaleddata.append({'input': scaled, 'result': row['result']})
    return scaleddata


'''
sdata = rescale(data, [10, 10, 0, 0.5])
print "------------------------"
print crossvalidate(knn3, sdata)
'''

'''对缩放结果进行优化：成本函数'''
def createcostfunction(algf, data):
    def costf(scale):
        sdata = rescale(data, scale)
        return crossvalidate(algf, sdata, trials=10)
    return costf

weightdomain = [(0, 20)] * 4


'''
import optimization
costf = createcostfunction(knnestimate, data)
print optimization.annealingoptimize(weightdomain, costf, step=2)
#print optimization.geneticotimize(weightdomain, costf, popsize=5, lrate=1, maxv=4, iters=20)
'''


'''不对称分布'''
def wineset3():
    rows = wineset1()
    for row in rows:
        if random() < 0.5:
            # 葡萄酒是从折扣店购得的
            row['result'] *= 0.5
    return rows


'''
data = wineset3()
print wineprice(99.0, 20.0)
print weightedknn(data, [99.0, 20.0])
'''



'''估计概率密度'''
def probguess(data, vec1, low, high, k=5, weightf=gaussian):
    dlist = getdistances(data, vec1)
    nweight = 0.0
    tweight = 0.0

    for i in range(k):
        dist = dlist[i][0]
        idx = dlist[i][1]
        weight = weightf(dist)
        v = data[idx]['result']

        # 当前数据点位于指定范围吗
        if v >= low and v < high:
            nweight += weight
        tweight += weight
    if tweight == 0: return 0

# 概率等于位于指定范围内的权重值除以所有权重值
    return nweight/tweight

'''
print probguess(data, [99, 20], 40, 80)
print probguess(data, [99, 20], 80, 120)
print probguess(data, [99, 20], 120, 1000)
print probguess(data, [99, 20], 30, 120)
'''



from pylab import *
'''画图功能测试'''
'''
a = array([1, 2, 3, 4])
b = array([4, 3, 2, 1])
plot(a, b)
show()
t1 = arange(0.0, 10, 0.1)
plot(t1, sin(t1))
show()
'''

'''累积概率'''
def cumulativegraph(data, vec1, high, k=5, weightf=gaussian):
    t1 = arange(0.0, high, 0.1)
    cprob = array([probguess(data, vec1, 0, v, k,weightf) for v in t1])
    plot(t1, cprob)
    show()

cumulativegraph(data, (1, 1), 120)


def probablitygraph(data, vec1, high, k=5, weightf=gaussian, ss=5.0):
    # 建立一个代表价格的值域范围
    t1 = arange(0.0, high, 0.1)

    # 得到整个值域范围内的所有概率
    probs = [probguess(data, vec1, v, v+0.1, k, weightf) for v in t1]

    # 通过加上近邻概率的高斯计算结果， 对概率值做平滑处理
    smoothed = []
    for i in range(len(probs)):
        sv = 0.0
        for j in range(0, len(probs)):
            dist = abs(i - j) * 0.1
            weight = gaussian(dist, sigma =ss)
            sv += weight * probs[j]
        smoothed.append(sv)
    smoothed = array(smoothed)

    plot(t1, smoothed)
    show()

probablitygraph(data, (1, 1), 6)







