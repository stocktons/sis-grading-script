import os
from helpers import (
    PATH_TO_ASSESSMENTS_DIR,
    choose_assessment,
    handle_files,
    create_feedback_forms)
from scraper import get_zip_file

def setup_grading():
    """ Conductor function that facilitates easy downloading of assessments and
    setup of grading environment.
    """

    # user chooses assessment in terminal
    assessment_id = choose_assessment()

    # visit Rithm website, download zip file of assessments
    get_zip_file(assessment_id)

    # move, unzip, and organize files
    handle_files(assessment_id)

    # add feedback forms to newly created assessment directory
    create_feedback_forms(assessment_id)

    # open in VSCode
    # code /Users/sarah/Rithm/assessments/r31/test/web-dev-1
    os.system('code {0}{1}'.format(PATH_TO_ASSESSMENTS_DIR, assessment_id))

setup_grading()