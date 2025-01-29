#!/bin/python3

from bs4 import BeautifulSoup
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
        def parseXMLData(xml_data):
            # We will consider the data that is present in between the <loc> ... </loc>
            # We will return 2 sets (urls & any sitemaps)
            _sitemaps = {}
            xml_soup = BeautifulSoup(xml_data, "xml")
            __urls = xml_soup.find_all("loc")
            xml_urls = {}
            for __url in __urls:
                if ".xml" in __url:
                    _sitemaps.add(__url)
                else:
                    xml_urls.add(__url)

            return (xml_urls, _sitemaps)

        def parseHTMLData(html_data):
            # The sitemap mostly consists of 'a' tags
            _sitemaps = {}
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
        
        print("Sitemap")
        urls = {}  # All the urls that don't have sitemap.xml in them
        _payloads = self.payloads()["payloads"]
        _completed_payloads = {}

        for _payload in _payloads:
            try:
                _resp = requester(sessionHandler=self._sessionHandler,
                    url=url, headers=self._headers, cookies=self._cookies, allow_redirects=True)
                if _resp.status_code >= 400:
                    continue
                
                else:
                    # This has to go in a loop
                    _payloads = set(url)
                    for _payload in _payloads:
                        _url = self._domain + _payload
                        if _url in _completed_payloads:
                            continue
                        
                        _resp = requester(sessionHandler=self._sessionHandler,
                            url=url, headers=self._headers, cookies=self._cookies, allow_redirects=True)
                        
                        if _resp.status_code < 400:
                            _content_type = getContentType(_resp)
                            _payloads.remove(url)
                            if _content_type == "text/html":
                                __payloads, __sitemaps = parseHTMLData(_resp.text)
                                _payloads = _payloads.union(__payloads)
                                urls = urls.union(__payloads)
                            else:
                                # This is a XML page
                                __payloads, __sitemaps = parseXMLData(_resp.text)
                                _payloads = _payloads.union(__sitemaps)
                                urls = urls.union(__payloads)
                            _completed_payloads.add(url)


            except Exception as _e:
                self._logger.error(f"Error in sitemap.scan module.\n Error: {_e}")
            
        return urls
