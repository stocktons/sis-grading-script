# TODO: move to scraper.py, rename scrapers.py

from selenium import webdriver
from selenium.webdriver.common.by import By

def make_jasmine_report(html_files):
    """ Takes in a list of .html file paths, and opens them in Chrome to run the
     Jasmine tests. Checks results for each test, and prints synopsis to terminal.
     """

    driver = webdriver.Chrome()

    for file in html_files:
        path = f'file://{file}'
        driver.get(path)

        if len(driver.find_elements(By.CLASS_NAME, "jasmine-failed")) > 0:
            # 31 is red font, 49 is no background
            print(f'\x1b[0;31;49m{path}\x1b[0m')
            failure_messages = driver.find_elements(
                By.CSS_SELECTOR,
                ".jasmine-description > a:nth-child(2)"
            )
            for msg in failure_messages:
                print(f'''    \x1b[0;31;49m ❌ {msg.text}\x1b[0m''')
        else:
            # 32 is green font
            print(f'\x1b[0;32;49m{path}\x1b[0m')

    driver.quit()


# make_jasmine_report(['/Users/sarah/Rithm/assessments/r31/flask-1/michael-herman/flask-1/scrambledPalindromeCheck.html', '/Users/sarah/Rithm/assessments/r31/flask-1/michael-herman/flask-1/almostIdentical.html', '/Users/sarah/Rithm/assessments/r31/flask-1/timothy-sukamtoh/flask-1 - Copy/scrambledPalindromeCheck.html', '/Users/sarah/Rithm/assessments/r31/flask-1/timothy-sukamtoh/flask-1 - Copy/almostIdentical.html', '/Users/sarah/Rithm/assessments/r31/flask-1/russell-jones/static/scrambledPalindromeCheck.html', '/Users/sarah/Rithm/assessments/r31/flask-1/russell-jones/static/almostIdentical.html', '/Users/sarah/Rithm/assessments/r31/flask-1/steven-zheng/flask-1/scrambledPalindromeCheck.html', '/Users/sarah/Rithm/assessments/r31/flask-1/steven-zheng/flask-1/almostIdentical.html', '/Users/sarah/Rithm/assessments/r31/flask-1/meeran-kim/flask-1/scrambledPalindromeCheck.html', '/Users/sarah/Rithm/assessments/r31/flask-1/meeran-kim/flask-1/almostIdentical.html'])