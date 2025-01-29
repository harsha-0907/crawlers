# Go-Grawler

This is a crawler that will read all the urls that are present in the website's surface

## To-Achieve
1. Ablity to perform Invasive & Non-Invasive searching \
2. Ability to fetch reslts based on extensions \

## Developer-Notes
1. Use Breadth First Search to crawl all the webpages \
2. Use the following approach while running the modules:
    ```
    crawler
    |-  modules
    |-  |-  helper.py   # Any helper functions
    |-  |-  cralwer_in_robots.py    # To perform a specific functionality    
    |-  crawler.py  # Runs all the modules
    |-  runner.py   # Runs the crawler (Done to avoid executing the whole process twice)
    ```
3. Must be able to add paths at the begining of the files that need to be imported at the first & delete at the last