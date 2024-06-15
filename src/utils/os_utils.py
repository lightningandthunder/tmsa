import os
import shutil
import subprocess
from src.constants import PLATFORM

def create_directory(path):
    os.makedirs(path, exist_ok=True)
    os.chmod(path, 0o775)

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
