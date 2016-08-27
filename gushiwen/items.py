#!/usr/local/bin/python
# _*_ coding:utf-8 _*_

import scrapy


"""
定义爬取古诗文网（gushiwen.org）的各数据项
时代：（先秦、唐、宋。。。）
作者
   风格
   作者介绍（名、字、生卒、画像。。。）
作品：
    作品正文、作品背景、后世评价、作品影响、其他名作
链接

"""

class GushiwenItem(scrapy.Item):

    PoetryLinks       = scrapy.Field()
    #处理具体作品
    PoetyName         = scrapy.Field()
    PoetryDestiny     = scrapy.Field()
    PoetryAuthor      = scrapy.Field()
    PoetryPingfen     = scrapy.Field()
    PoetryContent     = scrapy.Field()
    #处理参考翻译,使用嵌套
    Cankaofanyi       = scrapy.Field()
    #处理参考赏析，使用嵌套
    Cankaoshangxi     = scrapy.Field()
    #处理作者介绍，使用嵌套
    AuthorInstr       = scrapy.Field()
   
   

