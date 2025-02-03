#!/bin/python3
import requests
import socket
import json
import logging
import urllib
import time

def requester(url=None, headers=None, cookies=None, method="GET", allow_redirects=False, timeout=None, attempts=1, sessionHandler=None, sleeptime=0.4, logger=None):
    # We need to send in the headers & all other information for the request to be sent
    _resp = None
    if not logger:
        logger = logging.getLogger()
    try:
        if attempts < 3:
            if not sessionHandler:
                sessionHandler = requests.Session()

            _resp = sessionHandler.request(method=method, url=url, headers=headers,
                cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
                
    except requests.ConnectTimeout as _rct:
        logger.warning("Connection Timed Out")
        if timeout:
            timeout += 1
            return requester(url, headers, cookies, method, allow_redirect, timeout, attempts+1)
        else:
            # No timeout(max possible time) defined so exiting
            return _resp
        
    except requests.exceptions.RequestException as _rere:
        logger.warning(f"Error sending the request: {_rere}")
        
    except socket.gaierror as _sge:
        logger.warning(f"Unable to find the host: {url}\n Error is: {_sge}")
    
    except Exception as _e:
        logger.warning("Error occured while sending the request\n Error: ", _e)
        logger.info(f"Retrying to send the packet again {attempts}")
        return requester(url, headers, cookies, method, allow_redirect, timeout, attempts+1)
    
    finally:
        return _resp

def getContentType(response):
    for header in response.headers:
        if header.lower() == "content-type":
            return response.headers[header]
    return None

def saveFile(file_path: str = None, json_data: dict = dict()):
    try:
        print("Successful")
        with open(file_path, 'w') as file:
            file.write(json.dumps(json_data, indent=4))
        return True
    
    except Exception as _e:
        print("Error Occured While Saving the File.\n Error: ")
        return False

def fetchPathAndParams(url):
    # Return the path of the url
    _path = url.split('/', 3)
    # https://example.com/path1/path2/file.ext -> ["https:", "", "example.com", "path1/path2/file.ext"]
    return _path[3]
