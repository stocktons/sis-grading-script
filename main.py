import os
from helpers import (
    build_paths,
    choose_assessment,
    handle_files,
    get_student_names,
    create_feedback_forms,
    find_format_run_jasmine_tests,
    setup_flask_apps)
from scrapers import get_zip_file

# TODO: scan for node modules, if found, install
# TODO: run all types of test suites automatically (Jasmine nearly done)

def setup_grading():
    """ Conductor function that facilitates easy downloading of assessments and
    setup of grading environment.
    """

    # determine os, usernames(s), and create downloads and assessments paths
    # base_assessments_path is like /Users/sarah/Rithm/assessments
    # assessments_path is like /Users/sarah/Rithm/assessments/r31
    base_assessments_path, assessments_path, downloads_path, curric_path = build_paths()

    # user chooses assessment in terminal
    assessment_id = choose_assessment()

    # visit Rithm website, download zip file of assessments
    get_zip_file(assessment_id)

    # move, unzip, and organize files
    handle_files(downloads_path, assessments_path, assessment_id)

    student_names = get_student_names(assessments_path, assessment_id)

    # add feedback forms to newly created assessment directory
    create_feedback_forms(student_names, base_assessments_path, assessments_path, assessment_id)

    breakpoint()

    # find any Jasmine tests and run them
    find_format_run_jasmine_tests(curric_path, assessments_path, assessment_id)

    # find any Flask apps, start them up, and open in Chrome
    setup_flask_apps(assessment_id, assessments_path, student_names)

    # open assessments in VSCode
    # code /Users/sarah/Rithm/assessments/r31/test/web-dev-1
    os.system('code {0}/{1}'.format(assessments_path, assessment_id))

setup_grading()


