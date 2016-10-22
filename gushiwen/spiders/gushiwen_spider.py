# _*_ coding:utf8 _*_

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from GushiwenSpider.items import GushiwenItem
from scrapy.loader import ItemLoader
import defines


class GushiwenSpider(CrawlSpider):
    """
    爬取古诗文网（so.gushiwen.org），提取出文章内容、翻译、作者介绍保存到本地或者数据库
    本程序为主程序，负责提取作品的URL，分朝代写入redis队列中。
    爬虫执行顺序：
        gushiwen --> view_spider --> author_spider --> fanyi_spider
    如果需要保存到本地再执行save脚本
    """
    name = 'gushiwen'
    allowed_domains = ['gushiwen.org']
    start_urls = defines.start_urls
    allowed_urls = defines.allowed_urls

    rules = (
        # 提取下一页链接,页面下方pages类中为小写字母。提取页面顺序：1、2、3、4、5....
        Rule(LinkExtractor(allow=allowed_urls, deny='.*baidu\.com'), callback='extract_view_urls', follow=True),
    )

    custom_settings = {
        "ITEM_PIPELINES": {
            'GushiwenSpider.pipelines.GushiwenPipeline': 300
        },
    }

    def extract_view_urls(self, response):
        itemld = ItemLoader(item=GushiwenItem(), response=response)
        itemld.add_xpath('view_urls', '//div[@class="typeleft"]/div[@class="sons"]/p[1]/a/@href')
        return itemld.load_item()

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(GushiwenSpider)
    process.start()
