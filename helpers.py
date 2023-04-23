import os
import subprocess
import inquirer
import glob
from refs import ASSESSMENT_TO_XPATH_TR

CURRENT_COHORT = os.environ.get('RITHM_COHORT')
PREVIOUS_COHORT = 'r29'

# find current root username for file paths
# returns, among other things, the stdout, which is a bytestring of the username
os_user_output = subprocess.run(['id', '-un'], capture_output=True)
# grab bytestring form stdout and turn into a normal string, stripping newline char
MAC_USER = os_user_output.stdout.decode('utf-8').strip()
# MAC_USER = os.system('id -un') # doesn't return "sarah", returns process code of 0

PATH_TO_ASSESSMENTS_DIR = f"/Users/{MAC_USER}/Rithm/assessments/{CURRENT_COHORT}/"

def choose_assessment():
    """ Display a list of assessments in the terminal for the user to choose from.
    Returns a string of the chosen assessment, like "web-dev-1".
    """

    questions = [
        inquirer.List('assessment',
                message='Choose an assessment',
                choices=list(ASSESSMENT_TO_XPATH_TR.keys()),
        ),
    ]

    answers = inquirer.prompt(questions)
    return answers['assessment']

def handle_files(id):
    """ Takes in chosen assessment id (like 'web-dev-2') to use to create new
    filenames.
    Find latest downloaded .zip file in Downloads directory, extract filename,
    move to assessments directory, unzip, rename unzipped file, delete .zip file,
    search all downloaded student directories for .git and __MACOSX folders and
    remove them.
    """

    # find all .zip files in Downloads directory
    zipped_downloads = glob.glob(f'/users/{MAC_USER}/Downloads/*.zip')
    # of the .zip files, grab the most recent
    # will look like: '/users/sarah/Downloads/submissions-20230423.zip'
    latest_zipped_download = max(zipped_downloads, key=os.path.getctime)

    # wrap file path in quotes in case of spaces, like in
    # '/users/sarah/Downloads/submissions-20230422 (1).zip'
    safe_path_lzd = f"'{latest_zipped_download}'"

    # isolate the part of the path from 'submissions' onward to use as a filename
    # 'submissions-20230422.zip'
    filename_start_index = latest_zipped_download.find("submissions")
    zipped_filename = latest_zipped_download[filename_start_index:]
    safe_zipped_filename = f"'{zipped_filename}'"

    # os.system doesn't like f-strings, so use .format instead
    # mv '/users/sarah/Downloads/submissions-20230423.zip' /Users/sarah/Rithm/assessments/r31/test/
    os.system('mv {0} {1}'.format(safe_path_lzd, PATH_TO_ASSESSMENTS_DIR))

    # unzip /Users/sarah/Rithm/assessments/r31/test/'submissions-20230423.zip' -d /Users/sarah/Rithm/assessments/r31/test/
    os.system('unzip {0}{1} -d {0}'.format(PATH_TO_ASSESSMENTS_DIR, safe_zipped_filename))

    # rm -rf /Users/sarah/Rithm/assessments/r31/test/'submissions-20230423.zip'
    os.system('rm -rf {0}{1}'.format(PATH_TO_ASSESSMENTS_DIR, safe_zipped_filename))

    # rm -rf $(find /Users/sarah/Rithm/assessments/r31/test/web-dev-1 -type d -name __MACOSX)
    os.system('rm -rf $(find {0}{1} -type d -name __MACOSX)'.format(PATH_TO_ASSESSMENTS_DIR, id))

    # rm -rf $(find /Users/sarah/Rithm/assessments/r31/test/web-dev-1 -type d -name .git)
    os.system('rm -rf $(find {0}{1} -type d -name .git)'.format(PATH_TO_ASSESSMENTS_DIR, id))


def create_feedback_forms(id):
    """ Takes in chosen assessment id (like 'web-dev-2') to use to create new
    filenames.
    Find blank feedback template from previous cohort and copy to current assessment
    directory.
    Search all files, create new feedback filenames from student assessment directory
    names.
    Create new blank individualized feedback forms.
    """

    # list all the files in the newly downloaded and unzipped directory. Files are
    # named according to students, and will be captured in a bytestring like
    #  'b"first1-last1\nfirst2-last2\n"'
    file_list_output = subprocess.run([
        'ls', '{0}{1}'
        .format(PATH_TO_ASSESSMENTS_DIR, id)],
        capture_output=True)

    # take the raw output from above, pull out the stdout, convert to a standard
    # string and split into a list on newlines
    file_list = file_list_output.stdout.decode('utf-8').splitlines()

    feedback_filenames = [f'{name}-feedback.md' for name in file_list]

    for filename in feedback_filenames:
        # copy blank feedback.md from previous cohort to new blank, personalized
        # feedback.md for each student, like first-last-feedback.md
        os.system(
            ('cp /Users/{0}/Rithm/assessments/{1}/{2}/feedback.md ' +
            '{3}{2}/{4}')
            .format(MAC_USER, PREVIOUS_COHORT, id, PATH_TO_ASSESSMENTS_DIR, filename)
        )

    # also copy blank feedback.md from previous cohort to new blank feedback.md
    # for use next time and to facilitate blanket changes in this grading cycle
    os.system(
        ('cp /Users/{0}/Rithm/assessments/{1}/{2}/feedback.md ' +
        '{3}{2}')
        .format(MAC_USER, PREVIOUS_COHORT, id, PATH_TO_ASSESSMENTS_DIR)
    )

