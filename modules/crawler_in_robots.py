#!/bin/python3

from crawler import Crawler
from helper import requester
import regex

class CrawlerHelper(Crawler):
    """
        This module is used to crawl the robots.txt file
    """
    def __init__(self):
        self._logger.info("Running the Robots-Crawler")
        pass

    def weight(self):
        # This indicates the order the class has to run
        # Less value indicates higher priority
        return 0

    def info(self):
        return """We are parsing the robots.txt to find any related paths or urls present in the website.
                    If the scan is asked as non Invasive only scan the allow part else scan the disallow sites also"""            

    def scan(self):
        def parseData(robo_data):
            try:
                with open("robots.txt", 'w') as fiel:
                    fiel.write(robo_data)

                lines = robo_data.split('\n')
                urls = set()
                for _line in lines:
                    if _line == '' or _line[0] == '#':
                        # This is a comment
                        continue
                    else:
                        _access, _path = _line.split(' ', 1)
                        if _access == "Allow:" or (_access == "Disallow:" and self._isInvasive):
                            # Now check if the path
                            _pos_last_backslash = _path.rfind('/')
                            _directory_path = _path[:_pos_last_backslash+1]
                            urls.add(self._domain + _directory_path)
                if urls:
                    return urls
                else:
                    return {}
            
            except Exception as _e:
                self._logger.error("Error while parsing the Robots file", _e)
                return list(urls)
            
        __paths = self.payloads()["robots"]
        for __path in __paths:
            url = self._domain + __path
            _resp = requester(sessionHandler=self._sessionHandler, url=url, headers=self._headers, cookies=self._cookies, allow_redirects=True)
            if (_resp is not None) and (_resp.status_code >= 400):
                continue
            else:
                _urls = parseData(_resp.text)
                # Break as soon as the robots.txt is parsed
                return _urls
        return {}
