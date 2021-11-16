# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Comment(scrapy.Item):
    User = scrapy.Field()
    Comment = scrapy.Field()
    Time = scrapy.Field()


class CrawlerItem(scrapy.Item):
    STT = scrapy.Field()
    URL = scrapy.Field()
    TenSanPham = scrapy.Field()
    GiaTien = scrapy.Field()
    ChuyenMuc = scrapy.Field()
    ChitietSanPham = scrapy.Field()
    Nhanxet = scrapy.Field()
