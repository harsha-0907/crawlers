#!/bin/python3

# Import the necessary packages
from typing import List
import json
import logging
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
        self.logger = logging.getLogger("Crawler-Log")
        self.logger.setLevel(logging.DEBUG)  # Set the logger to capture DEBUG and above
        
        # Create a file handler to write logs to a file
        handler = logging.FileHandler('crawler.log')
        handler.setLevel(logging.DEBUG)  # Ensure the handler is set to capture DEBUG and above
        
        # Create a formatter with the desired format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add the handler to the logger
        self.logger.addHandler(handler)

        self.logger.info("-"*100)
        self.logger.info("\n\n New Scan")
    
    def loadPaths(self):
        file_path = os.path.abspath(__file__)
        self.directory_path = file_path[:file_path.rfind('/')]
        self.module_directory_path = os.path.join(self.directory_path, "modules")
        sys.path.append(self.directory_path)
        sys.path.append(self.module_directory_path)

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
                self.maxDepth = self.data_store["Configurations"]["maxdepth"]   # The default value for depth limit is 4
                self.disallowedExtensions = self.data_store["Configurations"]["disallowedExtensions"]
                self.allowedExtensions = self.data_store["Configurations"]["allowedExtensions"]

            else:
                self.logger.critical("Invalid Settings.json")
                exit()
        
        except Exception as _e:
            self.logger.critical(f"Error Occured while loading settings\n Error: {_e}")
            exit()
    
    def loadVariables(self):
        self.urls = {self.domain: 0, }
        self.reverseUrls = {0: self.domain, }
        self.graph = dict()

    def loadSessionHandler(self):
        try:
            self.sessionHandler = requests.Session()
            self.sessionHandler.headers.update(self.headers)
            self.sessionHandler.cookies.update(self.cookies)
        
        except Exception as _e:
            self.logger.critical(f"Error Occured while loading session handler\n Error: {_e}")
            exit()

    def validateServerDetails(self):
        # Any checks for the server
        if self.domain[-1] == '/':
            # The url shouldn't end with a '/'
            self.domain = self.domain[:-1]

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
        self.loadVariables()
        self.loadSessionHandler()
        self.validateServerDetails()
        self.isServerActive()
        self.loadCrawlerClasses()
        self.sortClasses()
        print("Crawler Initalized Successfully")

    def payloads(self):
        return self.crawler_payloads

    def addUrls(self, urls):
        index = len(self.urls) + 1
        for url in urls:
            if url not in self.urls:
                self.urls[url] = index
                self.reverseUrls[index] = url
            index += 1

    def __init__(self, domain):
        self.domain = domain
        self.setup()

    def crawl(self) -> List:
        if not os.path.exists(os.path.join(self.directory_path, "results")):   # If the directory doesn't exist
            os.makedirs(os.path.join(self.directory_path, "results"))
        for class_obj in self.crawler_classes:
            module_start_time = time.time()
            _new_results = class_obj.scan(self) # Returns a set of urls
            _already_found_urls = len(self.urls)
            if _new_results:
                self.addUrls(_new_results)
                class_obj.saveJsonFile(self, _new_results)
            else:
                _new_results = {}

            module_end_time = time.time()
            self.logger.info(f"{class_obj.name()} - Total Urls Found: {len(_new_results)} - New - {len(self.urls) - _already_found_urls}")
            self.logger.info(f"Execution Time- {module_end_time-module_start_time}")
        
        self.saveFinalJsonFile()
        return list(self.urls)
    
    def saveFinalJsonFile(self):
        from helper import saveFile
        if self.urls:
            file_path = os.path.join(self.directory_path, "results", "total-urls.json")
            saveFile(file_path, {"Urls": list(self.urls)})
            self.logger.info(f"Saved all the urls in the file : {file_path}")
