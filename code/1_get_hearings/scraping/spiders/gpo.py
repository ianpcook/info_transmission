# -*- coding: utf-8 -*-
import HTMLParser
import os
import scrapy
from scraping import items
from scrapy import Request
from urlparse import urlparse, urljoin


class GpoSpider(scrapy.Spider):
    name = "gpo"
    allowed_domains = ["www.gpo.gov"]
    start_urls = (
        'http://www.gpo.gov/fdsys/browse/collection.action?'
        'collectionCode=CHRG&bread=true',
    )
    parser = HTMLParser.HTMLParser()

    def __init__(self, destination='../../../data/scraped_hearings', overwrite=False):
        self.destination = os.path.abspath(destination)
        self.overwrite = overwrite == '1'

    def parse(self, response):
        for link in response.xpath(
                "//div[@id='browse-drilldown-mask']/input[@id='urlhid1']/@value"
        ).extract():
            yield Request(
                urljoin(response.url, self.parser.unescape(link)),
                callback=self.parse_l2)

    def parse_l2(self, response):
        for link in response.xpath(
                "//div[@id='browse-drilldown-mask']/input[@id='urlhid2']/@value"
        ).extract():
            yield Request(
                urljoin(response.url, self.parser.unescape(link)),
                callback=self.parse_l3)

    def parse_l3(self, response):
        for link in response.xpath(
                "//div[@id='browse-drilldown-mask']/input[@id='urlhid3']/@value"
        ).extract():
            yield Request(
                urljoin(response.url, self.parser.unescape(link)),
                callback=self.parse_hearings)

    def parse_hearings(self, response):
        for link in response.xpath(
                "//td[@class='browse-download-links']/a[text()='Text']/@href"
        ).extract():
            yield Request(
                urljoin(response.url, self.parser.unescape(link)),
                callback=self.parse_hearing_page)

    def parse_hearing_page(self, response):
        yield items.HearingItem(
            text= ''.join(response.xpath('//body//text()').extract()),
            filename=os.path.basename(
                urlparse(response.url).path).rsplit('.', 1)[0] + '.txt')
