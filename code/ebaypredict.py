#!/usr/bin/env python
# -*- coding: utf-8 -*-

# time : 2016.6.17

import httplib
import xml.dom.minidom
from xml.dom.minidom import parseString

devKey = 'd7681f43-9bef-4fec-ae04-0d398e18bd1e'
appKey = 'zgc-ebaytest-SBX-b5a63948a-4ad4c382'
certKey = 'SBX-5a63948a96a4-7033-4ddf-8b0d-ab34'
userToken = 'AgAAAA**AQAAAA**aAAAAA**L79jVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GgAJKAoA+dj6x9nY+seQ**rNkDAA**AAMAAA**EzIkOI4Jy1TSjdsNhGxGTEiS/UrbkK+qImLHIrIsSoFrMRoPIgi9PvJRMmV6eZtv62a/CxSo2YrC++kKfnh08/Lv29vdeBEq9eiXf9ft0VmD5jXgq58LCCMHihT/ccboVch4qO3trHnZlYRS2Ab9vj0KbhPTLo36c9ZsykPzh9Oena1hj0tBlzYGDfRnlyjRfnioeYd6t8IuRVg5HnjjliEiasFSaeQZIRvxOMZpn0OeCvPp4gluOvFKQ5barviIcns0NJN7dMgfYpZFplcIcWG+MPDDRibGQQTy6qryt5OEww4aKlTboKsvVP/UTGm+TOuBrWnA117+VKexFRcSxAZ3KUOpa2qPFQTENFCYYgEHvaN0WArmY6mvCdgvXFatjBOfcoYo1TN6evb6h2Kz1DgiSrxmUKIzQfuJFzvsRGDt6XDehSH2nZQJW4UshN+T7vb64nPUtMZo09gTnVuXgn9CHNjGjPGgCUvNkcbD4uAJ+dgXEJ7Rbiwjg52FzEDBsZvY2/UteCVUttapB2Zlt4/0ccnTswFnihAvB4P+xpComhiXvL4ljfGo89iQxODuq4UStS7P/bb8J23RTKDoJJ3l9yOzikgV2Km/3fRCxPib1xTGvdamib0C6kMMpGnZy6z5yJlfBCr75/1rmMTnWJeivswJLjzqQpKqydIqVre8C89Se+ijKFnKcm/vWZhwi8JR7nu4my0OUJHQWmg8nvYUGqI6Hw1m1mmlPVlp8pBilDTam3YE64QtpCeLn8pD'
serverUrl = 'api.ebay.com'


'''建立连接'''
def getHeaders(apicall, siteID="0", compatabilityLevel = "433"):
    headers = {"X-EBAY-API-COMPATIBILITY-LEVEL": compatabilityLevel,
               "X-EBAY-API-DEV-NAME": devKey,
               "X-EBAY-API-APP-NAME": appKey,
               "X-EBAY-API-CERT-NAME": certKey,
               "X-EBAY-API-CALL-NAME": apicall,
               "X-EBAY-API-SITEID": siteID,
               "Content-Type": "text/xml"}
    return headers


'''发送请求'''
def sendRequest(apicall,xmlparameters):
    connection = httplib.HTTPSConnection(serverUrl)
    connection.request("POST", '/ws/api.dll', xmlparameters, getHeaders(apicall))
    response = connection.getresponse()
    if response.status != 200:
        print "Error sending request:" + response.reason
    else:
        data = response.read()
        connection.close()
    return data


'''查找节点并返回节点对应的内容'''
def getSingleValue(node, tag):
    nl = node.getElementsByTagName(tag)
    if len(nl) > 0:
        tagNode = nl[0]
        if tagNode.hasChildNodes():
            return tagNode.firstChild.nodeValue
    return '-1'


'''
执行搜索:
    Query: 包含搜索词条的字符串，使用该参数就如同在eBay的主页上手工进行搜索一样
    CategoryID: 这是一个数字，它指定了我们想要搜索的分类
'''

def doSearch(query, categoryID=None, page=1):
    xml = "<?xml version='1.0' encoding='utf-8'?>" + \
          "<GetSearchResultsRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">" + \
          "<RequesterCredentials><eBayAuthToken>" + \
          userToken + \
          "</eBayAuthToken></RequesterCredentials>" + \
          "<Pagination>" + \
          "<EntriesPerPage>200</EntriesPerPage>" + \
          "<PageNumber>" + str(page) + "</PageNumber>" + \
          "</Pagination>" + \
          "<Query>" + query + "</Query>"
    if categoryID != None:
        xml +="<CategoryID>" + str(categoryID) + "</CategoryID>"
    xml += "</GetSearchRequestsResults>"

    data = sendRequest('GetSearchResults', xml)
    response = parseString(data)
    itemNodes = response.getElementsByTagName('Item')
    results = []
    for item in itemNodes:
        itemId = getSingleValue(item, 'ItemID')
        itemTitle = getSingleValue(item, 'Title')
        itemPrice = getSingleValue(item, 'CurrentPrice')
        itemEnds = getSingleValue(item, 'EndTime')
        results.append((itemId, itemTitle, itemPrice, itemEnds))
    return results



'''分类函数'''
def getCategory(query='', parentID=None, siteID='0'):
    lquery = query.lower()
    xml = "<?xml version='1.0' encoding='utf-8'?>" + \
          "<GetCategoriesRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">" + \
          "<RequesterCredentials><eBayAuthToken>" + \
          userToken + \
          "</eBayAuthToken></RequesterCredentials>" + \
          "<DetailLevel>ReturnAll</DetailLevel>" + \
          "<ViewAllNodes>true</ViewAllNodes>" + \
          "<CategorySiteID>" + siteID + "</CategorySiteID>"
    if parentID == None:
        xml += "<LevelLimet>1</LevelLimit>"
    else:
        xml += "<CategoryParent>" + str(parentID) + "</CategoryParent>"
    xml += "</GetCategoriesRequest>"
    data = sendRequest('GetCategory', xml)
    categortList = parseString(data)
    catNodes = categortList.getElementsByTagName('Category')
    for node in catNodes:
        catid = getSingleValue(node, 'CategoryID')
        name = getSingleValue(node, 'CategoryName')
        if name.lower().find(lquery) != -1:
            print catid, name


laptops = doSearch('laptop')
print laptops[0:30]
print getCategory('computers')
print getCategory('laptops', parentID=58058)
laptops = doSearch('laptop', categoryID=51148)
print laptops[0:10]
print getCategory('Men')



'''获取商品明细'''
def getItem(itemID):
    xml = "<?xml version='1.0' encoding='utf-8'?>" + \
          "<GetItemRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">" + \
          "<RequesterCredentials><eBayAuthToken>" + \
          userToken + \
          "</eBayAuthToken></RequesterCredentials>" + \
          "<ItemID>" + str(itemID) + "</ItemID>" + \
          "<DetailLevel>ItemReturnAttributes</DetailLevel>" + \
          "</GetItemRequest>"
    data = sendRequest('GetItem', xml)
    result = {}
    response = parseString(data)
    result['title'] = getSingleValue(response, 'Title')
    sellingStatusNode = response.getElementsByTagName('SellingStatus')[0];
    result['price'] = getSingleValue(sellingStatusNode, 'CurrentPrice')
    result['bids'] = getSingleValue(sellingStatusNode, 'BidCount')
    seller = response.getElementsByTagName('Seller')
    result['feedback'] = getSingleValue(seller[0], 'FeedbackScore')
    attributeSet = response.getElementsByTagName('Attribute')
    attributes = {}
    for att in attributeSet:
        attID = att.attributes.getNameItem('attributeID').nodeValue
        attValue = getSingleValue(att, 'ValueLiteral')
        attributes[attID] = attValue
    result['attributes'] = attributes
    return result


print getItem(laptops[7][0])


'''构造价格预测程序'''
def makeLaptopDataset():
    searchResults = doSearch('laptop', categoryID=51148)
    result = []
    for r in searchResults:
        item = getItem(r[0])
        att = item['attributes']
        try:
            data = (float(att['12']), float(att['26444']),
                    float(att['26446']), float(att['25710'])
                    )
            entry = {'input': data, 'result': float(item['price'])}
            result.append(entry)
        except:
            print item['title'] + 'failed'
    return result

set1 = makeLaptopDataset()
import numpredict
print numpredict.knnestimate(set1, (1024, 1000, 14, 40, 1000))

