#!/bin/python3

from crawler import Crawler
from helper import *

class CrawlerHelper(Crawler):
    def __init__(self):
        pass
    
    @staticmethod
    def weight():
        # This is after the sitemap.xml
        # Less value indicates higher priority
        return 2

    @classmethod
    def scan(cls, self):    # Here self -> object of the parent class
        # We are defining scan as parent class as we need to call other methods of the child class(CrawlerHelper)
        print("Crawling Webpages")
        return {}

    def saveJsonFile(self, urls):
        saveFile(os.path.join(self._directory_path, "results", "urls-webpage.json"), {"Webpage": list(urls)})
        self._logger.info("Document Dump Successful")

