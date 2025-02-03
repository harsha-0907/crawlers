#!/bin/python3

from bs4 import BeautifulSoup
from crawler import Crawler
from helper import *
import os

class CrawlerHelper(Crawler):
    """
    This module is used to parse the sitemap.xml file recursively.
    """
    def __init__(self):
        pass

    @staticmethod
    def weight():
        # Next in queue after the robots.txt
        # Less value indicates higher priority
        return 1

    @staticmethod
    def info():
        return """We are crawling the urls from sitemap.xml present in the webite
                All the urls will be parsed irrespective of the invasivness of the crawling"""

    @staticmethod
    def parseXMLData(xml_data):
            # We will consider the data that is present in between the <loc> ... </loc>
            # We will return 2 sets (urls & any sitemaps)
            _sitemaps = set()
            xml_soup = BeautifulSoup(xml_data, "xml")
            _xml_urls = xml_soup.find_all("loc")
            xml_urls = set()   # The final set of urls
            for _xml_url in _xml_urls:
                _xml_url = str(_xml_url)[5:-6]
                if ".xml" in _xml_url:
                    _sitemaps.add(_xml_url)
                else:
                    xml_urls.add(_xml_url)

            return (xml_urls, _sitemaps)

    @staticmethod
    def parseHTMLData(html_data): # self is the parent object (crawler's instance)
        # The sitemap mostly consists of 'a' tags
        _sitemaps = set()
        html_soup = BeautifulSoup(html_data, "html.parser")
        __urls = html_soup.find_all("a")
        for __url in __urls:
            __url = __url[3:-4]
            __url = __url[__url.find("=")+2:]
            __url = __url[:__url.find('"')]
            if ".xml" in __url:
                _sitemaps.add(__url)
            else:
                # Remove href from the text
                xml_urls.add(self_domain + __url)
        
        return (xml_urls, _sitemaps)
    
    @classmethod
    def scan(cls, self):    # self is the object of the parent class(crawler)
        # We are defining scan as parent class as we need to call other methods of the child class(CrawlerHelper)
        print("Sitemap")
        urls = set()  # All the urls that don't have sitemap.xml in them
        _payloads = self.payloads()["sitemap"]
        for _payload in _payloads:
            try:
                url = self._domain + _payload
                _resp = requester(sessionHandler=self._sessionHandler,
                    url=url, headers=self._headers, cookies=self._cookies, allow_redirects=True)
                
                if _resp is None or _resp.status_code >= 400:
                    continue
                
                else:
                    # We found the payload, so now we will explore all the urls present in the xml doc
                    # This has to go in a loop
                    _payloads = set([url]); _completed_payloads = set()
                    while len(_payloads) > 0:
                        url = _payloads.pop()
                        if url not in _completed_payloads:
                            _completed_payloads.add(url)
                            _resp = requester(sessionHandler=self._sessionHandler,
                                url=url, headers=self._headers, cookies=self._cookies, allow_redirects=True)

                            if _resp:
                                if _resp.status_code < 400:
                                    # Classify the type of response
                                    _content_type = getContentType(_resp)
                                    if _content_type == "text/html":
                                        __urls, __payloads = cls.parseHTMLData(_resp.text)
                                        urls = urls.union(__urls)
                                        _payloads = _payloads.union(__payloads)

                                    else:
                                        # Default is text/xml
                                        __urls, __payloads = cls.parseXMLData(_resp.text)
                                        urls = urls.union(__urls)
                                        _payloads = _payloads.union(__payloads)
                                    
                                else:
                                    # This is not a valid payload
                                    continue

                        else:
                            # This payload is already complete
                            continue
                    
                    # No need to check for any other payloads
                    break
            except Exception as _e:
                self._logger.error(f"Error in sitemap.scan module.\n Error: {_e}")
            
        return urls

    def saveJsonFile(self, urls):
        saveFile(os.path.join(self._directory_path, "results", "urls-sitemap.json"), {"Sitemap": list(urls)})
        self._logger.info("Document Dump Successful")
