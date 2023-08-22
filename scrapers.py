from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv

load_dotenv()




LOGIN_USER = 'sarah'
LOGIN_PW = os.environ.get('RITHM_STUDENTS_PW')
CURRENT_COHORT = os.environ.get('RITHM_COHORT')
ASSESSMENTS_URL = f'https://{CURRENT_COHORT}.students.rithmschool.com/assessments'


def get_zip_file(id):
    """ Takes in chosen assessment id (like 'web-dev-2') to use to target links.
    Use Selenium to visit Rithm website, go to the proper assessment, and
    click "Claim & Download" button.
    """




#####
# Auto-update broke 7/23, workaround from https://github.com/GoogleChromeLabs/chrome-for-testing/issues/30#issuecomment-1643741069
# ChromeOptions options = new ChromeOptions();
# options.setBinary("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome");
# WebDriver driver = new ChromeDriver(options);
#####

    # used to need these, seems like it works now without
    # ser = Service('/home/stocktons/chromedriver')
    ## old code, uncommented for 7/23 bug:
    op = webdriver.ChromeOptions()

    ## new code, adapted for 7/23 bug:
    ser = Service("/Users/sarah/Projects/sis-grading-script/chromedriver")

    driver = webdriver.Chrome(service=ser, options=op)
    # Make sure latest version is installed
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    print("MADE IT PAST DRIVER", driver)
    driver.get(ASSESSMENTS_URL)

    # locate username & password fields and login button
    username_input = '//*[@id="id_username"]'
    password_input = '//*[@id="id_password"]'
    login_button = '/html/body/div/div/form/div[3]/button'

    # fill out fields and click login
    driver.find_element(By.XPATH, username_input).send_keys(LOGIN_USER)
    driver.find_element(By.XPATH, password_input).send_keys(LOGIN_PW)
    driver.find_element(By.XPATH, login_button).click()

    time.sleep(1)

    # go to assessment url
    driver.get(f'{ASSESSMENTS_URL}/{id}')

    time.sleep(2)

    # click claim & download button
    claim_and_download_button = '/html/body/div/form/h5/span/button[1]'
    driver.find_element(By.XPATH, claim_and_download_button).click()

    # wait for download to finish
    time.sleep(3)

    # Selenium now manages this automatically, but it's good practice to be explicit here
    driver.quit()

def make_jasmine_report(html_files):
    """ Takes in a list of .html file paths, and opens them in Chrome to run the
     Jasmine tests. Checks results for each test, and prints synopsis to terminal.
     """
    print("running tests")

        ## old code, uncommented for 7/23 bug:
    op = webdriver.ChromeOptions()

    ## new code, adapted for 7/23 bug:
    ser = Service("/Users/sarah/Projects/sis-grading-script/chromedriver")

    driver = webdriver.Chrome(service=ser, options=op)
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    print("\x1b[6;30;43mRUNNING JASMINE TESTS... \x1b[0m")
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
                print(f'    \x1b[0;31;49m ❌ {msg.text}\x1b[0m')
        else:
            # 32 is green font
            print(f'\x1b[0;32;49m{path}\x1b[0m')

    driver.quit()
