#!/bin/python3

from crawler import Crawler
from helper import requester, saveFile, fetchPathAndParams
import os
import regex

class CrawlerHelper(Crawler):
    """
        This module is used to crawl the robots.txt file
    """

    def __init__(self):
        pass

    @staticmethod
    def weight():
        # This indicates the order the class has to run
        # Less value indicates higher priority
        return 0

    @staticmethod
    def info():
        return """We are parsing the robots.txt to find any related paths or urls present in the website.
                    If the scan is asked as non Invasive only scan the allow part else scan the disallow sites also"""            

    def parseData(self, robo_data):
            try:
                site_map_urls = set()
                lines = robo_data.split('\n')
                urls = set()
                for _line in lines:
                    if _line == '' or _line[0] == '#':
                        # This is a comment
                        continue

                    elif "Sitemap" in _line:
                        # This is the url to the sitemap
                        _, site_map_url = _line.split(' ', 1)
                        # Here we will change the payload of the sitemap
                        site_map_urls.add(site_map_url)

                    else:
                        if _line[:5] == "Allow" or _line[:8] == "Disallow":
                            try:
                                _access, _path = _line.split(' ', 1)
                                if _access == "Allow:" or (_access == "Disallow:" and self._isInvasive):
                                    # Now check if the path
                                    _pos_last_backslash = _path.rfind('/')
                                    _directory_path = _path[:_pos_last_backslash+1]
                                    urls.add(self._domain + _directory_path)
                            except ValueError as _ve:
                                # The line doesn't have any path mentioned after the Allow/Disallow
                                continue
                                
                if site_map_urls:
                    print(site_map_urls)
                    site_map_urls = ['/'+fetchPathAndParams(url_path) for url_path in site_map_urls]
                    print(site_map_urls)
                    self._crawler_payloads["sitemap"] = list(site_map_urls)
                    print("Updated the Sitemap")
                
                if urls:
                    return urls
                else:
                    return {}
            
            except Exception as _e:
                self._logger.error("Error while parsing the Robots file", _e)
                return list(urls)
        
    @classmethod
    def scan(cls, self): # Here self is the parent class's object
        # We are defining scan as parent class as we need to call other methods of the child class(CrawlerHelper)
        self._logger.info("Scanning the Robots.txt")
        __paths = self.payloads()["robots"]
        for __path in __paths:
            url = self._domain + __path
            _resp = requester(sessionHandler=self._sessionHandler, url=url, headers=self._headers, cookies=self._cookies, allow_redirects=True)
            if (_resp is not None) and (_resp.status_code >= 400):
                continue
            else:
                _urls = cls.parseData(self, _resp.text)
                # Break as soon as the robots.txt is parsed
                return _urls
        return {}

    def saveJsonFile(self, urls):
        saveFile(os.path.join(self._directory_path, "results", "urls-robots.json"), {"Robots": list(urls)})
        self._logger.info("Document Dump Successful")