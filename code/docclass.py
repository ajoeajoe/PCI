#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' 文档分类 '''
# time 2016.6.7

import re
import math


'''导入训练样本数据'''
def sampletrain(c1):
    c1.train('Nobody owns the water.', 'good')
    c1.train('the quick rabbit jumps fences', 'good')
    c1.train('buy pharmaceuticals now', 'bad')
    c1.train('make quick money at the online casino', 'bad')
    c1.train('the quick brown fox jumps', 'good')


'''
该函数以任何非字母类字符为分隔符对文本进行划分，
将文本拆分成了一个个单词。这一过程只留下了真正的单词，
并将这些单词全都转换成小写形式
'''
def getwords(doc):
    splitter = re.compile('\\W*')
    # 根据非字母符进行单词拆分
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]

    # 只返回一组不重复的单词
    return dict([(w, 1) for w in words])



'''
代表分类器的类
'''
class classifier:
    def __init__(self, getfeatures, filename = None):
        # 统计特征/分类组合的数量
        self.fc = {}  # fc记录位于各分类中的不同特征的数量
        # 统计每个分类中的文档数量
        self.cc = {}  # cc是一个记录各分类被使用次数的字典
        self.getfeatures = getfeatures  # 从即将被归类的内容项中提取出特征来，本例中是getwords函数

    '''实现计数值的增加和获取'''
    def incf(self, f, cat): # cat 分类
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1

    # 增加对某一部分类的计数值
    def incc(self, cat):
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1

    # 某一特征出现于某一类中的次数
    def fcount(self, f, cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    # 属于某一分类的内容项数量
    def catcount(self, cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0

    # 所有内容项(本例中为文档)的数量
    def totalcount(self):
        return sum(self.cc.values())

    # 所有分类的列表
    def categories(self):
        return self.cc.keys()

    def train(self, item, cat):
        features = self.getfeatures(item)
        # 针对该分类为每个特征增加计数值
        for f in features:
            self.incf(f, cat)

        # 增加针对该分类的计数值
        self.incc(cat)

    '''计算概率'''
    def fprob(self, f, cat):
        if self.catcount(cat) == 0: return 0
        # 特征在分类中出现的总次数， 除以分类中包含内容项的总数
        return self.fcount(f, cat) / self.catcount(cat)

    def weightedprob(self, f, cat, prf, weight = 1.0, ap = 0.5): # ap 假设概率
        # 计算当前的概率值
        basicprob = prf(f, cat)

        # 统计特征在所有分类中出现的次数
        totals = sum([self.fcount(f, c) for c in self.categories()])

        # 计算加权平均
        bp = ((weight * ap) + (totals * basicprob)) / (weight + totals)
        return bp


'''
c1 = classifier(getwords)
c1.train('the quick brown fox jumps over the lazy dog', 'good')
c1.train('make quick money in the online casino', 'bad')
print c1.fcount('the', 'good')
print c1.fcount('quick', 'bad')
'''

'''
c1 = classifier(getwords)
sampletrain(c1)
print c1.weightedprob('money', 'good', c1.fprob)

sampletrain(c1)
print c1.weightedprob('money', 'good', c1.fprob)
#print c1.fprob('quick', 'good')
'''


class naivebayes(classifier):
    def __init__(self, getfeatures):
        classifier.__init__(self,getfeatures)
        self.thresholds = {}

    # 提取特征(单词)并将所有单词的概率值相乘以求出整体概率
    def docprob(self, item, cat):
        features = self.getfeatures(item)

        # 将所有特征值的概率相乘
        p = 1
        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)
            return p

    # 计算分类的概率，并返回Pr(Document|Category)与Pr(Category)的乘积
    def prob(self, item, cat):
        catprob = self.catcount(cat) / self.totalcount() # 分类概率
        docprob = self.docprob(item, cat)
        return docprob * catprob

    # 设值和取值的方法，令其默认返回值为1.0
    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        if cat not in self.thresholds:
            return  1.0
        return self.thresholds[cat]

    def classify(self, item, default=None):
        probs = {}
        # 寻找概率最大的分类
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat

        # 确保概率值超出阈值 * 次大概率值
        for cat in probs:
            if cat == best:
                continue
            if probs[cat] * self.getthreshold(best) > probs[best]:
                return default
        return best


'''
c1 = naivebayes(getwords)
sampletrain(c1)
print c1.prob('quick rabbit', 'good')
print c1.prob('quick rabbit', 'bad')
'''

'''
c1 = naivebayes(getwords)
sampletrain(c1)
print c1.classify('quick rabbit', default='unknown')
print c1.classify('online', default='unknown')
c1.setthreshold('bad', 3.0)
print c1.classify('quick money', default='unknown')
for i in range(10):
    sampletrain(c1)
print c1.classify('quick money', default='unknown')
'''


class fisherclassifier(classifier):
    def cprob(self, f, cat):
        # 特征在该分类中出现的频率
        clf = self.fprob(f, cat)
        if clf == 0:
            return 0

        # 特征在所有分类中出现的频率
        freqsum = sum([self.fprob(f, c) for c in self.categories()])

        # 概率等于特征在该分类中出现的频率除以总体频率
        p = clf / (freqsum)

        return p

    def fisherprob(self, item, cat):
        # 将所有的概率值相乘
        p =1
        features = self.getfeatures(item)
        for f in features:
            p *= (self.weightedprob(f, cat, self.cprob))

        # 取自然对数， 并乘以-2
        fscore = -2 * math.log(p)

        # 利用倒置对数卡方函数求得概率
        return self.invchi2(fscore, len(features) * 2)

    def invchi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df//2):
            term *= m / i
            sum += term
        return min(sum, 1.0)

    def __init__(self, getfeatures):
        classifier.__init__(self, getfeatures)
        self.minimums = {}

    def setminimum(self, cat, min):
        self.minimums[cat] = min

    def getminimum(self, cat):
        if cat not in self.minimums:
            return 0
        return self.minimums[cat]

    def classify(self, item, default=None):
        # 循环遍历并寻找最佳结果
        best = default
        max = 0.0
        for c in self.categories():
            p = self.fisherprob(item, c)
            # 确保其超过下限值
            if p > self.getminimum(c) and p > max:
                best = c
                max = p
        return best



'''
c1 = fisherclassifier(getwords)
sampletrain(c1)
print c1.cprob('quick', 'good')
print c1.cprob('money', 'bad')
print c1.weightedprob('money', 'bad', c1.cprob)
'''

'''
c1 = fisherclassifier(getwords)
sampletrain(c1)
print c1.cprob('quick', 'good')
print c1.fisherprob('quick rabbit', 'good')
print c1.fisherprob('quick rabbit', 'bad')
'''

c1 = fisherclassifier(getwords)
sampletrain(c1)
print c1.classify('quick rabbit')
print c1.classify('quick money')
c1.setminimum('bad', 0.8)
print c1.classify('quick money')
c1.setminimum('good', 0.4)
print c1.classify('quick money')
