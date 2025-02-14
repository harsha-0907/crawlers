#!/bin/python3

import time
import regex as re
from os.path import splitext
from urllib.parse import urlparse
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
    def info():
        return """
            Here we will start with the BaseUrl and then move using depth-first search algorithm.
            We will parse all the data frorm webpages filter the urls & follow them
        """

    def parseData(self, web_data):  # It might consist any file(html, js, css or php)
        # Links(Direct & In-Direct are found in anchor tags) -> href, src (most cases)
        urls = set()
        try:
            domain_name = self.domain.split("/", 2)[2]
            src_pattern = r'src="[^\s]+"'   # regex Patterns to match src
            href_pattern = r'href="[^\s]+"'  # regex Patterns to match href
            src_text = re.findall(src_pattern, web_data)
            for _text in src_text:
                _url = _text[5:-1]
                if "http" not in _url:
                    # This is an indirect url (same domain only)
                    if _url[0] == '/':
                        urls.add(self.domain+_url)
                else:
                    if domain_name in _url:
                        # Check if the url belongs to the same domain
                        urls.add(_url)
                    else:
                        # This url belongs to a different domain => Hence not considered
                        pass
            
            href_text = re.findall(href_pattern, web_data)
            for _text in href_text:
                _url = _text[6:-1]
                if "http" not in _url:
                    # This is an indirect url (same domain only)
                    if _url[0] == '/':
                        urls.add(self.domain+_url)
                else:
                    if domain_name in _url:
                        urls.add(_url)
                    else:
                        # This url belongs to another domain => not considered
                        pass
        
        except Exception as _e:
            pass

        finally:
            return urls
        
    def isValidExtension(self, url):
        # We will check if the response data that is expected from the url is required or not
        _url = urlparse(url)
        _ext = splitext(_url.path)[1]
        if _ext in self.disallowedExtensions:
            return False
        elif _ext == '' or self.allowedExtensions == [] or _ext in self.allowedExtensions:
            # If it is a webpage like(/path1/path2)
            return True
        else:
            return False    # This extension is not restricted but also not required

    @classmethod
    def scan(cls, self):    # Here self -> object of the parent class
        # We are defining scan as parent class as we need to call other methods of the child class(CrawlerHelper)
        if self.isInvasive:    # This is an Invasive scan -> consumes a lot of network bandwidth
            print("Crawling Webpages")
            _last_time = 0  # Intitalizing the _last_time param
            _request_interval = 0.4 # A timeout of atleast 0.4 seconds before sending another request (increases on 429 error)
            # Here we have to start with a single url & start searching for others
            # Starting point of the crawl will be baseUrl or first url in the urls(set)
            crawled_urls = set(); queue = [self.domain]    
            while len(queue) > 0:
                _current_url = queue.pop(0)
                _resp = requester(sessionHandler=self.sessionHandler, url=_current_url, headers=self.headers,
                        cookies=self.cookies, timeout=self.timeout, allow_redirects=True)
                last_time = time.time() # To store the time at which the scan started
                _new_results = set()
                if _resp is not None:
                    # Parse the response if it is valid for any content
                    if _resp.status_code == 429:
                        # Rate Limiting Code (increasing the request interval by 0.1 s)
                        _request_interval += 0.1
                        time.sleep(_request_interval)
                        queue.insert(0, _current_url)
                        continue
                    
                    else:
                        _new_results = cls.parseData(self, _resp.text)
                
                # print(len(_new_results))
                if _new_results:
                    for _new_url in _new_results:
                        if cls.isValidExtension(self, _new_url):
                            if _new_url[-1] == '/':
                                _new_url = _new_url[:-1]
                            
                            if _new_url in crawled_urls or _new_url in queue:
                                continue
                            else:
                                queue.append(_new_url)

                # Wait for _request_interval seconds before sending another request
                _time_spent = time.time() - _last_time
                if _time_spent < _request_interval:
                    _time_rem = _request_interval - _time_rem
                    time.sleep(_time_rem)

                crawled_urls.add(_current_url)
                
        else:
            print("Not Crawling the WEbpage")
            self.logger.info("Web-Crawling not Done as scan is non Invasive")
            return {}

    def saveJsonFile(self, urls):
        saveFile(os.path.join(self.directory_path, "results", "urls-webpage.json"), {"Webpage": list(urls)})
        self.logger.info("Document Dump Successful")

