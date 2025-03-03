#!/bin/python3

import time
import regex as re
import os
from os.path import splitext
from urllib.parse import urlparse, urljoin
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

    @staticmethod
    def name():
        return "CrawlerInWebpage"
    
    @staticmethod
    def info():
        return """
            Here we will start with the BaseUrl and then move using depth-first search algorithm.
            We will parse all the data frorm webpages filter the urls & follow them
        """

    def parseData(cls, self, web_data , url):
        # Links(Direct & In-Direct are found in anchor tags) -> href, src (most cases)
        finalUrls = set(); urls = set()
        try:
            domain_name = self.domain.split("/", 2)[2]
            src_pattern = r'src="[^\s]+"'
            href_pattern = r'href="[^\s]+"'
            src_text = re.findall(src_pattern, web_data)
            for _text in src_text:
                _url = _text[5:-1]
                if "javascript" in _url:
                    pass
                if "http" != _url[:4]:
                    if _url[0] == '/':
                        urls.add(self.domain+_url)

                    else:
                        _url = urljoin(url, _url)
                        urls.add(_url)

                else:
                    if domain_name in _url:
                        urls.add(_url)

            href_text = re.findall(href_pattern, web_data)
            for _text in href_text:
                _url = _text[6:-1]
                if "javascript" in _url:
                    pass
                if "http" != _url[:4]:
                    # This is an indirect url (same domain only)
                    if _url[0] == '/':
                        # This is a direct path
                        urls.add(self.domain+_url)

                    else:
                        _url = urljoin(url, _url)
                        urls.add(_url)

                else:
                    if domain_name in _url:
                        urls.add(_url)

            for url in urls:
                if url[:4] == "http" and cls.isValidExtension(self, url):
                    finalUrls.add(url)

        except Exception as _e:
            self.logger.warning("Error occured while Parsing Webpage: {_e}")

        finally:
            return finalUrls

    def isValidExtension(self, url):
        try:
            _url = urlparse(url)
            _ext = splitext(_url.path)[1]
            if _ext in self.disallowedExtensions:
                return False
            elif _ext == '' or self.allowedExtensions == [] or _ext in self.allowedExtensions:

                return True
            else:
                return False

        except Exception as _e:
            return False

    def addGraphNode(self, url,egressUrls):
        nodeVal = self.urls[url]
        self.graph[nodeVal] = [self.urls[_url] for _url in egressUrls if _url in self.urls] # Compressing the Nodes
        return True
        
    @classmethod
    def scan(cls, self):    # Here self -> object of the parent class
        # We are defining scan as parent class as we need to call other methods of the child class(CrawlerHelper)
        if self.isInvasive:    # This is an Invasive scan -> consumes a lot of network bandwidth
            self.logger.info("Crawling Webpages")
            _last_time = 0
            _request_interval = 0.4
            stack = [(1, self.domain)]; # Any new url is checked in stack first and then in self.urls
            now_time = time.time(); maxTime = self.data_store["Configurations"]["timedCrawl"]; newUrls = True
            completed_urls = set()
            try:
                while len(stack) > 0:
                    if maxTime is not None and time.time() - now_time > maxTime:
                        self.logger.warning("Aborting Crawl - Time Complete")
                        break

                    stack_pos, newUrl = stack.pop(-1)
                    if newUrl in completed_urls:
                        continue
                    completed_urls.add(newUrl)
                    if stack_pos > self.maxDepth:
                        continue
                    response = requester(sessionHandler=self.sessionHandler, url=newUrl, headers=self.headers,
                        cookies=self.cookies, allow_redirects=True, timeout=self.timeout)

                    if response is None:
                        continue

                    newUncheckedUrls = cls.parseData(cls, self, response.text, newUrl)
                    for _url in newUncheckedUrls:
                        if _url in completed_urls:
                            continue
                        else:
                            stack.append((stack_pos+1, _url))
                            self.addUrls([_url])
                    cls.addGraphNode(self, newUrl, newUncheckedUrls)

            except Exception as _e:
                self.logger.warning(f"Error Occured in Web-Crawl: {_e}")
            
            finally:
                if len(completed_urls) > 0:
                    cls.saveGraph(self)
                return {}

        else:
            print("Not Crawling the Webpages")
            self.logger.info("This is a non Invasive scan")
            return {}

    def saveJsonFile(self, urls):
        saveFile(os.path.join(self.directory_path, "results", "urls-webpage.json"), {"Urls": list(urls)})
        self.logger.info("Document Dump Successful")

    def saveGraph(self):
        # graph = dict()
        # for graphNode in self.graph:
        #     graph[self.reverseUrls[graphNode]] = [self.reverseUrls[url] for url in self.graph[graphNode]]   # Inflating the Nodes

        graphFile = os.path.join(self.directory_path, "results", "web-graph.json")
        urlsFile = os.path.join(self.directory_path, "results", "web-urls.json")
        saveFile(graphFile, self.graph)
        saveFile(urlsFile, self.reverseUrls)        
        self.logger.info(f"Graph Saved (Check here: {graphFile})")
