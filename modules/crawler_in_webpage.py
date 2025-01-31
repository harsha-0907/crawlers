#!/bin/python3


from crawler import Crawler
from helper import *
class CrawlerHelper(Crawler):
    def __init__(self):
        print(self._domain)
        pass
    
    def weight(self):
        # This is after the sitemap.xml
        # Less value indicates higher priority
        return 2

    def scan(self):
        print("Webpage")
        return {}
