#!/usr/bin/env python
# -*- coding: utf-8 -*-

# time 2016.6.6

import xml.dom.minidom
import time
import urllib2
import optimization

dom = xml.dom.minidom.parseString('<data><rec>Hello!</rec></data>')
print dom
r = dom.getElementsByTagName('rec')
print r
print r[0].firstChild
print r[0].firstChild.data
'''
getElementByTagName(name) :
    在整个文档范围内搜索标签名与name相匹配的元素，然后返回一个包含所有满足条件的DOM节点的列表
firstChild ：
    返回对象的首个节点。在上面的例子中，r的首个节点就是代表文本“Hello的节点
 data :
    返回与对象有关的数据，大多数情况下这些数据就是该节点所内含的一个Unicode文本串

'''

kayakkey = 'YOURKEYHERE'

'对XML进行解析，以得到sid标签的内容'
def getkayaksession():
    # 构造URL以开启一个会话
    url = 'http://www.kayak.com/ident/apisession?token=%s&version=1' % kayakkey

    # 解析返回的XML
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

    # 找到<sid>xxxxxxxxx</sid>
    sid = doc.getElementsByTagName('sid')[0].firstChild.data
    return sid

'航班搜索'
def flightsearch(sid, origin, destination, depart_date):

    # 构造搜索用得URL
    url = 'http://www.kayak.com/s/apisearch?basicmode=true&oneway=y&origin=%s' % origin
    url +='&destination=%s&depart_date=%s' % (destination, depart_date)
    url += '&return_date=nane&depart_time=a&return_time=a'
    url += '&travelers=1&cabin=e&action=doFlights&apimode=1'
    url += '&_sid_ = %s&version= 1' % (sid)

    # 得到XML
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

    # 提取搜索用得ID
    searchid = doc.getElementsByTagName('searchid')[0].firstChild.data

    return searchid


'不断地请求结果，直到没有任何新结果获得为止'
def flightsearchresults(sid, searchid):

    # 删除开头的$和逗号，并把数字转化成浮点类型
    def parseprice(p):
        return float(p[1:].replace(',' , ''))

    # 遍历检测
    while 1:
        time.sleep(2)

        # 构造检测所用的URL
        url = 'http://www.kayak.com/s/basic/flight?'
        url += 'searchid=%s&c=5&apimode=1&_sid_=%s&version=1' % (searchid, sid)
        doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

        # 寻找morepending标签， 并等待其不再为true
        morepending = doc.getElementsByTagName('morepending')[0].firstChild
        if morepending == None or morepending.data == 'false':
            break

        # 现在，下载完整的列表
        url = 'http://www.kayak.com/s/basic/flighe?'
        url += 'searchid=%s&-999&apimode=1&_sid_=%s&version=1' % (searchid, sid)
        doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

        # 得到不同元素组成的列表
        prices = doc.getElementsByTagName('price')
        departures = doc.getElementsByTagName('depart')
        arrivals = doc.getElementsByTagName('arrive')

        # 用zip将它们连在一起
        return zip([p.firstChild.data.split(' ')[1] for p in departures],
                   [p.firstChild.data.split(' ')[1] for p in arrivals],
                   [parseprice(p.firstChild.data) for p in prices])


sid = getkayaksession()
searchid = flightsearch(sid, 'BOS', 'LGA', '11/17/2016')
f = flightsearchresults(sid, searchid)
print f[0:3]


'给Glass一家的不同成员建立一个完整的日程安排'
def createschedule(people, dest, dep, ret):
    # 得到搜索用得会话id
    sid = getkayaksession()
    flights = {}

    for p in people:
        name, origin = p
        # 往程航班
        searchid = flightsearch(sid, origin, dest, dep)
        flights[(origin, dest)] = flightsearchresults(sid, searchid)

        #　返程航班
        searchid = flightsearch(sid, origin, dest, dep)
        flights[(origin, dest)] = flightsearchresults(sid, searchid)

    return flights

f = createschedule(optimization.people[0:2], 'LGA', '11/17/2016', '11/19/2016')
optimization.flghts = f
domain = [(0, 30)] * len(f)
print optimization.geneticotimize(domain, optimization.schedulecost)
optimization.printshcedule(s)



