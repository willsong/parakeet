# -*- coding: utf-8 -*-

from scrapy import signals
from scrapy.exporters import CsvItemExporter

class ParakeetPipeline(object):

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        _file = open('%_posts.csv' % spider.name, 'w+b')
        self.files[spider] = _file
        self.exporter = CsvItemExporter(_file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        _file = self.files.pop(spider)
        _file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
