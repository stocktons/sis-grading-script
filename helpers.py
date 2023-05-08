import os
import subprocess
import inquirer
import glob
from refs import ASSESSMENT_TO_XPATH_TR
from scrapers import make_jasmine_report

CURRENT_COHORT = os.environ.get('RITHM_COHORT')
PREVIOUS_COHORT = 'r29'

def determine_os_and_find_username():
    """Ask the current OS what it is, find the current user's name(s) to determine
    whether to use file paths for WSL or for MacOS. Returns tuple of one or two
    usernames, depending on OS.
    """
    # print("determine_os_and_find_username")
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
    # print("build_paths")
    system_data = determine_os_and_find_username()
    os_name = system_data['os']
    os_user = system_data['username']
    # not needed in current implementation, but leaving in case of future uses
    # windows_username = system_data.get('windows_username')

    if os_name == 'linux':
        base_ass_path = f'/home/{os_user}/rithm/assessments'
        ass_path = f'{base_ass_path}/{CURRENT_COHORT}'
        downlds_path = f'/home/{os_user}/Downloads'
        curric_path = f'/home/{os_user}/rithm/rithm-apps/curric/assessments'
    elif os_name == 'mac':
        base_ass_path = f'/Users/{os_user}/Rithm/assessments'
        ass_path = f'{base_ass_path}/{CURRENT_COHORT}/test'
        downlds_path = f'/Users/{os_user}/Downloads'
        curric_path = f'/Users/{os_user}/Rithm/rithm-apps/curric/assessments'
    else:
        raise ValueError(
            "Only MacOS and WSL/Linux here, please. Take your fancypants OS elsewhere."
        )

    return (base_ass_path, ass_path, downlds_path, curric_path)

def choose_assessment():
    """ Display a list of assessments in the terminal for the user to choose from.
    Returns a string of the chosen assessment, like "web-dev-1".
    """
    # print("choose_assessment")
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
    search all downloaded student directories for commonly-found unneeded dirs
    and files and remove them.
    """

    # print("handle_files", downloads_path, assessments_path, id)
    # find all .zip files in Downloads directory
    zipped_downloads = glob.glob(f'{downloads_path}/*.zip')
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

    # os.system doesn't like f-strings, so use .format instead TODO: I don't think
    # that's actually accurate, seems to be working in other places now. Refactor
    # because .format() is annoying
    # move downloaded .zip file from downloads directory to assessments directory
    os.system('mv {0} {1}'.format(safe_path_lzd, assessments_path))

    # unzip downloaded .zip file. -qq flag suppresses output from command
    os.system('unzip -qq {0}/{1} -d {0}'.format(assessments_path, safe_zipped_filename))

    # remove now unneeded .zip file
    os.system('rm -rf {0}/{1}'.format(assessments_path, safe_zipped_filename))

    # remove commonly-found unneeded files and directories
    os.system('rm -rf $(find {0}/{1} -type d -name __MACOSX)'.format(assessments_path, id))
    os.system('rm -rf $(find {0}/{1} -type d -name .vscode)'.format(assessments_path, id))
    find_alert_and_remove_unwanted_items(assessments_path, id, [('.git', 'd'), ('venv', 'd'), ('node_modules', 'd')])
    # os.system('rm -rf $(find {0}/{1} -type d -name .git)'.format(assessments_path, id))


def get_student_names(assessments_path, id):
    """ Takes in the path to a particular cohort's assessments folder and an
    assessment id. Generates a list of student names like:
    ['first-last1', 'first-last2', 'first-last3'].
    NOTE: This is very naïve and only works as expected if this is run on a
    freshly-unzipped directory that ONLY has student-name folders in it.
    """
    # print("get_student_names", assessments_path, id)

    # Pull student names from downloaded files. Files are
    # named according to students, and will be captured in a bytestring like
    #  'b"first1-last1\nfirst2-last2\n"'
    file_list_output = subprocess.run(['ls', f'{assessments_path}/{id}'], capture_output=True)

    # take the raw output from above, pull out the stdout, convert to a standard
    # string and split into a list on newlines
    student_names = file_list_output.stdout.decode('utf-8').splitlines()

    return student_names

def create_feedback_forms(student_names, base_assessments_path, assessments_path, id):
    """ Takes in chosen assessment id (like 'web-dev-2') to use to create new
    filenames.
    Find blank feedback template from previous cohort and copy to current assessment
    directory.
    Search all files, create new feedback filenames from student assessment directory
    names.
    Create new blank individualized feedback forms.
    """
    # print("create_feedback_forms", student_names, base_assessments_path, assessments_path, id)
    feedback_filenames = [f'{name}-feedback.md' for name in student_names]

    for filename in feedback_filenames:
        # copy blank feedback.md from previous cohort to new blank, personalized
        # feedback.md for each student, like first-last-feedback.md
        os.system(
            ('cp {0}/{1}/{2}/feedback.md ' +
            '{3}/{2}/{4}')
            .format(base_assessments_path, PREVIOUS_COHORT, id, assessments_path, filename)
        )

    # also copy blank feedback.md from previous cohort to new blank feedback.md
    # for use next time and to facilitate blanket changes in this grading cycle
    os.system(
        ('cp {0}/{1}/{2}/feedback.md ' +
        '{3}/{2}')
        .format(base_assessments_path, PREVIOUS_COHORT, id, assessments_path)
    )

def setup_jasmine_tests(curric_path, assessments_path, assessment_id):
    """ Takes in:
     - assessment id like 'web-dev-2',
     - the path to the current cohort's assessments, like '/Users/sarah/Rithm/assessments/r31'

    Finds all Jasmine tests in the solution folder of the current assessment.

    If no Jasmine tests found, returns False and aborts further Jasmine-test-related actions.

    Otherwise, finds the name of the directory students have stored their Jasmine tests.
    Copies the Rithm solution tests to their directory.
    Renames the "it" or "test" statements in the Rithm solution copy to be like
    'it("rithm test: sorts the array correctly"...' to differentiate whether it's
    a Rithm test or a student test that fails in the final printout.
    Adds a <script> tag linking to the Rithm solution copy to the bottom of their .html file.
    """
    # print("setup_jasmine_tests", curric_path, assessment_id, assessments_path )

    # find all *.test.js in curric solution
    results = subprocess.run(f'find {curric_path}/{assessment_id}/solution -name "*.test.js"', shell=True, capture_output=True)
    file_list = results.stdout.decode('utf-8').splitlines()
    # print("path", f"{curric_path}/{assessment_id}/solution")
    # print("files", file_list)
    if len(file_list) == 0:
        print("no jasmine tests to run")
        return False

    # find the name of the folder that has .test.js files for each student
    # https://unix.stackexchange.com/questions/111949/get-list-of-subdirectories-which-contain-a-file-whose-name-contains-a-string
    # The below finds all files below the given directory that are regular files
    # (-type f) and have .test.js at the end of their name (-name '*.test.js').
    # Next, sed removes the file name, leaving just the directory name. Then, the
    # list of directories is sorted (sort) and duplicates removed (-u).
    # The sed command consists of a single substitute. It looks for matches to the
    # regular expression /[^/]+$ and replaces anything matching that with nothing.
    # The dollar sign means the end of the line. [^/]+' means one or more characters
    # that are not slashes. Thus, /[^/]+$ means all characters from the final slash
    # to the end of the line. In other words, this matches the file name at the end
    # of the full path. Thus, the sed command removes the file name, leaving unchanged
    # the name of directory that the file was in.
    # replace -E with -r for non-Mac
    # NEED to make them raw strings with r"...". Can combine with f-string like fr"..."

    test_directories_raw = subprocess.run(f"find {assessments_path}/{assessment_id} -type f -name '*.test.js' | sed -E 's|/[^/]+$||' |sort -u", shell=True, capture_output=True)
    test_directories = test_directories_raw.stdout.decode('utf-8').splitlines()
    # print("TEST DIRECTORIES", test_directories)

    # dir: /Users/sarah/Rithm/assessments/r31/test-web-dev-1/student-name/web-dev-1
    for dir in test_directories:

        # file: /Users/sarah/Rithm/rithm-apps/curric/assessments/web-dev-1/solution/sortAlmostSorted.test.js
        for file in file_list:

            # filename: 'sortAlmostSorted.test.js'
            filename = file.split('/')[-1]

            # test_name: 'sortAlmostSorted'
            test_name = filename.split(".")[0]

            # new_test_file_path: /Users/sarah/Rithm/assessments/r31/test-web-dev-1/student-name/web-dev-1/rithm-sortAlmostSorted.test.js
            new_test_file_path = f'{dir}/rithm-{filename}'
            subprocess.run(f'cp {file} "{new_test_file_path}"', shell=True) #double quotes for student paths with spaces

            # find all it(" and test(" occurrences and replace with it("rithm test:
            # TODO: use a regex OR to combine into one
            # TODO: also need to account for it(' ..... ') with single quotes
            subprocess.run(fr'sed -i "" "s/it(\"/it(\"rithm test: /g" "{new_test_file_path}"', shell=True)
            subprocess.run(fr'sed -i "" "s/test(\"/it(\"rithm test: /g" "{new_test_file_path}"', shell=True)

            # line breaks and weird indentations are part of the command, don't change
            # extra "" around html file name to account for student paths with spaces
            subprocess.run(fr"""sed -i '' '\|.*</body>.*| i\
    <script src="rithm-{filename}"></script>
            ' "{dir}/{test_name}.html"
            """, shell=True)


def find_jasmine_tests(assessment_path, assessment_id):
    """ Takes in a path like '/Users/sarah/Rithm/assessments/r31/', and an assessment_id
    like 'web-dev-2'. Finds and returns all .html files that contain Jasmine tests.
    """
    # print("find_jasmine_tests", assessment_path, assessment_id)
    # look in the current assessment folder for all .html files.
    # Search those .html files recursively (-r) for the word (-w) "jasmine-core"
    # jasmine-core is part of the CDN link and therefore is a good identifier for any
    # html file that will run jasmine tests
    # when and html file that contains the word "jasmine-core" is found,
    # output the name of that file (-l)

    # escape the curly braces needed for grep with more curly braces per Python f-string escape rules
    results = subprocess.run(
        f'find {assessment_path}/{assessment_id} -name "*.html" -exec grep -rlw "jasmine-core" {{}} \;',
        shell=True,
        capture_output=True
    )

    file_list = results.stdout.decode('utf-8').splitlines()

    # put the filename in quotes in case the student put spaces in their path
    formatted_file_names = [str(file) for file in file_list]
    return formatted_file_names


def find_format_run_jasmine_tests(curric_path, assessment_path, assessment_id):
    # find all .test.js files and add rithm links (setup_jasmine_tests)
    # find .html files with Jasmine tests in each student directory
    # make jasmine report - open all .html files in chrome and scrape results
    # print("find_format_run_jasmine_tests", curric_path, assessment_path, assessment_id )
    if setup_jasmine_tests(curric_path, assessment_path, assessment_id) is False:
        return
    html_files = find_jasmine_tests(assessment_path, assessment_id)
    make_jasmine_report(html_files)


def find_directories_with_sought_file_type(path, id, file_matcher):
    """ Locate and return the directories containing a certain file type: '*.txt'
    for all text files, or 'requirements.txt', etc.
    """
    # print("find_directories", path, id, file_matcher)
    directories_raw = subprocess.run(f"find {path}/{id} -type f -name '{file_matcher}' | sed -E 's|/[^/]+$||' |sort -u", shell=True, capture_output=True)
    directories = directories_raw.stdout.decode('utf-8').splitlines()
    # print("directories with sought file type", directories)

    return directories


def setup_flask_apps(assessment_id, assessments_path, student_names):
    """ Search for a requirements.txt files in student submissions.
    If found, create a venv in that folder, activate it, and install the
    requirements.txt. Start Flask servers on sequentially-numbered ports
    and open Chrome at those addresses.
    """

    # print("setup_flask_apps", assessment_id, assessments_path, student_names)

    # find all flask app directories, as long as the student remembered to make a
    # requirements.txt
    flask_directories = find_directories_with_sought_file_type(assessments_path, assessment_id, 'requirements.txt')
    # print(flask_directories)

    # if this assessment doesn't include any Flask apps, exit immediately
    if len(flask_directories) == 0:
        print("no flask apps to run")
        return

    # find students who forgot to include a requirements.txt and print a statement to the console
    if len(flask_directories) != len(student_names):
        for name in student_names:
            if not any(name in flask_dir for flask_dir in flask_directories):
                print(f'\x1b[6;30;41m ***ALERT: {name} forgot to include a requirements.txt; run this app manually.*** \x1b[0m')

    for i, dir in enumerate(flask_directories):
        # create a unique server port for each project
        port = i + 5001
        # print(port, dir)

        # There is an 'extra' deactivate and reactivate sequence because sometimes
        # the venv fails to recognize some freshly-installed packages otherwise
        # wrap dir in quotes to safeguard against student paths with spaces
        command = f"""tell application "Terminal"
                            activate
                            tell application "System Events" to keystroke "t" using {{command down}}
                            do script "cd '{dir}'" in front window
                            do script "python3 -m venv venv" in front window
                            do script "source venv/bin/activate" in front window
                            do script "pip3 install -r requirements.txt" in front window
                            do script "deactivate" in front window
                            do script "source venv/bin/activate" in front window
                            do script "flask run -p {port}" in front window
                        end tell"""
        subprocess.call(["osascript", "-e", command])
        # the following line will execute before everything is installed so nothing
        # will load. Just refresh the browser once the installations are complete
        # and the server has started.
        subprocess.run(f'open http://localhost:{port}', shell=True)

def find_files_and_directories(path, id, items_to_find):
    """ Finds all files and directories passed in.
    items_to_find is a list of tuples with the name of the file or directory,
    and a d for directory or an f for file, like:
    [('venv', 'd'), ('node_modules', 'd'), ('__pycache__', 'd')]

    Returns a list of file paths like:
    [
    '/Users/sarah/Rithm/assessments/r31/test/flask-1/student-name/flask-1/currencyConverter/venv',
    '/Users/sarah/Rithm/assessments/r31/test/flask-1/student-name/flask-1/currencyConverter/__pycache__'
    ]
    """
    found_files = []
    for item, type in items_to_find:
        raw_out = subprocess.run(f"find {path}/{id} -type {type} -name {item}", shell=True, capture_output=True)
        output_list = raw_out.stdout.decode('utf-8').splitlines()
        # print("output_list", output_list)
        if output_list != []:
            # only top-level directories that match the sought-for name
            found_files.append(output_list[0])

    return found_files

def find_alert_and_remove_unwanted_items(path, id, items_to_find):
    """ Finds things like venvs and node_modules; prints an
    alert to the terminal when found, and removes them from the student's
    directory.
    """

    unwanted_item_paths = find_files_and_directories(path, id, items_to_find)

    for path in unwanted_item_paths:
        print(f'\x1b[6;30;41m***ALERT: found {path}. Removing from student directory.***\x1b[0m')
        subprocess.run(f'rm -rf "{path}"', shell=True)


# find_alert_and_remove_unwanted_items('.', '', [('venv', 'd'), ('node_modules', 'd')])
