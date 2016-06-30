# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
from scrapy import log

class HearingPipeline(object):
    def open_spider(self, spider):
        if not os.path.exists(spider.destination):
            os.makedirs(spider.destination)
        
    def process_item(self, item, spider):
        path = os.path.join(spider.destination, item['filename'])
        if os.path.exists(path) and not spider.overwrite:
            spider.log('File exists: {}'.format(item['filename']), log.DEBUG)
        else:
            spider.log('Saving file: {}'.format(item['filename']), log.DEBUG)
            file(path, 'w').write(item['text'].encode('utf-8'))
        return item


            