# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.selector import Selector
from w3lib.html import remove_tags
from _mysql_exceptions import IntegrityError
import MySQLdb
import redis
import re


# 定义公用变量
rooturl = 'http://so.gushiwen.org'
# 数据库表结构见 数据库表结构.xlsx
conn = MySQLdb.connect(
            host='192.168.154.135',
            port=3306,
            user='gushiwen',
            passwd='gushiwen',
            db='gushiwen',
            charset='utf8',
        )
cur = conn.cursor()
# redis
rds = redis.Redis(host='localhost', port=6379, db=0)

class GushiwenPipeline(object):
    """
    从http://so.gushiwen.org/type.aspx?p=1&c=唐代 提取作品链接(view_123.aspx)
    存入redis队列
    """

    def process_item(self, item, spider):
        if item['view_urls']:
            # print item['view_urls']
            # 列表不为空
            for it in item['view_urls']:
                url = 'http://so.gushiwen.org' + it
                rds.lpush('view:start_urls', url)


class ParseViewPipeline(object):

    def process_item(self, item, spider):
        """
        提取:
        1、作品名
        2、朝代
        3、作者
        4、正文部分 div.shileft div.son2，送入数据库。view_7722Z;content
        5、翻译、赏析链接,送入redis队列。有作者时需剔除底部的作者介绍链接. tangdai:fanyi:start_urls
        6、作者介绍链接，送入redis队列。tangdai:author:start_urls
        7、提取评分及评分人数，作为进一步分析用
        """

        # 部分的作品名中含有‘/’，如 梅花/梅 在建立文件时会报错，替换为空格
        poetry_name = item['poetry_name'][0].replace('/', ' ')
        poetry_link = item['poetry_link'][0]
        view_pa = 'http://so.gushiwen.org/(.*?).aspx.*'
        view_num = re.match(view_pa, poetry_link).groups()[0]  # view_7722
        rds.lpush('view_num', view_num)
        poetry_dynasty = item['poetry_dynasty'][0]
        # 处理评分及人数
        pingfen = item['pingfen'][0]
        grade, grade_popus = extract_grade(pingfen)

        # 每个parse_view一个dict_list，用于调整翻译输出的顺序
        """
        区分有无作者
        有作者的话在 div.shileft div.son2 p a 的文本为作者名
        无作者的话在 div.shileft div.son2 p 第二个标签为 佚名或者孟子及其弟子等
        """

        shileft_son2 = item['shileft_son2'][0]  # list , len=1
        shileft_son2_sel = Selector(text=shileft_son2)
        # 提取正文，写入数据库
        poetry_mainbody = extract_poetry_mainbody(shileft_son2)

        sqli = 'insert into main_content values(%s,%s)'
        cur.execute(sqli, (view_num, poetry_mainbody))
        # 提取view_num, view_link, dynasty, view_name. maint_content等内容写入数据
        sqli = 'insert into view ' \
               '(view_num,view_link,dynasty,view_name,main_content,grade,grade_popus)' \
               'values (%s,%s,%s,%s,%s,%s,%s)'
        values = (view_num.encode('utf8'), poetry_link.encode('utf8'),poetry_dynasty.encode('utf8'),
                  poetry_name.encode('utf8'), view_num.encode('utf8'), grade, grade_popus)
        cur.execute(sqli, values)

        try:
            # 部分作品没有翻译
            div_son5 = item['div_son5']  # list
            if shileft_son2_sel.css('p a'):
                # 处理有作者的情况
                # 没有作者介绍的都当作没有作者，归为佚名
                author_name = shileft_son2_sel.css('a::text').extract()[0]
                author_intro_link = shileft_son2_sel.css('a::attr(href)').extract()[0]  # /author_600.aspx
                author_num = re.match('/(.*?).aspx', author_intro_link).groups()[0]
                author_intro_link = rooturl + author_intro_link
                poetry_fanyi_list = lpush_fanyi_url(div_son5[:-1])
                try:
                    #  处理author内容入库， author_247, 作者名、朝代
                    #  一个作者有N篇文章，只能插入一次
                    sqli = 'insert into author (author_num,author_name,dynasty) values(%s,%s,%s)'
                    cur.execute(sqli, (author_num, author_name, poetry_dynasty))
                    # 重复操作会收到数据库返回的错误，不会再次lpush author：start_urls
                    rds.lpush('author:start_urls', author_intro_link)
                except IntegrityError:
                    pass
            else:
                # 没有作者又分两种情况，一种是佚名，另一种是“孟子及其弟子”,都没有作者介绍
                try:
                    author_name = shileft_son2_sel.xpath('p[2]/text()').extract()[0]
                except IndexError:
                    author_name = u'佚名'
                poetry_fanyi_list = lpush_fanyi_url(div_son5)

            fanyi_list = ','.join(poetry_fanyi_list)
            fanyi_list = fanyi_list.replace('http://so.gushiwen.org/', '').replace('.aspx', '')
            sqli = 'update view  set author_name=%s,fanyi_list=%s where view_num=%s'
            cur.execute(sqli, (author_name.encode('utf8'), fanyi_list.encode('utf8'), view_num.encode('utf8')))
        except KeyError:
            pass


class ParseFanyiPipeline(object):
    """
    只处理翻译部分，获取翻译URL，存入数据库
    fanyi_967:content
    """

    def process_item(self, item, spider):
        content = item['content'][0]
        youorno = item['youorno'][0]
        # youorno 为页面下方投票翻译、介绍是否有用，剔除这一部分
        nouse = u'本页内容整理自网络（或由匿名网友上传），原作者已无法考证，版权归原作者所有。' \
                u'本站免费发布仅供学习参考，其观点不代表本站立场。站务邮箱：service@gushiwen.org'
        nouse2 = '(adsbygoogle=window.adsbygoogle||[]).push({});'
        extract_content = content.replace(youorno, '').replace('<br>', '\n')
        extract_content_text = remove_tags(extract_content) # u''
        extract_content_text = extract_content_text.replace(' ', '') .replace(nouse, '').replace(nouse2, '')
        # 删掉多余的换行符
        extract_content_text = remove_needless_sysmbols(extract_content_text)
        fanyi_url = item['fanyi_url'][0]  # http://so.gushiwen.org/fanyi_967.aspx
        fanyi_pa = 'http://so.gushiwen.org/(.*?).aspx.*'
        fanyi_num = re.match(fanyi_pa, fanyi_url).groups()[0]  # view_7722
        # self.insert_mysql(url=response.url, cont=extract_content_text.encode('utf8'))
        sqli = 'insert into fanyi values(%s,%s)'
        cur.execute(sqli, (fanyi_num.encode('utf8'), extract_content_text))


class ParseAuthorPipeline(object):
    """
    只处理作者介绍部分，获取作者介绍URL，提取内容存入数据库
    author_247:content
    """

    def process_item(self, item, spider):
        author_url = item['author_url'][0]
        author_pa = 'http://so.gushiwen.org/(.*?).aspx.*'
        author_num = re.match(author_pa, author_url).groups()[0]  #  author_247
        rds.lpush('author_num', author_num)
        # 处理正文部分，同处理作品正文一致
        author_profile = item['author_profile'][0]
        author_profile_text = remove_tags(author_profile, which_ones=('div', 'a', 'span', 'p'))
        mainbody_text = author_profile_text.replace(' ', '').replace('\n', '', 16).replace('<br>', '\n')
        mainbody_text = remove_needless_sysmbols(mainbody_text)
        try:
            sqli = 'insert into main_content values(%s,%s)'
            cur.execute(sqli, (author_num, mainbody_text))
        except IntegrityError:
            pass

        # 处理作者资料介绍，同作品翻译一致
        try:
            author_intro_list = item['author_intro_list']
            poetry_fanyi_list = lpush_fanyi_url(author_intro_list)
            fanyi_list = ','.join(poetry_fanyi_list)
            fanyi_list = fanyi_list.replace('http://so.gushiwen.org/', '').replace('.aspx', '')
            sqli = 'update author ' \
                   'set author_link=%s,main_content=%s,fanyi_list=%s' \
                   'where author_num=%s'
            values = (
            author_url.encode('utf8'), author_num.encode('utf8'), fanyi_list.encode('utf8'), author_num.encode('utf8'))
            cur.execute(sqli, values)
        except KeyError:
            pass



"""
定义公用方法
"""

# 文本处理方法
def extract_poetry_mainbody(text):
    """
    调用w3lib.html.remove_tags()处理正文
    部分作品的文本内容放在了p标签外面，div.son2内，通过<br>分隔
    <br>标签不是完整标签，在remove_tags()函数中会被去掉，无法通过keep保留
    先remove其他标签（div，a，span，p...） 再用'\n'替换<br>
    """
    mainbody_text = remove_tags(text=text, which_ones=('div', 'a', 'span', 'p'))
    mainbody_text = mainbody_text.replace(' ', '').replace('\n', '', 16).replace('<br>', '\n')
    # mainbody_text = remove_needless_sysmbols(mainbody_text)
    return mainbody_text

def remove_needless_sysmbols(text):
    # 删除多余的符号
    text = text.replace('\r\n', '\r')
    for sysmbol in ['\r', '\n']:
        double_sysmbols = sysmbol * 2
        while double_sysmbols in text:
            text = text.replace(double_sysmbols, sysmbol)
        return text

def lpush_fanyi_url(div_son5):
    """
    从div_son5原始数据中提取出翻译、赏析链接(/fanyi_123.aspx)
    送入redis队列
    """
    poetry_fanyi_list = []
    for p_a_href in div_son5:
        p_a_href_selector = Selector(text=p_a_href)
        a_href = p_a_href_selector.xpath('//p[1]/a/@href').extract()[0]
        fanyi_url = rooturl + a_href
        poetry_fanyi_list.append(fanyi_url)
        rds.lpush('fanyi:start_urls', fanyi_url)
    return poetry_fanyi_list

def insert_mysql(self, table=None, key=None, value=None):
    sqli = "insert into (%s) values(%s,%s)"
    cur.execute(sqli, (table, key, value))

def extract_grade(pingfen):

    # 评分人数不足的以0分和0人处理
    if u'评分人数不足' in pingfen:
        grade = 0
        grade_popus = 0
    else:
        pingfen_raw = remove_tags(pingfen).split()
        grade_popus = int(pingfen_raw[0][1:-4])  # 31397
        grade = float(pingfen_raw[1])  # 8.5

    return grade, grade_popus

