# _*_ coding:utf8 _*_

from scrapy_redis.spiders import RedisSpider
from GushiwenSpider.items import AuthorItem
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess


class AuthorSpider(RedisSpider):
    """
    处理作者介绍部分
    作者简介与作品正文处理方式相同
    作者生平事迹等与作品翻译处理方式相同
    """
    name = 'author_spider'
    redis_key = 'author:start_urls'
    custom_settings = {
        'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",
        'ITEM_PIPELINES': {
            'GushiwenSpider.pipelines.ParseAuthorPipeline': 300,
        },
    }

    def parse(self, response):
        ld = ItemLoader(item=AuthorItem(), response=response)
        ld.add_css('author_profile', 'div.shileft div.son2')
        ld.add_css('author_intro_list', 'div.son5')
        # ld.add_xpath('author_name', '//div[@class="shileft"]/div[@class="son1"]/h1/text()')
        ld.add_value('author_url', response.url)
        return ld.load_item()


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(AuthorSpider)
    process.start()
