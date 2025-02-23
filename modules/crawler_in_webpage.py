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
    def name():
        return "CrawlerInWebpage"
    
    @staticmethod
    def info():
        return """
            Here we will start with the BaseUrl and then move using depth-first search algorithm.
            We will parse all the data frorm webpages filter the urls & follow them
        """

    def parseData(cls, self, web_data , url):  # It might consist any file(html, js, css or php)
        # Links(Direct & In-Direct are found in anchor tags) -> href, src (most cases)
        finalUrls = set(); urls = set()
        try:
            url_path = urlparse(url).path
            if url_path != '/':
                url_path += '/'

            domain_name = self.domain.split("/", 2)[2]
            src_pattern = r'src="[^\s]+"'   # regex Patterns to match src
            href_pattern = r'href="[^\s]+"'  # regex Patterns to match href
            src_text = re.findall(src_pattern, web_data)

            for _text in src_text:
                _url = _text[5:-1]
                if "http" != _url[:4]:
                    # This is an indirect url (same domain only)
                    if _url[0] == '/':
                        # This is a direct url
                        urls.add(self.domain+_url)

                    else:
                        # This is an indirect url
                        urls.add(self.domain+url_path+_url)

                else:
                    if domain_name in _url:
                        # Check if the url belongs to the same domain
                        urls.add(_url)
                        
            href_text = re.findall(href_pattern, web_data)

            for _text in href_text:
                _url = _text[6:-1]
                if "http" != _url[:4]:
                    # This is an indirect url (same domain only)
                    if _url[0] == '/':
                        # This is a direct path
                        urls.add(self.domain+_url)
                    
                    else:
                        urls.add(self.domain+url_path+_url)
                    
                else:
                    if domain_name in _url:
                        # CHeck for the extension
                        urls.add(_url)
                    
            for url in urls:
                if cls.isValidExtension(self, url):
                    finalUrls.add(url)
            # finalUrls = [url for url in urls if cls.isValidExtension(self, url)]
            
        except Exception as _e:
            pass

        finally:
            return finalUrls
        
    def isValidExtension(self, url):
        # We will check if the response data that is expected from the url is required or not
        try:
            _url = urlparse(url)
            _ext = splitext(_url.path)[1]
            if _ext in self.disallowedExtensions:
                return False
            elif _ext == '' or self.allowedExtensions == [] or _ext in self.allowedExtensions:
                # If it is a webpage like(/path1/path2)
                return True
            else:
                return False    # This extension is not restricted but also not required

        except Exception as _e:
            return False

    @classmethod
    def scan(cls, self):    # Here self -> object of the parent class
        # We are defining scan as parent class as we need to call other methods of the child class(CrawlerHelper)
        if self.isInvasive:    # This is an Invasive scan -> consumes a lot of network bandwidth
            self.logger.info("Crawling Webpages")
            _last_time = 0  # Intitalizing the _last_time param
            _request_interval = 0.4 # A timeout of atleast 0.4 seconds before sending another request (increases on 429 error)
            # Here we have to start with a single url & start searching for others
            # Starting point of the crawl will be baseUrl or first url in the urls(set)
            stack = [(1, self.domain)]; # Any new url is checked in stack first and then in self.urls
            now_time = time.time(); maxTime = self.data_store["Configurations"]["timedCrawl"]; newUrls = True
            completed_urls = set()

            while len(stack) > 0:
                if maxTime is not None and time.time() - now_time > maxTime:
                    self.logger.warning("Aborting Crawl - Time Complete")
                    break
                
                stack_pos, newUrl = stack.pop(-1)
                if newUrl in completed_urls:
                    continue
                  
                completed_urls.add(newUrl)
                if stack_pos > self.maxDepth:
                    # This url will not be considered now as maxDepth reached
                    continue
                self.urls.add(newUrl)
                response = requester(sessionHandler=self.sessionHandler, url=newUrl, headers=self.headers, cookies=self.cookies, allow_redirects=True, timeout=self.timeout)

                if response is None:
                    continue
                
                newUncheckedUrls = cls.parseData(cls, self, response.text, response.url)
                # newUrls = False # There are no new urls detected
                for _url in newUncheckedUrls:
                    if _url[-1] == '/':
                        _url = _url[:-1]

                    if _url in completed_urls:
                        # We will not pursue with this url
                        continue

                    else:
                        stack.append((stack_pos+1, _url))
                        # newUrls = True

            print(len(stack), len(completed_urls))
            # cls.saveJsonFile(self, urls)
        else:
            print("Not Crawling the Webpages")
            self.logger.info("This is a non Invasive scan")
            return {}

    def saveJsonFile(self, urls):
        saveFile(os.path.join(self.directory_path, "results", "urls-webpage.json"), {"Webpage": list(urls)})
        self.logger.info("Document Dump Successful")


