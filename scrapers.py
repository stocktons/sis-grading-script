import time
import os
import requests
import subprocess
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

LOGIN_USER = os.environ.get("SIS_USERNAME")
LOGIN_PW = os.environ.get('RITHM_STUDENTS_PW')
CURRENT_COHORT = os.environ.get('RITHM_COHORT')
ASSESSMENTS_URL = (
    f'https://{CURRENT_COHORT}.students.rithmschool.com/assessments')


def get_zip_file(id):
    """Use Selenium to download zip file from Rithm website.

    Takes in chosen assessment id (like 'web-dev-2') to use to target links.
    Use Selenium to visit Rithm website, go to the proper assessment, and
    click "Claim & Download" button.
    """

    driver = webdriver.Chrome()
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
