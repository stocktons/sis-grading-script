from selenium import webdriver
# from selenium.webdriver.chrome.service import Service # no longer needed?
from selenium.webdriver.common.by import By
import time
import os
from helpers import CURRENT_COHORT
from refs import ASSESSMENT_TO_XPATH_TR
from dotenv import load_dotenv

load_dotenv()

# used to need these, seems like it works now without
# ser = Service('/Users/Sarah/Downloads/chromedriver_mac64/chromedriver')
# op = webdriver.ChromeOptions()
# driver = webdriver.Chrome(service=ser, options=op)
driver = webdriver.Chrome()

LOGIN_USER = "sarah"
LOGIN_PW = os.environ.get("RITHM_STUDENTS_PW")
ASSESSMENTS_URL = f"https://{CURRENT_COHORT}.students.rithmschool.com/assessments/"


def get_zip_file(id):
    """ Takes in chosen assessment id (like 'web-dev-2') to use to target links.
    Use Selenium to visit Rithm website, go to the proper assessment, and
    click "Claim & Download" button.
    """

    driver.get(ASSESSMENTS_URL)
    time.sleep(3)

    # locate username & password fields and login button
    username_input = '//*[@id="id_username"]'
    password_input = '//*[@id="id_password"]'
    login_button = '/html/body/div/div/form/div[3]/button'

    # fill out fields and click login
    driver.find_element(By.XPATH, username_input).send_keys(LOGIN_USER)
    driver.find_element(By.XPATH, password_input).send_keys(LOGIN_PW)
    driver.find_element(By.XPATH, login_button).click()

    # visit that assessment page
    assessment_link = ('/html/body/div/table/tbody/' +
                       f'tr[{ASSESSMENT_TO_XPATH_TR[id]}]/td[3]/div[1]/b/a')

    driver.find_element(By.XPATH, assessment_link).click()

    time.sleep(2)

    # click claim & download button
    claim_and_download_button = '/html/body/div/form/h5/span/button[1]'
    driver.find_element(By.XPATH, claim_and_download_button).click()

    # wait for download to finish
    time.sleep(5)

    # TODO: this also seems unneeded in latest version (exciting!), investigate
    driver.quit()