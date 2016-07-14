# -*- coding: utf-8 -*-

import scrapy
from parakeet.items import BlogPostItem
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

    def __init__(self, *args, **kwargs):
        self.start_urls = [self.get_query_url()]
        super(NaverBlogSpider, self).__init__(*args, **kwargs)

    def get_query_url(self):
        print '------------------------------- PAGE %s' % self.page
        url = 'http://section.blog.naver.com/sub/SearchBlog.nhn?type=post&option.keyword=소비자&term=period&option.startDate=2015-01-01&option.endDate=2015-03-20&option.page.currentPage=%s&option.orderBy=date' % self.page
        self.page += 1
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
            post_item['src'] = 'Naver'.encode('utf-8')
            post_item['title'] = post_title.encode('utf-8')
            post_item['url'] = post_url.encode('utf-8')
            post_item['date'] = post_date.encode('utf-8')

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

        post_item['body'] = strip_tags(''.join(post_body_str)).replace("\n", '').replace("\r\n", '').replace("\r", '').encode('utf-8')

        yield post_item
