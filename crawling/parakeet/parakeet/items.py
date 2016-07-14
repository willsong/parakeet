# -*- coding: utf-8 -*-

import scrapy


class BlogPostItem(scrapy.Item):
    src = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    body = scrapy.Field()

class CafePostItem(scrapy.Item):
    src = scrapy.Field()
    cafe_name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    body = scrapy.Field()

class BlogCommentItem(scrapy.Item):
    pass
