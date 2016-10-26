#!/usr/bin/env python
# -*- coding: utf-8 -*-

# time 2016.6.7

import math
import optimization

people = ['Charlie', 'Augustus', 'Veruca', 'Violet', 'Mike', 'Joe', 'Willy', 'Miranda']

links = [('Augustus', 'Willy'),
         ('Mike', 'Joe'),
         ('Miranda', 'Mike'),
         ('Violet', 'Augustus'),
         ('Miranda', 'Willy'),
         ('Charlie', 'Mike'),
         ('Veruca', 'Joe'),
         ('Miranda', 'Augustus'),
         ('Willy', 'Augustus'),
         ('Joe', 'Charlie'),
         ('Veruca', 'Augustus'),
         ('Miranda', 'Joe')]

'''
遍历每一对连线，并利用连线端点的当前坐标来判定他们是否交叉，
如果交叉，则总分加1
'''


def crosscount(v):
    # 将数字序列转换成一个person:(x, y)的字典
    loc = dict([(people[i], (v[i * 2], v[i * 2 + 1])) for i in range(0, len(people))])
    total = 0

    # 遍历每一对连线
    for i in range(len(links)):
        for j in range(i + 1, len(links)):

            # 获取坐标位置
            (x1, y1), (x2, y2) = loc[links[i][0]], loc[links[i][1]]
            (x3, y3), (x4, y4) = loc[links[j][0]], loc[links[j][1]]

            den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

            # 如果两线平行， 则den == 0
            if den == 0:
                continue

            # 否则， ua与ub就是两条交叉线的分数值
            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
            ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den

            # 如果两条直线的分数值介于0和1之间， 则两线彼此相交
            if ua > 0 and ua < 1 and ub > 0 and ub < 1:
                total += 1

        for i in range(len(people)):
            for j in range(i + 1, len(people)):
                # 获得两节点的位置
                (x1, y1), (x2, y2) = loc[people[i]], loc[people[j]]

                # 计算两节点的间距
                dist = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
                # 对间距小于50个像素的节点进行判罚
                if dist < 50:
                    total +=(1.0 - (dist / 50.0))

        return total


domain = [(10, 370)] * (len(people) * 2)

sol = optimization.randomoptimize(domain, crosscount)
print crosscount(sol)
print sol
sol1 = optimization.annealingoptimize(domain, crosscount, step = 50, cool = 0.99)
print crosscount(sol1)
print sol1


# 绘制网格
from PIL import Image,ImageDraw
def drawnetwork(sol):
    # 建立image对象
    img = Image.new('RGB', (400, 400), (255, 255, 255))
    draw = ImageDraw(img)

    # 建立标示位置信息的字典
    pos = dict([people[i], (sol[i * 2], sol[i * 2 + 1]) for i in range(0, len(people))])

    # 绘制连线
    for (a, b) in links:
        draw.line((pos[a], pos[b]), fill = (255, 0, 0))

    # 绘制代表人的节点
    for n, p in pos.items():
        draw.text(p, n (0, 0, 0))

    img.show()

drawnetwork(sol)
