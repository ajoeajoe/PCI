#!/usr/bin/env python
# -*- coding: utf-8 -*-

# time: 2016.6.2

import time
import random
import math

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

# New York的LaGuardia机场
destination = 'LGA'

# 将航班数据载入一个字典中，以起点为键，以可能的航班信息明细为值
flights = {}

for line in file('../data/schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])

    # 将航班详情添加到列表中
    flights[(origin, dest)].append((depart, arrive, int(price)))


# 计算某个给定时间在一天中的分钟数
def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]


# 将人们决定搭乘的所有航班打印成表格
def printshcedule(r):
    for d in range(len(r) / 2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[2 * d]]  # 往程航班信息
        ret = flights[(destination, origin)][r[2 * d + 1]]  # 返程航班信息
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin, out[0], out[1], out[2], ret[0], ret[1], ret[2])


# s = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
# printshcedule(s)


'成本函数'


def schedulecost(sol):
    totalprice = 0  # 总价格
    latestarrival = 0  # 最晚到达时间
    earliestdep = 24 * 60  # 最早离开时间

    for d in range(len(sol) / 2):
        # 得到往程航班和返程航班
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2 * d])]
        returnf = flights[(destination, origin)][int(sol[2 * d + 1])]

        # 总价格等于所有往程航班和返程航班之和
        totalprice += outbound[2]
        totalprice += returnf[2]

        # 记录最晚到达时间和最早离开时间
        if latestarrival < getminutes(outbound[1]):
            latestarrival = getminutes(outbound[1])
        if earliestdep > getminutes(returnf[0]):
            earliestdep = getminutes(returnf[0])

    # 每个人必须在机场等待直到最后一个人到达为止
    # 他们也必须在相同时间到达，并等候他们的返程航班
    totalwait = 0
    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[2 * d])]
        returnf = flights[(destination, origin)][int(sol[2 * d + 1])]
        totalwait += latestarrival - getminutes(outbound[1])
        totalwait += getminutes(returnf[0]) - earliestdep

    # 这个题解要求多付一天的汽车租用费用吗？ 如果是， 则费用为50美元
    if latestarrival < earliestdep:
        totalprice += 50

    return totalprice + totalwait


# print '成本函数值：', schedulecost(s)


'随机搜索'


def randomoptimize(domain, costf):
    best = 999999999  # 最优成本
    bestr = None  # 最优解，
    for i in range(10000):
        # 创建一个随机解
        r = [random.randint(domain[i][0], domain[i][1])
             for i in range(len(domain))]

        # 得到成本
        cost = costf(r)

        # 与到目前为止的最优解进行比较
        if cost < best:
            best = cost
            bestr = r
    return r


domain = [(0, 9)] * (len(people) * 2)

'''
s = randomoptimize(domain, schedulecost)
print s
print schedulecost(s)
printshcedule(s)
'''

'爬山法'


def hillclimb(domain, costf):
    # 创建一个随机解
    sol = [random.randint(domain[i][0], domain[i][1])
           for i in range(len(domain))]

    # 主循环
    while 1:

        # 创建相邻解得列表
        neighbors = []
        for j in range(len(domain)):

            # 在每个方向是相对于原值偏离一点
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j + 1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j + 1:])

        # 在相邻解中寻找最优解
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]

            # 如果没有更好的解， 则退出循环
            if best == current:
                break

        return sol


'''
s = hillclimb(domain, schedulecost)
print s
print schedulecost(s)
printshcedule(s)
'''

'模拟退火法'


def annealingoptimize(domain, costf, T=10000.0, cool=0.95, step=1):
    # 随机化初始值
    vec = [int(random.randint(domain[i][0], domain[i][1]))
           for i in range(len(domain))]

    while T > 0.1:
        # 选择一个索引值
        i = random.randint(0, len(domain) - 1)

        # 选择一个改变索引值的方向
        dir = random.randint(-step, step)

        # 创建一个代表题解的新列表， 改变其中一个值
        vecb = vec[:]
        vecb[i] += dir
        if vecb[i] < domain[i][0]:
            vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]:
            vecb[i] = domain[i][1]

        # 计算当前成本和新的成本
        ea = costf(vec)
        eb = costf(vecb)

        # 它是更好的解吗？ 或者是趋向最优解的可能的临界解吗？
        if (eb < ea or random.random() < pow(math.e, -(eb - ea) / T)):
            vec = vecb

        # 降低温度
        T *= cool
    return vec


'''
s = annealingoptimize(domain, schedulecost)
print s
print schedulecost(s)
printshcedule(s)
'''


'遗传算法'
'''
popsize : 种群大小
mutprob : 种群的新成员是由变异而非交叉得来的概率
elite : 种群中被认为是优解且被允许传入下一代的部分
maxiter : 须运行多少代
'''

def geneticotimize(domain, costf, popsize=50, step=1,
                   mutprob=0.2, elite=0.2, maxiter=100):

    # 变异操作
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i] - step] + vec[i + 1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [vec[i] + step] + vec[i + 1:]

    # 交叉操作
    def crossover(r1, r2):
        i = random.randint(1, len(domain) - 2)
        return r1[0:i] + r2[i:]

    # 构造初始种群
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1])
               for i in range(len(domain))]
        pop.append(vec)

    # 每一代中有多少胜出者
    topelite = int(elite * popsize)

    # 主循环
    for i in range(maxiter):
        scores = [(costf(v), v) for v in pop]
        scores.sort()
        ranked = [v for (s, v) in scores]

        # 从纯粹的胜出者开始
        pop = ranked[0:topelite]

        # 添加变异和配对后的胜出者
        while len(pop) < popsize:
            if random.random() < mutprob:

                # 变异
                c = random.randint(0, topelite)
                pop.append(mutate(ranked[c]))

            else:

                # 交叉
                c1 = random.randint(0, topelite)
                c2 = random.randint(0, topelite)
                pop.append(crossover(ranked[c1], ranked[c2]))

            # 打印当前最优值
            print scores[0][0]

        return scores[0][1]

'''
s = geneticotimize(domain, schedulecost)
print s
printshcedule(s)
'''
