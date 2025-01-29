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
    def __init__(self, domain: str = None, isInvasive: bool = False):
        success = True
        try:
            print("This is Crawler")
            self._domain = domain
            self._isInvasive = isInvasive
            self._logger = logging.Logger("Crawler-Log")
            self._logger.setLevel(logging.INFO)
            self._headers = {"User-Agent": "Crawler-Bot"}
            self._cookies = None
            self._sessionHandler = requests.Session()
            self._directory_path = None
            self.loadModulePath()
            self.sortModules()
            __init_response = self._sessionHandler.get(self._domain)
            __init_response.raise_for_status()
        
        except requests.exceptions.RequestException as _ree:
            success = False
            print("Error connecting with the server", _ree)
        
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
            class_obj = getattr(_modules, "CrawlerHelper")
            _weight = class_obj.weight(self)
            self._classes[class_obj] = _weight
        
        self._classes = dict(sorted(self._classes.items(), key=lambda item: item[1])).keys()

    def payloads(self):
        return {
            "robots": [
                "/robots.txt",
                 "/../../../../../../../../robots.txt",
                  "..././..././..././..././..././..././robots.txt"
            ]
        }

    def crawl(self) -> List:
        # We will first perform the scan for Robots.txt then Sitemap.xml & then lastly webpage
        # First sorting the modules in sorted order of the weights

        results = set()
        for class_obj in self._classes:
            results = results.union(class_obj.scan(self))   # Sends a set of urls

        return list(results)
        