import subprocess

def determine_os():
    """Ask the current OS what it is, to determine whether to use file paths 
    for WSL or for MacOS.
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

        return (linux_username, windows_username)

    if os_name == "Darwin":
        # mac_username_data will be like: 
        # CompletedProcess(args=['id', '-un'], returncode=0, stdout=b'sarah\n', stderr=b'')
        mac_username_data= subprocess.run(['id', '-un'], capture_output=True)
        # grab "sarah". not like that. ugh...
        mac_username = mac_username_data.stdout.decode('utf-8').strip()

        return (mac_username,)

print(determine_os())