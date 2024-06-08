import tkinter.messagebox as tkmessagebox
from utils import open_file
from widgets import base_font


class ShowHelp:
    def __init__(self, filename):
        open_file(filename)


class NotImplemented:
    def __init__(self):
        tkmessagebox.showinfo(
            'Not Implemented', 'This functionality not yet implemented.'
        )


def newline_if_past_breakpoint(
    text: str, breakpoint: float, width: float
) -> str:
    if width < breakpoint:
        # Don't split onto more than two lines
        if '\n' in text:
            return text

        text = text.split(' ')
        if len(text) == 1:
            return text[0]
        return f'{" ".join(text[0:len(text) - 1])}\n{text[-1]}'

    return ' '.join(text.split('\n'))


def format_version_for_title(version: str) -> str:
    if 'a' in version:
        return f'Version {version} ALPHA'
    if 'b' in version:
        return f'Version {version} BETA'
    return f'Version {version}'
