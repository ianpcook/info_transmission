# -*- coding: utf-8 -*-

# Scrapy settings for scraping project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
from scrapy import log

BOT_NAME = 'scraping'

SPIDER_MODULES = ['scraping.spiders']
NEWSPIDER_MODULE = 'scraping.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scraping (+http://www.yourdomain.com)'

LOG_LEVEL = log.INFO

ITEM_PIPELINES = {
    'scraping.pipelines.HearingPipeline': 500
}