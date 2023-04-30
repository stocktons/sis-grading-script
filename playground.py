###### PLAYGROUND FILE FOR EXPERIMENTS AND RESEARCH ###########

import os
# import glob
import subprocess
base_path = '/Users/sarah/Rithm/assessments/r31/flask-1'
# base_path = '/Users/sarah/Projects/test'

# https://stackoverflow.com/questions/16956810/how-to-find-all-files-containing-specific-text-string-on-linux
# grep -rlw '/Users/sarah/Rithm/assessments/r31/flask-1/' -e 'jasmine-core'
# grep -F -l jasmine-core **/*.html
# grep --include=\*.html -l -e "jasmine-core"
# find . -type f \( -iname \*.xml -o -iname \*.py \) | xargs grep "Jason"
# ls $(find /Users/sarah/Rithm/assessments/r31/flask-1/ -type f -name '*.html' | xargs grep "jasmine-core")
# jasmine_tests = subprocess.run(['find', base_path, '-type', 'f', '-name', '"*.html"', '|', 'xargs', 'grep', '"jasmine-core"'])

# jasmine_tests = subprocess.Popen(('find', '/Users/sarah/Rithm/assessments/r31/flask-1/', '-type', 'f','-name', '*.html', '-exec', 'ls', '{}', ';'))
# jt = subprocess.run('grep -rlw "/Users/sarah/Rithm/assessments/r31/flask-1/" -e "jasmine-core"', shell=True, capture_output=True)
# time: 1.44s user 0.30s system 99% cpu 1.743 total

# jasmine_tests = subprocess.run(['grep', 'rlw', '/Users/sarah/Rithm/c
# assessments/r31/flask-1/', '-e', '"jasmine-core"'], capture_output=True)
# jasmine = glob.glob(f'{base_path}**/*.html', recursive=True)

# jt2 = subprocess.run('find /Users/sarah/Rithm/assessments/r31/flask-1 -name "*.html" -exec grep -rlw "jasmine-core" {} \;', shell=True, capture_output=True)
# time: 0.02s user 0.10s system 90% cpu 0.136 total

# file_list = jt.stdout.decode('utf-8').splitlines()

# print(file_list)

# jt2_out = jt2.stdout.decode('utf-8').splitlines()

# print("second search", jt2_out)

def find_and_run_jasmine_tests():
    # escape the curly braces needed for grep with more curly braces per Python f-string escape rules
    results = subprocess.run(f'find {base_path} -name "*.html" -exec grep -rlw "jasmine-core" {{}} \;', shell=True, capture_output=True)
    file_list = results.stdout.decode('utf-8').splitlines()
    print(file_list)

    for file in file_list:
        # put the filename in quotes in case the student put spaces in their path

        os.system(f'open "{file}"')

find_and_run_jasmine_tests()

# not needed, just wrapped the path in quotes, but keeping for further study/interest
# search for filenames that contain spaces and replace all spaces with underscores:
# this 'find' command works in terminal but not with os.system
# https://stackoverflow.com/questions/2709458/how-to-replace-spaces-in-file-names-using-a-bash-script
# os.system('find /Users/sarah/Projects/test -depth -name "* *" | while IFS= read -r f ; do mv -i "$f" "$(dirname "$f")/$(basename "$f"|tr ' ' _)" ; done')

# variations on the above that also don't work
# subprocess.run('find /Users/sarah/Projects/test -depth -name "* *" | while IFS= read -r f ; do mv -i "$f" "$(dirname "$f")/$(basename "$f"|tr ' ' _)" ; done', shell=True)
# subprocess.run(['find', '/Users/sarah/Projects/test', '-depth', '-name', '"* *"', '|', 'while', 'IFS=', 'read', '-r', 'f', ';', 'do', 'mv', '-i', '"$f"', '"$(dirname "$f")/$(basename "$f"|tr ' ' _)"', ';', 'done'], shell=True)

# os.system(f'for f in *\ *; do mv "$f" "${{f// /_}}"; done')
# os.system(f'while read line ; do mv "$line" "${{line// /_}}" ; done < <(find {base_path} -iname "* *")')

# add a line after a match (find s01. ... and add b01\Baking Powder)
# sed '/^s01.*/a b01\tBaking Powder' products.txt

# add a line before a match (find anothervalue= ... and insert before=me before it)
# sed '/^anothervalue=.*/i before=me' test.txt

# <script src="/Users/sarah/Rithm/rithm-apps/curric/assessments/flask-1/solution/scrambledPalindromeCheck.test.js"></script>

# I want to find </body> and insert a <script... > before it
# will have to copy the test file and rename it locally, then construct the local path

### HOLY SHIT THIS TOOK FOREVER
# https://stackoverflow.com/questions/40843994/extra-characters-after-at-the-end-of-a-command
# Macs require the -i '' to change the file in place
# they also require that the command be written across multiple lines with a \ at the end of the first line
# using the | to replace the typical / separator so that the /body doesn't get confused or need to escape
# must precede first custom delimiter with a \
sed -i '' '\|^</body>.*| i\
<script src="/Users/sarah/Rithm/rithm-apps/curric/assessments/flask-1/solution/scrambledPalindromeCheck.test.js"></script>
' /Users/sarah/Rithm/assessments/r31/flask-1/michael-herman/flask-1/scrambledPalindromeCheck.html

