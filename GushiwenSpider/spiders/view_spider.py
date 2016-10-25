# _*_ coding:utf8 _*_

from scrapy_redis.spiders import RedisSpider
from scrapy.loader import ItemLoader
from GushiwenSpider.items import ViewItem
from scrapy.crawler import CrawlerProcess


class ViewSdier(RedisSpider):
    """
    提取View页面主要内容：
    作品名称、作者、朝代、作品正文、翻译链接(fanyi_123.aspx, shangxi_123.aspx)、作者介绍链接(author_123.aspx)。
    链接部分提交到redis，供爬虫fanyi_spider爬取
    """
    name = 'view_spider'
    redis_key = 'view:start_urls'
    custom_settings = {
        'ITEM_PIPELINES': {
            'GushiwenSpider.pipelines.ParseViewPipeline': 300,
        },
    }

    def parse(self, response):
        view_item = ItemLoader(item=ViewItem(), response=response)
        view_item.add_css('poetry_name', 'div.main3 div.shileft div.son1 h1::text')
        view_item.add_value('poetry_link', response.url)
        view_item.add_xpath('poetry_dynasty', '//div[@class="shileft"]/div[@class="son2"]/p[1]/text()')
        view_item.add_css('shileft_son2', 'div.shileft div.son2')
        view_item.add_css('div_son5', 'div.son5')
        view_item.add_css('pingfen', 'div.pingfen div.line1')
        return view_item.load_item()

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(ViewSdier)
    process.start()
