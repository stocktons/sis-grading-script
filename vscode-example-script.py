"""Update VSCode settings non-destructively for Rithm.

Written and maintained by Joel Burton <joel@joelburton.com>.
"""

from pathlib import Path

from datetime import datetime
import json
import os
import platform
import shutil
import subprocess
import sys

IS_DOCKER = Path("/.dockerenv").exists()
IS_VAGRANT = "agrant" in platform.machine()
IS_WSL = "icrosoft" in platform.release()
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# ################################################################ configuration

EXTENSIONS_TO_INSTALL = [
    "wayou.vscode-todo-highlight",  # highlight "to do" comments
#     "dbaeumer.vscode-eslint",  # low-opinion JS linting
    "ms-python.python",  # core Python lang features
    "ms-python.vscode-pylance",  # deep Python code understanding
    "ms-python.flake8",  # low-opinion Python linting
    "ms-python.autopep8",
    "samuelcolvin.jinjahtml",  # jinja formatting; requires ".j2" file extension
]

if IS_WSL:
    EXTENSIONS_TO_INSTALL.extend([
        # "ms-vscode-remote.remote-wsl",
    ])

EXTENSIONS_TO_UNINSTALL = [
    "ms-python.black-formatter",
    "esbenp.prettier-vscode",
]

COMMON_LANG = {
    "editor.tabSize": 2,
    "editor.wordWrap": "off",
    "editor.rulers": [80],
}

# make Flake8 not complain about most whitespace/minor things
FLAKE8 = ["--ignore=F541,E12,E2,E3,E402,E501,E701,E704,E711,W2,W3,W503,W504"]

SETTINGS = {
    "[typescript]": COMMON_LANG,
    "[css]": COMMON_LANG,
    "[html]": {
        **COMMON_LANG,
        "editor.defaultFormatter": "vscode.html-language-features",
    },
    "[javascript]": {
        **COMMON_LANG,
        "editor.defaultFormatter": "vscode.typescript-language-features",
    },
    "[python]": {
        **COMMON_LANG,
        "editor.tabSize": 4,
        "editor.defaultFormatter": "ms-python.autopep8"
    },
    "editor.minimap.enabled": False,
    "files.trimTrailingWhitespace": True,
    "javascript.format.semicolons": "insert",
    # "python.linting.flake8Enabled": True,
#     "python.linting.flake8Args": FLAKE8,
    "flake8.args": FLAKE8,
    "security.workspace.trust.untrustedFiles": "open",
    "typescript.format.semicolons": "insert",
}


# ######################################################### end of configuration


def err(msg: str):
    """Print error message and quit."""
    print("\033[31;1;4m*** ERROR\033[0m", msg)  # underlined and red
    sys.exit(1)


def update_settings(curr: dict, new: dict):
    """Update settings non-destructively in place.

    Create/update simple keys with exact value:

        >>> s = {'a': 1, 'b': 2}
        >>> update_settings(s, {'a': 11, 'c': 13})
        >>> s
        {'a': 11, 'b': 2, 'c': 13}

    If complex key doesn't exist, make it & set:

        >>> s = {'a': 1}
        >>> update_settings(s, {'b': {'ba': 1}})
        >>> s
        {'a': 1, 'b': {'ba': 1}}

    If complex key already exists, add in new subkeys:

        >>> s = {'a': {'aa': 1, 'ab': 2}}
        >>> update_settings(s, {'a': {'ab': 12, 'ac': 13}})
        >>> s
        {'a': {'aa': 1, 'ab': 12, 'ac': 13}}
    """

    for k, v in new.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                curr.setdefault(k, {})[kk] = vv
        else:
            curr[k] = v


# ######################################################################### main

def main():
    # Initial sanity checks

    if IS_DOCKER:
        err("Cannot setup host VSCode via Docker.")

    if IS_VAGRANT:
        # FIXME: is it under machine?
        err("Cannot setup host VSCode via Vagrant")

    if not shutil.which("code"):
        err("""'code' command not found for VSCode"

    In VSCode (on MacOS):
    - from menu, choose View > Command Palette
    - search for \"shell\"
    - select \"Shell Command: Install 'code' command in PATH\"
    Once that is done, re-run this script.

    In VSCode (on Windows):
    - see our installation instructions for help""")

    # Install/uninstall extensions

    res = subprocess.run(
        [f"code --list-extensions"],
        capture_output=True,
        shell=True)
    if res.returncode != 0:
        err(res.stderr.decode("utf8"))
    installed = res.stdout.decode("utf8").split()

    for extension_name in EXTENSIONS_TO_INSTALL:
        if extension_name not in installed:
            res = subprocess.run(
                [f"code --install-extension {extension_name}"],
                capture_output=True,
                shell=True
            )
            if res.returncode != 0:
                err(res.stderr.decode("utf8"))
            print(f"Installed {extension_name}")

    for extension_name in EXTENSIONS_TO_UNINSTALL:
        if extension_name in installed:
            res = subprocess.run(
                [f"code --uninstall-extension {extension_name}"],
                capture_output=True,
                shell=True
            )
            if res.returncode != 0:
                err(res.stderr.decode("utf8"))
            print(f"Uninstalled {extension_name}")

    # Get directory for VSCode settings

    if IS_MAC:
        settings_dir = f"{Path.home()}/Library/Application Support/Code/User"

    elif IS_WSL:
        res = subprocess.run(
            ["wslpath $(wslvar APPDATA)"],
            capture_output=True,
            shell=True
        )
        if res.returncode != 0:
            err(res.stderr.decode("utf8"))
        settings_dir = res.stdout.decode("utf8").strip() + "/Code/User"

    elif IS_LINUX:
        settings_dir = f"{Path.home()}/.config/Code/User"

    else:
        err("Cannot determine path to VSCode settings.")
        settings_dir = None

    print(f'VSCode settings folder is "{settings_dir}"')
    os.chdir(settings_dir)

    # Create settings.json if it doesn't exist

    try:
        open("settings.json", "x")
        print("Created empty settings.json, as it didn't exist")
    except FileExistsError:
        pass

    # Make backup file like "settings-2023-03-11T11:30:39.795259.json"

    backup_name = f"settings-{datetime.now().isoformat()}.json"
    shutil.copy("settings.json", backup_name)
    print(f"Copied existing settings.json to {backup_name}")

    # Read JSON into settings object

    with open("settings.json") as settings_file:
        settings = json.load(settings_file)

    # Change settings
    update_settings(settings, SETTINGS)

    # Write settings out to disk pretty-printed

    with open("settings.json", "w") as settings_file:
        json.dump(settings, settings_file, indent=True)

    # Complete!

    print("Edited VSCode settings for Rithm. Done!")


if __name__ == "__main__":
    main()