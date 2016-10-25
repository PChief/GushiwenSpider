# _*_ coding:utf-8 _*_

import scrapy


"""
定义爬取古诗文网（gushiwen.org）的各数据项
朝代：
   先秦、唐、宋...
作者：
   作者介绍（名、字、生卒、）
作品：
    作品正文、作品背景、后世评价、作品影响、其他名作
链接
"""


class GushiwenItem(scrapy.Item):
    """
    主程序只需要提取出作品链接即可,每页最多十个
    送入redis队列view:start_urls
    """
    view_urls = scrapy.Field()


class ViewItem(scrapy.Item):
    """
    提取作品名称、朝代、作者名、作者介绍
    """
    poetry_name = scrapy.Field()
    poetry_link = scrapy.Field()
    poetry_dynasty = scrapy.Field()
    pingfen = scrapy.Field()
    # 区分有无作者
    # 有作者的话在 div.shileft div.son2 p a 的文本为作者名
    shileft_son2 = scrapy.Field()
    # 无作者的话在 div.shileft div.son2 p 第二个标签为 佚名或者孟子及其弟子等
    div_son5 = scrapy.Field()
    author_name = scrapy.Field()
    author_intro_link = scrapy.Field()
    poetry_fanyi_list = scrapy.Field()
    # 正文
    poetry_mainbody_meta_content = scrapy.Field()


class FanyiItem(scrapy.Item):
    """
    通过翻译链接
    http://so.gushiwen.org/fanyi_123.aspx
    http://so.gushiwen.org/shangxi_123.aspx
    提取翻译内容
    """
    content = scrapy.Field()  # div.shileft
    youorno = scrapy.Field()  # div.youorno
    fanyi_url = scrapy.Field()


class AuthorItem(scrapy.Item):
    """
    通过author介绍链接 http://so.gushiwen.org/author_247.aspx
    提取作者介绍概况（正文），奇闻异事（fanyi）url  /ziliao_123.apsx
    """
    author_profile = scrapy.Field()  # div.shileft div.son2 同正文处理部分
    author_intro_list = scrapy.Field()  # div.son5 同翻译部分
    author_name = scrapy.Field()
    author_url = scrapy.Field()
