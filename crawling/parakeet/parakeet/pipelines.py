# -*- coding: utf-8 -*-

from scrapy import signals
from scrapy.exporters import CsvItemExporter
from scrapy.xlib.pydispatch import dispatcher

def item_type(item):
    return type(item).__name__.replace('Item', '').lower()

class ParakeetPipeline(object):

    save_types = ['blogpost', 'blogcomment']
    csv_dir = '/tmp/csv/'

    def __init__(self):
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_opened(self, spider):
        self.files = dict([ (name, open(self.csv_dir + name + '.csv', 'w+b')) for name in self.save_types ])
        self.exporters = dict([ (name, CsvItemExporter(self.files[name])) for name in self.save_types])
        [e.start_exporting() for e in self.exporters.values()]

    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        what = item_type(item)
        if what in set(self.save_types):
            self.exporters[what].export_item(item)
        return item
