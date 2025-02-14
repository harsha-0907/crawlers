#!/bin/python3

# Import the necessary packages
from typing import List
import json
import logging
import colorlog
import importlib
import sys
import os
import requests
import socket
import time

class Crawler:
    # This module is used to run all the remaining modules

    def loadLogger(self):
        # Initializing the object variables & dependencies like logger 
        self.logger = logging.Logger("Crawler-Log")
        LOG_FORMAT = '%(log_color)s - %(levelname)-8s%(reset)s %(message)s'
        formatter = colorlog.ColoredFormatter(
                        LOG_FORMAT,
                        log_colors={
                            'DEBUG': 'green',
                            'INFO': 'normal',
                            'WARNING': 'pink',
                            'ERROR': 'light_red',
                            'CRITICAL': 'dark_red',
                        }
                    )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger = logging.getLogger('colored_logger')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    
    def loadSettings(self):
        # The setings are present in the settings.json file
        try:
            if os.path.exists(os.path.join(self.directory_path, "settings.json")):
                with open(os.path.join(self.directory_path, "settings.json"))as file:
                    self.data_store = json.loads(file.read())
                    
                self.crawler_payloads = self.data_store["Configurations"]["crawler-payloads"]
                self.isInvasive = self.data_store["Configurations"]["isInvasive"]
                self.headers = {"User-Agent": self.data_store["Configurations"]["user-agent"]}
                self.cookies = self.data_store["Configurations"]["cookies"]
                self.timeout = self.data_store["Configurations"]["timeout"]
            
            else:
                self.logger.critical("Invalid Settings.json")
                exit()
        
        except Exception as _e:
            self.logger.critical(f"Error Occured while loading settings\n Error: {_e}")
            exit()
        
    def loadPaths(self):
        file_path = os.path.abspath(__file__)
        self.directory_path = file_path[:file_path.rfind('/')]
        self.module_directory_path = os.path.join(self.directory_path, "modules")

        # print(self.directory_path, self.module_directory_path)

        # Add the directories for searching modules & other files
        sys.path.append(self.directory_path)
        sys.path.append(self.module_directory_path)

    def loadSessionHandler(self):
        try:
            self.sessionHandler = requests.Session()
            self.sessionHandler.headers.update(self.headers)
            self.sessionHandler.cookies.update(self.cookies)
        
        except Exception as _e:
            self.logger.critical(f"Error Occured while loading session handler\n Error: {_e}")
            exit()

    def isServerActive(self):
        try:
            _resp = self.sessionHandler.get(self.domain, timeout=10)

            if _resp is None:
                self.logger.critical("Null Response Recieved.")
                exit()
            
            elif _resp.status_code in (405, 406, 407, 408):
                self.logger.warning("Error: Server Unavailable or behind an active WAF")
                exit()

            else:
                # Server is Active
                self.logger.debug("The Server is Active.")
                pass
        
        except socket.gaierror as _sge:
            self.logger.critical(f"Host Name Invalid.. Please re-check the domain\n Error: {_sge}")
            exit()
        
        except requests.Timeout as _rte:
            self.logger.warning(f"Host Connection has Timed Out... \n Error: {_rte}")
            exit()

        except Exception as _e:
            self.logger.critical(f" An Unknown Error Occured\n Error: {_e}")
            exit()

    def loadCrawlerClasses(self):
        try:
            _crawler_modules_ = os.listdir(self.module_directory_path)
            self.unsorted_crawler_classes = [] # List of all the modules

            for _module in _crawler_modules_:
                if _module[-3:] == ".py" and _module[:7] == "crawler":
                    try:
                        __module = importlib.import_module(_module[:-3])
                        __class = getattr(__module, "CrawlerHelper")
                        self.unsorted_crawler_classes.append(__class)
                    
                    except Exception as _e:
                        self.logger.error(f"Error Loading the Module/Class: {_module[:-3]}")
                
        except Exception as _ee:
            self.logger.critical(f"Error occured while loading modules\n Error : {_ee}")
            exit()

    def sortClasses(self):
        # Sort the classes according to the weights assigned
        try:
            __class_dict = dict()
            for _class in self.unsorted_crawler_classes:
                _weight = _class.weight()
                __class_dict[_class] = _weight
            
            self.crawler_classes = dict(sorted(__class_dict.items(), key=lambda item: item[1])).keys()
        
        except Exception as _e:
            self.logger.critical(f"Error Occured while Sorting the Classes. \n Error : {_e}")
            exit()

    def setup(self):
        # Setup all the variables & dependencies
        print("Initializing the Crawler Dependencies")
        self.loadLogger()
        self.loadPaths()
        self.loadSettings()
        self.loadSessionHandler()
        self.isServerActive()
        self.loadCrawlerClasses()
        self.sortClasses()
        print("Crawler Initalized Successfully")

    def payloads(self):
        return self.crawler_payloads

    def __init__(self, domain, isInvasive):
        self.domain = domain
        self.isInvasive = isInvasive
        self.setup()

    def crawl(self) -> List:
        # We will first perform the scan for Robots.txt then Sitemap.xml & then lastly webpage
        # First sorting the modules in sorted order of the weights

        results = set()
        if not os.path.exists(os.path.join(self.directory_path, "results")):   # If the directory doesn't exist
            os.makedirs(os.path.join(self.directory_path, "results"))
        for class_obj in self.crawler_classes:
            _new_results = class_obj.scan(self) # Returns a set of urls
            if _new_results:
                results = results.union(_new_results)
                class_obj.saveJsonFile(self, _new_results)
        
        self.results = results
        self.saveFinalJsonFile()
        return list(results)
    
    def saveFinalJsonFile(self):
        from helper import saveFile
        if self.results:
            file_path = os.path.join(self.directory_path, "results", "total-urls.json")
            saveFile(file_path, {"Urls": list(self.results)})
            self.logger.info(f"Saved all the ursl in the file : {file_path}")
