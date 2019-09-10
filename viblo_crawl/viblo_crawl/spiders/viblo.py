#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import scrapy
import calendar
import datetime
import json
import re

from scrapy.spiders import CrawlSpider
from ..items import VibloPostsItem
    
class VibloSpider(CrawlSpider):
    name = 'viblo'
    allowed_domains = ['https://viblo.asia'] #1
    start_urls = []

    start_urls.append('https://viblo.asia/p/ban-ve-js-arrow-function-3Q75wGRe5Wb') #2
    # start_urls.append('https://viblo.asia/p/dependency-injection-with-dagger-2-trong-android-phan-2-bJzKmjmYZ9N')
    # start_urls.append('https://viblo.asia/p/a-complete-guide-to-flexbox-phan-1-Qbq5QkXmZD8')

    def parse_related(self, response):
        same_objs = ['sameAuthor', 'sameTags', 'sameContentPosts']
        json_response = json.loads(response.body_as_unicode())
        for obj_name in same_objs:
            new_items = json_response[obj_name]['data']
            for item in new_items:
                yield scrapy.Request(item['url'], dont_filter=True)
        
        
    def parse(self, response): #3
        viblo_post = VibloPostsItem()
        data_resp = scrapy.Selector(response)
        # new request for related link
        post_id = response.url.split('-')[-1]
        yield scrapy.http.JSONRequest("https://viblo.asia/api/posts/%s/related" % post_id, callback=self.parse_related, dont_filter=True)
        
            #yield scrapy.Request(response.urljoin(href), self.parse)
        #yield scrapy.Request("https://viblo.asia/p/crawl-du-lieu-trang-web-voi-scrapy-E375zWr1KGW", callback=self.parse)
        viblo_post['url'] = response.request.url
        viblo_post['author'] = data_resp.xpath("//a[contains(@class, 'post-author__name')]/text()").extract_first().strip()
        viblo_post['title'] = data_resp.xpath("//h1[contains(@class, 'article-content__title')]/text()").extract_first().strip()
        
        viblo_post['content'] = ''
        for i in data_resp.xpath("//div[contains(@class, 'article-content__body')]/*[self::div or self::p or self::h1 or self::h2 or self::h3]/text()"):
            viblo_post['content']  += i.extract() +  " "
        
        viblo_post['tags'] = [i.strip() for i in data_resp.xpath("//div[@class='tags']/a/text()").extract()]
                
        viblo_post['created'] = data_resp.xpath("//header//div[contains(@class, 'post-meta')]/div/text()").extract_first().replace("Published", '').strip()
        viblo_post['created'] = self.parse_date(viblo_post['created'])
        
        yield viblo_post #6
        
     
    def parse_date(self, date):
        result = re.sub('\d+(st|nd|rd|th)', lambda m: m.group()[:-2].zfill(2), date)
        try:
            result = datetime.datetime.strptime(result, '%b %d, %Y %I:%M %p')
        except ValueError:
            result = datetime.datetime.strptime(result, '%b %d, %I:%M %p').replace(year = datetime.datetime.now().year)
        return result.strftime('%Y-%m-%dT%H:%M:%SZ')