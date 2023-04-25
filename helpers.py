import os
import subprocess
import inquirer
import glob
from refs import ASSESSMENT_TO_XPATH_TR

CURRENT_COHORT = os.environ.get('RITHM_COHORT')
PREVIOUS_COHORT = 'r29'

def determine_os_and_find_username():
    """Ask the current OS what it is, find the current user's name(s) to determine
    whether to use file paths for WSL or for MacOS. Returns tuple of one or two
    usernames, depending on OS.
    """

    # Will be "Darwin" for MacOS and "Linux" for WSL/Linux
    os_name_data = subprocess.run(['uname'], capture_output=True)
    os_name = os_name_data.stdout.decode('utf-8').strip()

    if os_name == "Linux":
        # linux_username_data will be like:
        # CompletedProcess(args=['whoami'], returncode=0, stdout=b'stocktons\n', stderr=b'')
        linux_username_data = subprocess.run(['whoami'], capture_output=True)
        # Grab "stocktons"
        linux_username = linux_username_data.stdout.decode('utf-8').strip()
        # Windows truncates the Linux username to 5 characters for its filepaths
        windows_username = linux_username[:5] # "stock"

        return {'os': 'linux', 'username': linux_username, 'windows_username': windows_username}

    if os_name == "Darwin":
        # mac_username_data will be like:
        # CompletedProcess(args=['id', '-un'], returncode=0, stdout=b'sarah\n', stderr=b'')
        mac_username_data= subprocess.run(['id', '-un'], capture_output=True)
        # grab "sarah". not like that. ugh...
        mac_username = mac_username_data.stdout.decode('utf-8').strip()

        return {'os': 'mac', 'username': mac_username}

def build_paths():
    """ """
    system_data = determine_os_and_find_username()
    os_name = system_data['os']
    os_user = system_data['username']
    # not needed in current implementation, but leaving in case of future uses
    # windows_username = system_data.get('windows_username')

    if os_name == 'linux':
        base_ass_path = f'/home/{os_user}/rithm/assessments/'
        ass_path = f'{base_ass_path}{CURRENT_COHORT}/'
        downlds_path = f'/home/{os_user}/Downloads/'
    elif os_name == 'mac':
        base_ass_path = f'/Users/{os_user}/Rithm/assessments/'
        ass_path = f'{base_ass_path}{CURRENT_COHORT}/'
        downlds_path = f'/Users/{os_user}/Downloads/'
    else:
        raise ValueError(
            "Only MacOS and WSL/Linux here, please. Take your fancypants OS elsewhere."
        )

    return (base_ass_path, ass_path, downlds_path)

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

def handle_files(downloads_path, assessments_path, id):
    """ Takes in path to downloads directory, path to assessments directory,
    and chosen assessment id (like 'web-dev-2') to find files and to create new
    filenames.
    Find latest downloaded .zip file in Downloads directory, extract filename,
    move to assessments directory, unzip, rename unzipped file, delete .zip file,
    search all downloaded student directories for .git and __MACOSX folders and
    remove them.
    """

    # find all .zip files in Downloads directory
    zipped_downloads = glob.glob(f'{downloads_path}*.zip')
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
    # move downloaded .zip file from downloads directory to assessments directory
    os.system('mv {0} {1}'.format(safe_path_lzd, assessments_path))

    # unzip downloaded .zip file
    os.system('unzip {0}{1} -d {0}'.format(assessments_path, safe_zipped_filename))

    # remove now unneeded .zip file
    os.system('rm -rf {0}{1}'.format(assessments_path, safe_zipped_filename))

    # remove commonly-found unneeded files and directories
    os.system('rm -rf $(find {0}{1} -type d -name __MACOSX)'.format(assessments_path, id))
    os.system('rm -rf $(find {0}{1} -type d -name .git)'.format(assessments_path, id))
    os.system('rm -rf $(find {0}{1} -type d -name .vscode)'.format(assessments_path, id))
    os.system('rm -rf $(find {0}{1} -type d -name __pycache__)'.format(assessments_path, id)) # TODO: if found, add a line to feedback.md for that student?!

    # TODO: requirements.txt finder, if found, create venv, activate, install requirements, deactivate
    # TODO: scan for node modules, if found, install

def create_feedback_forms(base_assessments_path, assessments_path, id):
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
        .format(assessments_path, id)],
        capture_output=True)

    # take the raw output from above, pull out the stdout, convert to a standard
    # string and split into a list on newlines
    file_list = file_list_output.stdout.decode('utf-8').splitlines()

    feedback_filenames = [f'{name}-feedback.md' for name in file_list]

    for filename in feedback_filenames:
        # copy blank feedback.md from previous cohort to new blank, personalized
        # feedback.md for each student, like first-last-feedback.md
        os.system(
            ('cp {0}{1}/{2}/feedback.md ' +
            '{3}{2}/{4}')
            .format(base_assessments_path, PREVIOUS_COHORT, id, assessments_path, filename)
        )

    # also copy blank feedback.md from previous cohort to new blank feedback.md
    # for use next time and to facilitate blanket changes in this grading cycle
    os.system(
        ('cp {0}{1}/{2}/feedback.md ' +
        '{3}{2}')
        .format(base_assessments_path, PREVIOUS_COHORT, id, assessments_path)
    )

