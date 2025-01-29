#!/bin/python3


from crawler import Crawler
from helper import *
print("This is Crawler IN Sitemap")
class CrawlerHelper(Crawler):
    def __init__(self):
        pass

    def weight(self):
        # Next in queue after the robots.txt
        # Less value indicates higher priority
        return 1

    def scan(self):
        print("Sitemap")
        return {}
