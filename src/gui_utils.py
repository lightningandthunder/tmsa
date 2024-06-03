import tkinter.messagebox as tkmessagebox
from utils import open_file


class ShowHelp:
    def __init__(self, filename):
        open_file(filename)


class NotImplemented:
    def __init__(self):
        tkmessagebox.showinfo(
            'Not Implemented', 'This functionality not yet implemented.'
        )
