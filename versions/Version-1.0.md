# Grawler (Version 1.0)

## Functionality
1. Ablity to perform Invasive & Non-Invasive searching 
2. Ability to filter urls based on the extensions


### Advantages
1. A Bare-Metal approach to crawling
2. Easier to understand & Simple to modify the code for any specifics

### Dis-Advantages
1. The webpage crawler is just a mess, need to sort the issue with clear cut diagrams & workflows -> (3)
2. Breadth First Approach used to crawl website that can't be controlled (Req) -> (1)
3. Unable to assign weightage to urls to ensure that optimal use of resources can be done (4)
4. Unable to treat urls as objects for effective indexing. (Req) -> (2)
5. Proper Logging should be available & status of the scan should be available


## Developer-Notes (Version 1.0)
1. Use Breadth First Search to crawl all the webpages \
2. Use the following approach while running the modules:\
    ```
    crawler
    |-  modules
    |-  |-  helper.py   # Any helper functions
    |-  |-  cralwer_in_robots.py    # To perform a specific functionality    
    |-  crawler.py  # Runs all the modules
    |-  runner.py   # Runs the crawler (Done to avoid executing the whole process twice)
    ```
3. Modules must be dependent on the runner.py. (So as to avoid problems with ModuleNotFound Errors)\
4. Need to fetch all the urls by crawling the wesbite. Any filters or features should be added in runner.py(Crawler must crawl all the sites)