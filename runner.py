#!/bin/python3

from crawler import Crawler

crawler_obj = Crawler("https://www.google.com", isInvasive=True)
crawled_urls = crawler_obj.crawl()

# print(f"Crawled Urls: {crawled_urls}")
print(f"Number of Crawled Urls: {len(crawled_urls)}")