import os
import shutil
import subprocess

from src.constants import APP_PATH, PLATFORM


def app_path(path=None):
    if not path:
        return APP_PATH
    return os.path.abspath(os.path.join(APP_PATH, path))


def copy_file_if_not_exists(expected: str, src: str):
    if not os.path.exists(expected):
        shutil.copyfile(src, expected)


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


def write_to_path(path: str, text: str):
    try:
        with open(path, 'w') as file:
            file.write(text)
    except:
        pass
