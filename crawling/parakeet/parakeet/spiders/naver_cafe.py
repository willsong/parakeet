# -*- coding: utf-8 -*-

import scrapy
from parakeet.items import CafePostItem
from HTMLParser import HTMLParser
import json

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

class NaverCafeSpider(scrapy.Spider):
    search_url = 'http://section.cafe.naver.com/ArticleSearchAjax.nhn'
    name = 'naver_cafe'
    allowed_domains = ['naver.com']
    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }
    start_urls = []
    post_count = 0
    page = 1

    '''
    def __init__(self, *args, **kwargs):
        self.start_urls = [self.get_query_url()]
        super(NaverCafeSpider, self).__init__(*args, **kwargs)
    '''

    def start_requests(self):
        form_data = self.get_query_data()
        return [scrapy.FormRequest(self.search_url, formdata = form_data, callback = self.parse)]

    def get_query_data(self):
        form_data = {
            'query': '빅데이터',
            'sortBy': '1',
            'menuType': '0',
            'searchBy': '0',
            'duplicate': 'false',
            'inCafe': '',
            'withOutCafe': '',
            'includeAll': '',
            'exclude': '',
            'include': '',
            'exact': '',
            'page': str(self.page)
        }
        print '------------------------------- PAGE %s' % self.page
        self.page += 1

        return form_data

    def parse(self, response):
        data = json.loads(response.body, strict = False)
        #posts = response.xpath('//ul[@id="ArticleSearchResultArea"]/li')

        if not data or not len(data):
            return

        if not data['isSuccess']:
            return

        res_meta = data['result']['pageInfo']
        num_posts = res_meta['totalCount']

        for p in data['result']['searchList']:
            post_title = p['articletitle']
            cafe_name = p['clubname']
            post_url = 'http://cafe.naver.com/%s/%s' % (p['cluburl'], p['articleid'])

            post_item = CafePostItem()
            post_item['src'] = 'Naver'.encode('utf-8')
            post_item['cafe_name'] = cafe_name.encode('utf-8')
            post_item['title'] = post_title.encode('utf-8')
            post_item['url'] = post_url.encode('utf-8')

            req = scrapy.Request(post_url, callback = self._parse_post)
            req.meta['post_item'] = post_item
            yield req

            self.post_count += 1
            return

        if self.post_count >= num_posts:
            return

        '''
        form_data = self.get_query_data()
        yield scrapy.FormRequest(self.search_url, formdata = form_data, callback = self.parse)
        '''

    def _parse_post(self, response):
        iframe = response.xpath('//iframe[@id="cafe_main"]/following-sibling::script/text()')
        iframe_url = iframe.re_first(r'src = \"(.*?)\"')

        req = scrapy.Request(iframe_url, callback = self._parse_post2)
        req.meta['post_item'] = response.meta['post_item']

        yield req

    def _parse_post2(self, response):

        print response.body

        '''
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
        '''
