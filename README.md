# Go-Grawler

This is a crawler that will read all the urls that are present in the website's surface

## To-Achieve
1. Ablity to perform Invasive & Non-Invasive searching \
2. Ability to fetch results based on extensions \

## Developer-Notes
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
4. Need to fetch all the urls by scraping the wesbite. Any filters or features should be added in runner.py(Crawler must crawl all the sites)

## Version-1.1
1. Ability to prevent the crawler from accessing the dis-allowed urls.
2. Ability to change the user agent according to the information present in the robots.txt (intelligent mode)
3. Should be able to add custom timeouts to the crawler to avoid being blocked.
4. Treating urls like objects so that further operations can be added
