# _*_ coding:utf8 _*_

from scrapy import Selector,Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import os
import MySQLdb
from w3lib.html import remove_tags
from scrapy.crawler import CrawlerProcess

"""
爬取古诗文网（so.gushiwen.org），提取出文章内容、翻译、作者介绍先保存到数据库，再提取出来保存到本地。
因为SCrapy调度机制的问题，访问链接不会按照给定的顺序，因此需要完全入库之后再按照顺序提取保存在本地。
"""


class GushiwenSpider(CrawlSpider):

    """
    以朝代为线索，分别爬取十二个朝代的所有文章
    """
    def __init__(self, *a, **kw):
        # 为什么初始化函数继承超类按照如下格式写？
        super(GushiwenSpider, self).__init__(*a, **kw)
        self.rooturl = 'http://so.gushiwen.org'
        self.conn = MySQLdb.connect(
            host='192.168.154.133',
            port=3306,
            user='gushiwen',
            passwd='gushiwen',
            db='test',
            charset='utf8',
        )
        self.cur = self.conn.cursor()
        self.error_url_file = open('errorUrl.txt', 'a')

    name = 'gushiwen'
    allowed_domains = ['gushiwen.org']
    start_urls = [
                  'http://so.gushiwen.org/type.aspx?p=1&c=先秦',
                  'http://so.gushiwen.org/type.aspx?p=1&c=两汉',
                  'http://so.gushiwen.org/type.aspx?p=1&c=魏晋',
                  'http://so.gushiwen.org/type.aspx?p=1&c=南北朝',
                  'http://so.gushiwen.org/type.aspx?p=1&c=隋代',
                  'http://so.gushiwen.org/type.aspx?p=1&c=唐代',
                  'http://so.gushiwen.org/type.aspx?p=1&c=五代',
                  'http://so.gushiwen.org/type.aspx?p=1&c=宋代',
                  'http://so.gushiwen.org/type.aspx?p=1&c=金朝',
                  'http://so.gushiwen.org/type.aspx?p=1&c=元代',
                  'http://so.gushiwen.org/type.aspx?p=1&c=明代',
                  'http://so.gushiwen.org/type.aspx?p=1&c=清代',
                  ]
    allowed_urls = [
                     'type\.aspx\?p\=[0-9]*&c=%e5%85%88%e7%a7%a6$',
                    'type\.aspx\?p\=[0-9]*&c=%e4%b8%a4%e6%b1%89$',
                    'type\.aspx\?p\=[0-9]*&c=%e9%ad%8f%e6%99%8b$',
                    'type\.aspx\?p\=[0-9]*&c=%e5%8d%97%e5%8c%97%e6%9c%9d$',
                    'type\.aspx\?p\=[0-9]*&c=%e9%9a%8b%e4%bb%a3$',
                    'type\.aspx\?p\=[0-9]*&c=%e5%94%90%e4%bb%a3$',
                    'type\.aspx\?p\=[0-9]*&c=%e4%ba%94%e4%bb%a3$',
                    'type\.aspx\?p\=[0-9]*&c=%e5%ae%8b%e4%bb%a3$',
                    'type\.aspx\?p\=[0-9]*&c=%e9%87%91%e6%9c%9d$',
                    'type\.aspx\?p\=[0-9]*&c=%e5%85%83%e4%bb%a3$',
                    'type\.aspx\?p\=[0-9]*&c=%e6%98%8e%e4%bb%a3$',
                    'type\.aspx\?p\=[0-9]*&c=%e6%b8%85%e4%bb%a3$',
                  ]

    rules = (

        # 以作品页为主线，提取view页面的正文，通过再次访问正文中的链接提取出翻译、作者介绍
        Rule(LinkExtractor(allow='/view_[0-9]*\.aspx', deny='.*baidu\.com'), callback='parse_view', follow=True),
        # 提取下一页链接,页面中为小写字母，只能匹配小写字母
        Rule(LinkExtractor(allow=allowed_urls, deny='.*baidu\.com'), callback='parse_next', follow=True),
    )

    def parse_view(self, response):

        """
        提取文章内容
        1、作品名
        2、朝代
        3、作者（包括作者介绍链接，作为参数传递给parse_author
        4、正文部分 div.shileft div.son2
        5、翻译、赏析部分在 div.son5，需剔除底部的作者介绍(有作者的情况下)
        6、处理评分，作为进一步分析用，预留接口
        """
        # 部分的作品名中含有‘/’，如 梅花/梅 在建立文件时会报错，替换为空格
        poetry_name_css = response.css('div.main3 div.shileft div.son1 h1::text').extract()[0]
        poetry_name = poetry_name_css.replace('/', ' ')
        poetry_link = response.url
        poetry_dynasty = response.css('div.shileft div.son2 p::text').extract()[0]
        # 每个parse_view一个dict_list，用于调整翻译的顺序
        dict_list = {}
        dict_list[response.url] = []

        # 区分有无作者
        # 有作者的话在 div.shileft div.son2 p a 的文本为作者名
        # 无作者的话在 div.shileft div.son2 p 第二个标签为 佚名或者孟子及其弟子等
        shileft_son2 = response.css('div.shileft div.son2')
        div_son5 = response.css('div.son5').extract()
        if shileft_son2.css('p a'):
            # 处理有作者的情况
            author_name = shileft_son2.css('a::text').extract()[0]
            author_path = poetry_dynasty + '\\' + author_name
            author_intro_link = shileft_son2.css('a::attr(href)').extract()[0]
            author_intro_file_path = poetry_dynasty + '\\' + author_name + '\\' + author_name + u'简介.txt'
            author_flag = 1
            poetry_fanyi_list = div_son5[:-1]
            author_dic = dict(author_name=author_name, author_path=author_path,
                              author_intro_link=author_intro_link, author_intro_file_path=author_intro_file_path,
                              author_flag=author_flag,
                              )
        else:
            # 没有作者又分两种情况，一种是佚名，另一种是“孟子及其弟子”,都没有作者介绍
            author_name = shileft_son2.xpath('p[2]/text()').extract()[0]
            author_path = poetry_dynasty + '\\' + author_name
            author_flag = 0
            poetry_fanyi_list = div_son5
            author_dic = dict(author_name=author_name, author_path=author_path, author_flag=author_flag, )

        if not os.path.exists(author_path):
            # 递归创建分级目录
            os.makedirs(author_path)
        poetry_path = author_path + '\\' + poetry_name + '.txt'
        file_poetry = open(poetry_path, 'a')
        poetry_dic = dict(poetry_name=poetry_name, poetry_link=poetry_link,
                          poetry_dynasty=poetry_dynasty, poetry_file=file_poetry,
                          poetry_fanyi_list=poetry_fanyi_list)

        # 提取正文部分，写入文件
        poetry_mainbody_meta_content = shileft_son2.extract()[0]
        self.parse_poetry_mainbody(poetry_file=file_poetry,
                                   poetry_dic=poetry_dic,
                                   meta_content=poetry_mainbody_meta_content,
                                   )
        # 提取翻译部分，写入文件
        self.parse_fanyi(son5_list=poetry_fanyi_list, file_poetry=file_poetry)

        # 提取作者介绍，写入文件，每个作者只提取一次
        if author_flag:
            if not os.path.exists(author_intro_file_path):
                # 首次提取内容，建立文件，文章结构与无作者的文章结构基本一致，可大量复用代码
                file_author_intro = open(author_intro_file_path, 'a')
                author_intro_url = self.rooturl + author_dic['author_intro_link']
                rqst = Request(url=author_intro_url, callback=self.parse_author_intro)
                rqst.meta['file_author_intro'] = file_author_intro
                yield rqst

    def parse_poetry_mainbody(self, poetry_file=None, poetry_dic=None, meta_content=None):
        poetry_file.write(poetry_dic['poetry_name'].encode('utf8') + '\n' + '原文链接：' + poetry_dic['poetry_link'] + '\n')
        # 调用w3lib.html.remove_tags()处理正文
        # 部分作品的文本内容放在了p标签外面，div.son2内，通过<br>分隔
        # <br>标签不是完整标签，在remove_tags()函数中会被去掉，无法通过keep保留
        #  先remove其他标签（div，a，span，p...） 再用'\n'替换<br>， 注意顺序
        mainbody_text = remove_tags(meta_content, which_ones=('div', 'a', 'span', 'p')).encode('utf8')
        mainbody_text = mainbody_text.replace(' ', '').replace('\n', '', 16).replace('<br>', '\n')
        mainbody_text = self.remove_needless_sysmbols(text=mainbody_text)
        poetry_file.write(mainbody_text + '\n')
        poetry_file.flush()

    def parse_fanyi(self, son5_list=None, file_poetry=None):
        # 翻译、赏析、作者介绍格式一致，传入url 列表和文件对象分别进行处理
        # shell 结合debug log 查看list url 顺序,排查顺序错乱的原因
        list_fanyi_url = []
        for p_a_href in son5_list:
            p_a_href_selector = Selector(text=p_a_href)
            a_href = p_a_href_selector.xpath('//p[1]/a/@href').extract()[0]
            fanyi_url = self.rooturl + a_href
            list_fanyi_url.append(fanyi_url)
        # 入库
        for fanyi_url in list_fanyi_url:
            rqst = Request(url=fanyi_url, callback=self.extract_son5_href)
            yield rqst

        # 从数据库中提取出来，写入文件
        for url in list_fanyi_url:
            cur = self.cur
            sqls = "select * from gushiwen where url=(%s)"
            cur.execute(sqls, (url))
            try:
                fc = cur.fetchone()
                cont = fc[1]
                file_poetry.write(cont.encode('utf8') + '\n')
                file_poetry.flush()
            except TypeError:
                self.error_url_file.write(url + '===>' + list_fanyi_url[0] + '\n')
                self.error_url_file.flush()

    def extract_son5_href(self, response):
        # 从href请求的响应中提取内容，写入数据库
        content = response.css('div.shileft').extract()[0]
        youorno = response.css('div.youorno').extract()[0]
        # youorno 为页面下方投票翻译、介绍是否有用，剔除这一部分
        extract_content = content.replace(youorno, '').replace('<br>', '\n')
        extract_content_text = remove_tags(extract_content).replace(' ', '')
        # 删掉多余的换行符
        extract_content_text = self.remove_needless_sysmbols(text=extract_content_text)
        self.insert_mysql(url=response.url, cont=extract_content_text.encode('utf8'))

    def remove_needless_sysmbols(self, text=''):
        """
        删除多余的符号，默认删除多余的'\n'
        sysmbol参数为要删掉的符号
        """
        text = text.replace('\r\n', '\r')
        for sysmbol in ['\r', '\n']:
            double_sysmbols = sysmbol * 2
            while double_sysmbols in text:
                text = text.replace(double_sysmbols, sysmbol)
        return text

    def parse_author_intro(self, response):

        # 处理第一段内容，复用parse_poetry_mainbody代码
        author_profile = response.css('div.shileft div.son2').extract()[0]
        author_profile_text = remove_tags(author_profile, which_ones=('div', 'a', 'span', 'p')).encode('utf8')
        mainbody_text = author_profile_text.replace(' ', '').replace('\n', '', 16).replace('<br>', '\n')
        mainbody_text = self.remove_needless_sysmbols(text=mainbody_text)
        file_author_intro = response.meta['file_author_intro']
        file_author_intro.write(mainbody_text + '\n')
        file_author_intro.flush()
        # 余下的内容与处理翻译内容一致，复用代码
        part_author_intro_list = response.css('div.son5').extract()
        self.parse_fanyi(son5_list=part_author_intro_list, file_poetry=file_author_intro)

    def parse_next(self, response):
        # follow等于True，此行甚至可以pass
        print response.url

    def insert_mysql(self, url=None, cont=None):
        sqli = "insert into gushiwen values(%s,%s)"
        self.cur.execute(sqli,(url,cont))
process = CrawlerProcess()
process.crawl(GushiwenSpider)
process.start()
