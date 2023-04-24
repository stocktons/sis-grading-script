## Needed environment variables for script to run:

- RITHM_STUDENTS_PW -- password for Rithm website login
- CURRENT_COHORT -- current cohort

## variables to change for your own setup:

### scraper.py
- LOGIN_USER -- your Rithm website login username

### helpers.py
- PREVIOUS_COHORT -- a previous cohort with feedback templates you want to copy
- in build_paths(), build your skeleton path to how your filesystem is set up (WSL users see the note about Chrome and a maybe-surprising side-effect this will have on your Downloads path below).

## WSL
If you're on WSL, you'll need to install Google Chrome on the Linux side of your machine, and the matching Chromedriver. This article has a good outline: [https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2](https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2)

NOTE: when this Chrome downloads something for the first time via Selenium, it will create a new Downloads folder for you on the WSL side of your machine!  

## Chromedriver
Both Mac and WSL will need the matching version of Chromedriver for their current version of Google Chrome: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)