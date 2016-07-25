# -*- coding: utf-8 -*-

import scrapy
from parakeet.items import BlogPostItem, BlogCommentItem
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class NaverBlogSpider(scrapy.Spider):
    name = 'naver_blog'
    allowed_domains = ['naver.com']
    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }
    start_urls = []
    page = 1
    post_count = 0

    search_term = '박유천'
    start_date = '2016-01-01'
    end_date = '2016-07-25'

    def __init__(self, *args, **kwargs):
        self.start_urls = [self.get_query_url()]
        super(NaverBlogSpider, self).__init__(*args, **kwargs)

    def get_query_url(self):
        print '------------------------------- PAGE %s' % self.page
        url = 'http://section.blog.naver.com/sub/SearchBlog.nhn?type=post&option.keyword=%s&term=period&option.startDate=%s&option.endDate=%s&option.page.currentPage=%s&option.orderBy=date' % (self.search_term, self.start_date, self.end_date, self.page)
        self.page += 1
        return url

    def get_comment_url(self, blog_id, post_no, page):
        url = 'http://blog.naver.com/CommentList.nhn?blogId=%s&logNo=%s&currentPage=%s' % (blog_id, post_no, page)
        return url

    def parse(self, response):
        posts = response.xpath('//ul[contains(@class, "search_list")]/li')
        if not len(posts): return

        # get total results
        res_meta = response.xpath('//p[@class="several_post"]/em/text()')
        num_posts = res_meta.re_first(r'^(\d+)')

        for p in posts:
            url = p.xpath('./h5/a/@href')
            post_title = p.xpath('./h5/a/text()').extract()[0]
            post_date = p.xpath('./div[@class="list_data"]/span[@class="date"]/text()').extract()[0]

            user_id = ''
            post_id = ''
            if url.re_first(r'^http:\/\/blog\.naver\.com\/'):
                user_id = url.re_first(r'^http:\/\/blog\.naver\.com\/(.*?)\?')
                post_id = url.re_first(r'^http:\/\/blog\.naver\.com\/.*?logNo=(.*?)&')
            elif url.re_first(r'blog\.me'):
                user_id = url.re_first(r'^http:\/\/(.*?)\.blog\.me')
                post_id = url.re_first(r'^http:\/\/.*?\.blog\.me\/(.*?)$')

            post_url = 'http://blog.naver.com/PostView.nhn?blogId=%s&logNo=%s' % (user_id, post_id)

            post_item = BlogPostItem()
            post_item['a_date'] = post_date.encode('utf-8')
            post_item['b_blog_id'] = user_id.encode('utf-8')
            post_item['c_post_no'] = post_id.encode('utf-8')
            post_item['d_url'] = post_url.encode('utf-8')
            post_item['e_src'] = 'Naver'.encode('utf-8')
            post_item['f_title'] = post_title.encode('utf-8')

            req = scrapy.Request(post_url, callback = self._parse_post)
            req.meta['post_item'] = post_item
            yield req

            self.post_count += 1

        if self.post_count >= num_posts:
            return
        if self.page >= 399:
            return

        next_page_url = self.get_query_url();
        yield scrapy.Request(next_page_url, callback = self.parse)

    def _parse_post(self, response):
        post_item = response.meta['post_item']

        post_body = response.xpath('//div[@id="postViewArea"]//div[@class="view"]/*')
        post_body_str = []
        if len(post_body):
            for body_part in post_body:
                post_body_str.append(body_part.extract())
        else:
            post_body = response.xpath('//div[@id="postViewArea"]//div[contains(@class, "post-view")]/*')
            if len(post_body):
                for body_part in post_body:
                    post_body_str.append(body_part.extract())

        post_item['g_body'] = strip_tags(''.join(post_body_str)).replace("\n", '').replace("\r\n", '').replace("\r", '').encode('utf-8')

        yield post_item

        # comments
        comment_text = response.xpath('//a[contains(@class, "_cmtList")]/text()')
        if len(comment_text):
            num_comments = comment_text.re_first(r'(\d+)$')
            if num_comments:
                print '---------- COUNT COMMENTS: %s postid: %s' % (num_comments, post_item['c_post_no'])
                comment_url = self.get_comment_url(post_item['b_blog_id'], post_item['c_post_no'], 1)
                req = scrapy.Request(comment_url, callback = self._parse_comments)
                req.meta['post_item'] = post_item
                req.meta['comment_page_no'] = 1

                yield req

    def _parse_comments(self, response):
        post_item = response.meta['post_item']
        comment_page_no = response.meta['comment_page_no']

        if comment_page_no == 1:
            yield post_item

        comment_list = response.xpath('//ul[@id="commentList"]//li[contains(@class, "_countableComment")]')
        comment_nav = response.xpath('//div[contains(@class, "cc_paginate")]')
        print 'NUM COMMENTS: %s PAGE: %s SHITE: %s postid: %s' % (len(comment_list), comment_page_no, len(comment_nav), post_item['c_post_no'])

        for c in comment_list:
            user_name = c.xpath('//dt[contains(@class, "h")]//a[contains(@class, "nick")]')

            if len(user_name):
                user_name = c.xpath('//dt[contains(@class, "h")]//a[contains(@class, "nick")]/text()').extract()[0]
                comment_date = c.xpath('//dt[contains(@class, "h")]//span[contains(@class, "date")]/text()').extract()[0]
                comment_body = c.xpath('//dd[contains(@class, "comm")]/text()').extract()[0]

                print 'COMMENT USERNAME: %s date: %s body: %s' % (user_name, comment_date, comment_body)

            '''
            comment_item = BlogCommentItem()
            comment_item['a_post_no'] = post_item['c_post_no']
            comment_item['b_blog_id'] = post_item['b_blog_id']
            comment_item['c_user_name'] = post_item['c_post_no']
            comment_item['d_date'] = post_item['c_post_no']
            comment_item['e_body'] = post_item['c_post_no']
            '''

        if len(comment_list) and len(comment_nav):
            comment_url = self.get_comment_url(post_item['b_blog_id'], post_item['c_post_no'], comment_page_no + 1)
            req = scrapy.Request(comment_url, callback = self._parse_comments)
            req.meta['post_item'] = post_item
            req.meta['comment_page_no'] = comment_page_no + 1
            yield req

