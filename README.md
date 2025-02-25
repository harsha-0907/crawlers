# Grawler (1.1)

**Grawler** is an *evolving* web crawler designed to explore and extract URLs associated with a given domain.  
It simplifies the process of discovering and analyzing site structures, offering efficiency and flexibility for various use cases.  

**Grawler** is built to handle crawling across multiple levels of URLs, with a focus on speed and accuracy.  
As it continues to *evolve*, it is set to become a valuable tool for developers looking for a reliable solution for web crawling and data collection.


## Functionality
1. Ablity to perform Invasive & Non-Invasive searching 
2. Ability to fetch results based on extensions


## Steps to Install & Run the Project
1. Git clone the repo: `git clone https://github.com/harsha-0907/crawlers.git` 
2. Create a Virtual Environment  `python3 -m venv .venv`    
3. Activate the Virtual Environment `source .venv/bin/activate` for linux & `venv\Scripts\activate` for windows systems 
4. Install the necessary packages  `pip install -r requirments.txt`
5. Run the Program with the command `python3 runner.py`

## Note
1. If you need to modify any default settings for the tool, head out to the settings.json for any changes


## Change-log
1. Updated the logging system to cover all critical areas
2. Modified the structure, using settings.json for all tool related settings
3. Modified the BFS to DFS for granular control over depth
4. Added time-bound crawling of webpages to ensure that crawling doesn't run for indefinitely
5. Fixed minor bugs present in Version 1.0


### You will be getting your results!!!


#### Stay Tuned For Version 1.2
