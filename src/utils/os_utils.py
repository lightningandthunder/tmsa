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


def write_to_file_if_not_exists(path: str, text: str):
    if not os.path.exists(path):
        write_to_path(path, text)


def migrate_from_file(old_path: str, new_path: str, fallback: str):
    if not os.path.exists(new_path):
        if os.path.exists(old_path):
            shutil.copyfile(old_path, new_path)
        else:
            write_to_path(new_path, fallback)

    if (
        os.path.exists(old_path)
        and os.path.exists(new_path)
        and old_path != new_path
    ):
        try:
            os.remove(old_path)
        except:
            pass


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
        with open(path, 'a') as file:
            file.write(text)
    except:
        pass
