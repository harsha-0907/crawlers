#!/bin/python3

from crawler import Crawler
from helper import *

class CrawlerHelper(Crawler):
    def __init__(self):
        pass
    
    def weight(self):
        # This is after the sitemap.xml
        # Less value indicates higher priority
        return 2

    def scan(self):
        print("Webpage")
        # Add filter to make sure that dis-allowed pages are not crawled
        return {}

    def saveJsonFile(self, urls):
        saveFile(os.path.join(self._directory_path, "results", "urls-webpage.json"), {"Webpage": list(urls)})
        self._logger.info("Document Dump Successful")

