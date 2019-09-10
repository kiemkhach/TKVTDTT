# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pysolr
import logging
from viblo_crawl import settings
import json


class VibloCrawlPipeline(object):
    def __init__(self):
        pysolr.ZooKeeper.CLUSTER_STATE = '/collections/viblo_posts/state.json'
        self.mapping = settings.SOLR_MAPPING.items()
        self.ignore_duplicates = settings.SOLR_IGNORE_DUPLICATES or False
        self.id_fields = settings.SOLR_DUPLICATES_KEY_FIELDS
        if self.ignore_duplicates and not self.id_fields:
            raise RuntimeError('To ignore duplicates SOLR_DUPLICATES_KEY_FIELDS has to be defined')
        zookeeper = pysolr.ZooKeeper("localhost:9983")
        self.solr = pysolr.SolrCloud(zookeeper, 'viblo_posts')
        
    
    def process_item(self, item, spider):
        if self.ignore_duplicates:
            dup_keys_values = [str(dst) + ':' + '"' + self.__get_item_value__(item, src) + '"' for dst, src in
                               self.mapping
                               if dst in self.id_fields]
            query = " ".join(dup_keys_values)
            result = self.solr.search(query)
            if len(result) != 0:
                logging.info('Skipping duplicate')
                return item
        solr_item = {}
        for dst, src in self.mapping:
            solr_item[dst] = self.__get_item_value__(item, src)
        print(solr_item)
        self.solr.add([solr_item], commit=True)
        return item

    def __get_item_value__(self, item, src):
        if type(src) is str:
            return item[src] if src in item else None
        elif type(src) is list:
            return [item[i] if i in item else None for i in src]
        else:
            raise TypeError('Only string and list are valid mapping source')