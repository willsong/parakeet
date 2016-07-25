# -*- coding: utf-8 -*-

import scrapy


class BlogPostItem(scrapy.Item):
    a_date = scrapy.Field()
    b_blog_id = scrapy.Field()
    c_post_no = scrapy.Field()
    d_url = scrapy.Field()
    e_src = scrapy.Field()
    f_title = scrapy.Field()
    g_body = scrapy.Field()

class CafePostItem(scrapy.Item):
    src = scrapy.Field()
    cafe_name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    body = scrapy.Field()

class BlogCommentItem(scrapy.Item):
    a_post_no = scrapy.Field()
    b_blog_id = scrapy.Field()
    c_user_name = scrapy.Field()
    d_date = scrapy.Field()
    e_body = scrapy.Field()

