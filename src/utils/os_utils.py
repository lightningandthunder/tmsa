import grp
import os
import pwd
import shutil
import subprocess

from src.constants import PLATFORM


def create_directory(path):
    os.makedirs(path, exist_ok=True)


def remove_directory(path):
    shutil.rmtree(path)


def open_file(file: str):
    match PLATFORM:
        case 'Win32GUI':
            os.startfile(file)
        case 'linux':
            if shutil.which('xdg-open'):
                subprocess.call(['xdg-open', file])
            elif 'EDITOR' in os.environ:
                subprocess.call([os.environ['EDITOR'], file])
        case 'darwin':
            subprocess.run(['open', '-a', 'TextEdit', file])


def drop_privileges():
    if PLATFORM != 'linux':
        return

    # Drop privileges if ran with sudo
    user_name = 'tmsauser'
    try:
        running_uid = os.getuid()

        target_uid = pwd.getpwnam(user_name).pw_uid
        target_gid = grp.getgrnam(user_name).gr_gid

        if running_uid == 0:  # Only drop privileges if running as root
            os.setgid(target_gid)
            os.setuid(target_uid)
    except Exception as e:
        print(f'Failed to drop privileges: {e}')
        exit(1)
