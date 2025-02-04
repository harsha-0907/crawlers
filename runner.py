#!/bin/python3

from crawler import Crawler

baseUrl = input("Base Url (https://example.com): ")

crawler_obj = Crawler(baseUrl, isInvasive=True)
crawled_urls = crawler_obj.crawl()

# print(f"Crawled Urls: {crawled_urls}")
print(f"Number of Crawled Urls: {len(crawled_urls)}")