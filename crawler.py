#!/bin/python3

# Import the necessary packages
from typing import List
import logging
import importlib
import sys
import os
import requests
import socket
import time

class Crawler:
    # This module is used to run all the remaining modules
    def __init__(self, domain: str = None, isInvasive: bool = False, _allowedExtensions = [], _disallowedExtensions = [".gif", ".css", ".svg", ".png", ".webp"]):
        success = True
        try:
            self._logger = logging.Logger("Crawler-Log")
            self._logger.setLevel(logging.DEBUG)
            _handler = logging.StreamHandler(sys.stdout)
            _handler.setLevel(logging.DEBUG)
            _formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            _handler.setFormatter(_formatter)
            self._logger.addHandler(_handler)
            self._domain = domain
            self._crawler_payloads = {
                    "robots": [
                        "/robots.txt",
                        "/../../../../../../../../robots.txt",
                        "/..././..././..././..././..././..././robots.txt"
                    ],

                    "sitemap": [
                        "/sitemap.xml",
                        "/../../../../../../sitemap.xml",
                        "/..././..././..././..././..././..././sitemap.xml",
                        "/sitemap_index.xml",
                        "/../../../../../../sitemap_index.xml",
                        "/..././..././..././..././..././..././sitemap_index.xml"
                    ]
                }
            self._isInvasive = isInvasive
            self._headers = {"User-Agent": "GoWebCrawler"}
            self._cookies = None
            self._sessionHandler = requests.Session()
            self._directory_path = None
            self.loadModulePath()
            self.sortModules()
            self._allowedExtensions = _allowedExtensions  # None denotes that all extensions except the disallowed ones will be be considered
            # If allowedExtensions is not None, then only those endpoints will be considered (disallowed > allowed) -. precedence
            self._disallowedExtensions = _disallowedExtensions   # Files with these extensions will not be parsed
            self._timeout = 2
            __init_response = self._sessionHandler.get(self._domain, allow_redirects=True)

            if __init_response.status_code in range(200, 400):
                # Server is active & ready to serve requests
                self._logger.info("Server Active & Ready")

            elif __init_response.status_code in (401, 403):
                self._logger.critical("Error: Authorization Required (Possible Cause :- Important Headers Unavailable)")
                success = False

            elif __init_response.status_code in (404,):
                self._logger.critical("Error: Page Not Found")
                success = False
            
            elif __init_response.status_code in(405, 406, 407, 408):
                self._logger.critical("Error: Server Unavailable or behind an active WAF")
                self._logger.info("Try using the Advanced Crawler (Under-Development)")
                success = False
       
            else:
                success = False
                self._logger.critical("Error: Internal Error Occured from the Server side")

        except socket.gaierror as _sge:
            success = False
            print("Error connecting with the server")
        
        except Exception as _e:
            success = False
            print("Error connecting with the server", _e)
        
        finally:
            if not success:
                exit()

    def loadModulePath(self):
        # Here we are loading the path of the modules & the crawler in the sys.path
        # We are also loading the modules that will be initialized
        try:
            file_path = os.path.abspath(__file__)
            self._directory_path = file_path[:file_path.rfind('/')]
            sys.path.append(self._directory_path)
            sys.path.append(os.path.join(self._directory_path, "modules"))
            modules_py = os.listdir(os.path.join(self._directory_path, "modules"))


            self.__modules = [] # List of all the modules
            for _module in modules_py:
                if _module[-3:] == ".py" and _module[:7] == "crawler":
                    try:
                        __module = importlib.import_module(_module[:-3])
                        self.__modules.append(__module)
                    
                    except Exception as _e:
                        print(f"Error Loading the Module: {_module[:-3]}")
                
        except Exception as _ee:
            print("Error occured initializing the sys-path: ",_ee)
    
    def sortModules(self):
        self._classes = dict()
        for _modules in self.__modules:
            self.class_ref = getattr(_modules, "CrawlerHelper")
            pass
            _weight = self.class_ref.weight()
            self._classes[self.class_ref] = _weight
        
        self._classes = dict(sorted(self._classes.items(), key=lambda item: item[1])).keys()

    def payloads(self):
        return self._crawler_payloads

    def crawl(self) -> List:
        # We will first perform the scan for Robots.txt then Sitemap.xml & then lastly webpage
        # First sorting the modules in sorted order of the weights

        results = set()
        if not os.path.exists(os.path.join(self._directory_path, "results")):   # If the directory doesn't exist
            os.makedirs(os.path.join(self._directory_path, "results"))
        for class_obj in self._classes:
            _new_results = class_obj.scan(self) # Returns a set of urls
            if _new_results:
                results = results.union(_new_results)
                class_obj.saveJsonFile(self, _new_results)
        
        self._results = results
        self.saveFinalJsonFile()
        return list(results)
    
    def saveFinalJsonFile(self):
        from helper import saveFile
        if self._results:
            file_path = os.path.join(self._directory_path, "results", "total-urls.json")
            saveFile(file_path, {"Urls": list(self._results)})
            self._logger.info(f"Saved all the ursl in the file : {file_path}")
