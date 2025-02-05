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
        self._logger = logging.Logger("Crawler-Log")
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
            if os.path.exists(os.path.join(self._directory_path, "settings.json")):
                with open(os.path.join(self.directory_path, "settings.json"))as file:
                    self.data_store = json.loads(file.read())
                    
                self.crawler_payloads = self.data_store["crawler-payloads"]
                self.isInvasive = self.data_store["isInvasive"]
                self.headers = {"User-Agent": self.data_store["user-agent"]}
                self.cookies = self.data_store["cookies"]
                self._timeout = self.data_store["timeout"]
            
            else:
                self._logger.critical("Invalid Settings.json")
                exit()
        
        except Exception as _e:
            self._logger.critical(f"Error Occured while loading settings\n Error: {_e}")
            exit()
        
    def loadPaths(self):
        file_path = os.path.abspath(__file__)
        self.directory_path = file_path[:file_path.rfind('/')]
        self.module_directory_path = os.path.join(self.directory_path, "modules")

        # Add the directories for searching modules & other files
        sys.path.append(self.directory_path)
        sys.path.append(self.module_directory_path)

    def loadSessionHandler(self):
        try:
            self.sessionHandler = requests.Session()
            self.sessionHandler.headers.update(self.headers)
            self.sessionHandler.cookies.update(self.cookies)
        
        except Exception as _e:
            self._logger.critical(f"Error Occured while loading session handler\n Error: {_e}")
            exit()

    def isServerActive(self):
        try:
            _resp = self.sessionHandler.get(self._domain, timeout=10)

            if _resp is None:
                raise socket.gaierror("Recieved Null Response")
            else:
                pass
        
        except socket.gaierror as _sge:
            self._logger.critical(f"Host Name Invalid.. Please re-check the domain\n Error: {_sge}")
            exit()
        
        except requests.Timeout as _rte:
            self._logger.warning(f"Host Connection has Timed Out... \n Error: {_rte}")
            exit()

        except Exception as _e:
            self._logger.critical(f" An Unknown Error Occured\n Error: {_e}")
    
    def setup():
        # Setup all the variables & dependencies
        print("Initializing the Crawler Dependencies")
        self.loadLogger()
        self.loadPaths()
        self.loadSettings()
        self.loadSessionHandler()
        self.isServerActive()

    def __init__(self, domain: str = None):
        success = True
        try:
            self._domain = domain
            self.setup()

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
