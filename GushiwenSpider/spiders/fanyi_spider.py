# _*_ coding:utf8 _*_

from scrapy_redis.spiders import RedisSpider
from GushiwenSpider.items import FanyiItem
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess


class FanyiSpider(RedisSpider):
    """
    从redis队列 fanyi:start_urls
    获取链接：
        http://so.gushiwen.org/shangxi_4323.aspx
        http://so.gushiwen.org/fanyi_3024.aspx
    提取翻译正文部分，存入数据库
        fanyi_3024 content
        shangxi_4323 content
    """
    name = 'fanyi_spider'
    redis_key = 'fanyi:start_urls'
    custom_settings = {
        'ITEM_PIPELINES': {
            'GushiwenSpider.pipelines.ParseFanyiPipeline': 300,
        },
    }

    def parse(self, response):
        ld = ItemLoader(item=FanyiItem(), response=response)
        ld.add_css('content', 'div.shileft')
        ld.add_css('youorno', 'div.youorno')
        ld.add_value('fanyi_url', response.url)
        return ld.load_item()

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(FanyiSpider)
    process.start()
