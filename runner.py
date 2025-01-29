#!/bin/python3

from crawler import Crawler

crawler_obj = Crawler("https://www.fca.org.uk", isInvasive=True)
crawled_urls = crawler_obj.crawl()

print(f"Crawled Urls: {crawled_urls}")