import time
import os
import requests
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

LOGIN_USER = os.environ.get("SIS_USERNAME")
LOGIN_PW = os.environ.get('RITHM_STUDENTS_PW')
CURRENT_COHORT = os.environ.get('RITHM_COHORT')
ASSESSMENTS_URL = f'https://{CURRENT_COHORT}.students.rithmschool.com/assessments'
CHROMEDRIVER_API = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"

def split_version(v):  # 116.0.5845.187
    # FIXME: think about how to search for the version in the data better
    version_number_split = v.split(".")
    version_number_start = version_number_split[:3]
    version_number_end = version_number_split[-1]
    s = "."
    v_start_str = s.join(version_number_start)
    v_end_str = str(version_number_end)
    # print(v_start_str, v_end_str)  # 116.0.5845 187
    return v_start_str, v_end_str

def get_chrome_version():
    full_version_name = subprocess.run(
        ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
        capture_output=True,
        text=True,
    ).stdout

    full_version_number = full_version_name.split()[-1]
    # print("get_chrome_version: full version number", full_version_number)
    # print("get_chrome_version: split version number", split_version(full_version_number))
    return split_version(full_version_number)
    # return truncate_version(full_version_number)

# print("get_chrome_version", get_chrome_version())


def get_platform():
    platform = subprocess.run(
        ["arch"], capture_output=True, text=True
    ).stdout.strip()

    if platform == "arm64":
        return "mac-arm64"

    if platform == "x86_64":
        return "mac-x64"

    # TODO: finish this

# print("get platform", get_platform())


def get_chromedriver_url():
    """Get link for the version of chromedriver to match installed version of Chrome.

    Returns the Chrome version and the link to download.

    Sample url: https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/mac-arm64/chromedriver-mac-arm64.zip

    Sample data structure:

    "chromedriver":[
        {
            "platform":"linux64",
            "url":"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/linux64/chromedriver-linux64.zip"
        },
        {
            "platform":"mac-arm64",
            "url":"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/mac-arm64/chromedriver-mac-arm64.zip"
        },
        {
            "platform":"mac-x64",
            "url":"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/mac-x64/chromedriver-mac-x64.zip"
        },
        {
            "platform":"win32",
            "url":"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/win32/chromedriver-win32.zip"
        },
        {
            "platform":"win64",
            "url":"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/win64/chromedriver-win64.zip"
        }
    ],...
    """

    chromedriver_data = requests.get(CHROMEDRIVER_API).json()

    # print("CHROMEDRIVER DATA", chromedriver_data)

    # Find the version you are interested in
    target_version_start, target_version_end = get_chrome_version()
    target_version = f"{target_version_start}.{target_version_end}"
    print("target version start", target_version_start)
    print("target version end", target_version_end)
    platform = get_platform()
    # breakpoint()
    chromedriver_data["versions"].reverse()
    for version_info in chromedriver_data["versions"]:
        # breakpoint()
        v_start, v_end = split_version(version_info["version"])
        if v_start == target_version_start and v_end < target_version_end:
            breakpoint()
            # Found the version, now search for the "platform" in "chromedriver"
            for driver_info in version_info["downloads"]["chromedriver"]:
                if driver_info["platform"] == platform:

                    url = driver_info["url"]
                    print("target version string in get_chromedriver_url")
                    print(f"URL for {platform} platform in version {target_version}: {url}")
                    return {"version": target_version, "url": url}
            else:
                # Handle the case where the platform was not found
                print(f"No URL found for {platform} platform in version {target_version}")
            break
    else:
        # Handle the case where the target version was not found
        print(f"Version {target_version} not found in the data")

# get_chromedriver_url()


def download_chromedriver(chunk_size=128):
    os.system("rm ~/Projects/sis-grading-script/chromedriver")
    chromedriver_data = get_chromedriver_url()
    url = chromedriver_data["url"]
    version = chromedriver_data["version"]
    output_path = f"chromedriver-{version}.zip"

    r = requests.get(url, stream=True)
    with open(f'./{output_path}', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

    os.system(f"unzip -qq /Users/Sarah/Projects/sis-grading-script/{output_path}")
    os.system(f"mv ~/Projects/sis-grading-script/chromedriver-mac-arm64/chromedriver ~/Projects/sis-grading-script/chromedriver")
    os.system(f"touch ~/Projects/sis-grading-script/chromedriver.txt")
    os.system(f"echo 'Chromedriver version: {version}' > ~/Projects/sis-grading-script/chromedriver.txt")
    os.system(f"rm -rf ~/Projects/sis-grading-script/chromedriver-mac-arm64")
    os.system(f"rm -rf ~/Projects/sis-grading-script/{output_path}")

download_chromedriver()


def initialize_selenium():
    """Get a working driver for Chrome for Selenium."""

    # try:
    #     print("trying automatic download of chromedriver")
    #     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    #     return driver
    # except:
    #     print("Please update ChromeDriverManager")

    try:
        print("trying local version of chromedriver")
        op = webdriver.ChromeOptions()
        ser = Service("./chromedriver")
        driver = webdriver.Chrome(service=ser, options=op)
        return driver
    except:
        print("Please update local version of Chromedriver")

# get_latest_chromedriver()
# get_chrome_version()

def get_zip_file(id):
    """Use Selenium to download zip file from Rithm website.

    Takes in chosen assessment id (like 'web-dev-2') to use to target links.
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
    ser = Service("/Users/sarah/Projects/sis-grading-script/chromedriver-119.0.6045.123")

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
    """Print results of jasmine tests to terminal.

    Takes in a list of .html file paths, and opens them in Chrome to run the
     Jasmine tests. Checks results for each test, and prints synopsis to terminal.
     """
    print("running tests")

        ## old code, uncommented for 7/23 bug:
    # op = webdriver.ChromeOptions()

    ## new code, adapted for 7/23 bug:
    # ser = Service("/Users/sarah/Projects/sis-grading-script/chromedriver")

    # driver = webdriver.Chrome(service=ser, options=op)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
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

# `arch` in Terminal (or `uname -m`)
#
# The output will either be "arm64" for Apple Silicon (ARM-based) or "x86_64" for Intel (x86_64) architecture.
# {
#     'timestamp': '2023-09-07T03:08:43.543Z',
#     'channels': {
#         'Stable': {
#             'channel': 'Stable',
#             'version': '116.0.5845.96',
#             'revision': '1160321',
#             'downloads': {
#                 'chrome': [
#                     {
#                         'platform': 'linux64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chrome-linux64.zip'
#                     },
#                     {
#                         'platform': 'mac-arm64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/mac-arm64/chrome-mac-arm64.zip'
#                     },
#                     {
#                         'platform': 'mac-x64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/mac-x64/chrome-mac-x64.zip'
#                     },
#                     {
#                         'platform': 'win32',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/win32/chrome-win32.zip'
#                     },
#                     {
#                         'platform': 'win64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/win64/chrome-win64.zip'
#                     }
#                 ],
#                 'chromedriver': [
#                     {
#                         'platform': 'linux64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chromedriver-linux64.zip'
#                     },
#                     {
#                         'platform': 'mac-arm64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/mac-arm64/chromedriver-mac-arm64.zip'
#                     },
#                     {
#                         'platform': 'mac-x64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/mac-x64/chromedriver-mac-x64.zip'
#                     },
#                     {
#                         'platform': 'win32',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/win32/chromedriver-win32.zip'
#                     },
#                     {
#                         'platform': 'win64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/win64/chromedriver-win64.zip'
#                     }
#                 ]
#             }
#         },
#         'Beta': {
#             'channel': 'Beta',
#             'version': '117.0.5938.48',
#             'revision': '1181205',
#             'downloads': {
#                 'chrome': [
#                     {
#                         'platform': 'linux64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.48/linux64/chrome-linux64.zip'
#                     },
#                     {
#                         'platform': 'mac-arm64',
#                         'url': 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.48/mac-arm64/chrome-mac-arm64.zip'
#                     }]}}}} # etc...






# {
#   "timestamp":"2023-09-07T03:08:43.548Z",
#   "versions":[
#       {
#           "version":"113.0.5672.0",
#           "revision":"1121455",
#           "downloads":{
#               "chrome":[
#                   {
#                       "platform":"linux64",
#                       "url":"https:.....
#                     },
#                     {
#                       "platform":"mac-arm64",
#                       "url":"https:.....
#                     }...],
#                 "chrome-driver": [
#                                    {
#                       "platform":"linux64",
#                       "url":"https:.....
#                     },
#                     {
#                       "platform":"mac-arm64",
#                       "url":"https:.....
#                     }...
#                 ]
#                 }}]}

# data["versions"] is a list of objects with "version" keys
# search this to locate the value that matches the current version of
# chrome. Grab the index of that dictionary. Once found, we are at
# data["versions"][idx]["downloads"]["chromedriver"][idx-of-platform]["url"]
# use the index() method
# data["versions"].index