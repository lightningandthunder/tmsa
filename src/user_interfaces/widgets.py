# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import tkinter as tk
import tkinter.messagebox as tkmessagebox
import traceback
from tkinter.font import Font as tkFont

from src.constants import PLATFORM, VERSION
from src import *

main = tk.Tk()
main.minsize(800, 600)

if not os.environ.get('TMSA_TEST'):
    if PLATFORM == 'Win32GUI':

        main.state('zoomed')
        main.iconbitmap(app_path(os.path.join('assets', 'tmsa3.ico')))
    elif PLATFORM == 'linux':
        main.state('normal')
        main.wm_attributes('-zoomed', True)

        icon = tk.PhotoImage(
            file=app_path(os.path.join('assets', 'tmsa2.png'))
        )
        main.wm_iconphoto(True, icon)
        main.iconphoto(
            True,
            tk.PhotoImage(file=app_path(os.path.join('assets', 'tmsa2.png'))),
        )
    elif PLATFORM == 'darwin':
        main.state('zoomed')
        main.iconbitmap(app_path(os.path.join('assets', 'tmsa3.ico')))

    main.title(f'Time Matters {VERSION}')

if PLATFORM == 'Win32GUI':
    base_font = tkFont(family='Lucida Console', size=18, weight='normal')
    font_16 = tkFont(family='Lucida Console', size=16, weight='normal')
    font_14 = tkFont(family='Lucida Console', size=14, weight='normal')
    font_12 = tkFont(family='Lucida Console', size=12, weight='normal')
    font_10 = tkFont(family='Lucida Console', size=10, weight='normal')
    ulfont = tkFont(
        family='Lucida Console', size=18, weight='normal', underline=1
    )
    title_font = tkFont(family='Lucida Console', size=36, weight='bold')
elif PLATFORM == 'linux':
    root_font = tk.font.nametofont('TkDefaultFont')

    base_font = root_font.copy()
    base_font.configure(size=18)

    font_16 = root_font.copy()
    font_16.configure(size=16)

    font_14 = root_font.copy()
    font_14.configure(size=14)

    font_12 = root_font.copy()
    font_12.configure(size=12)

    font_10 = root_font.copy()
    font_10.configure(size=10)

    ulfont = root_font.copy()
    ulfont.configure(size=18, underline=1)

    title_font = root_font.copy()
    title_font.configure(size=36, weight='bold')

elif PLATFORM == 'darwin':
    root_font = tk.font.nametofont('TkDefaultFont')

    base_font = root_font.copy()
    base_font.configure(size=18)

    font_16 = root_font.copy()
    font_16.configure(size=16)

    font_14 = root_font.copy()
    font_14.configure(size=14)

    font_12 = root_font.copy()
    font_12.configure(size=12)

    font_10 = root_font.copy()
    font_10.configure(size=10)

    ulfont = root_font.copy()
    ulfont.configure(size=18, underline=1)

    title_font = root_font.copy()
    title_font.configure(size=36, weight='bold')


def on_exit():
    if tkmessagebox.askyesno('Are you sure?', f'Quit Time Matters {VERSION}?'):
        main.destroy()


main.protocol('WM_DELETE_WINDOW', on_exit)


def show_error(self, *args):
    err = traceback.format_exception(*args)
    tkmessagebox.showerror('Exception', err)
    with open(ERROR_FILE, 'w') as ef:
        ef.write(str(err))


tk.Tk.report_callback_exception = show_error


def delay(func, *args, **kwargs):
    main.after(1, func, *args, **kwargs)


def check_num(widget):
    text = widget.text
    l = len(text)
    if l == 0:
        return
    if text[-1] not in '0123456789':
        widget.text = text[0:-1]
        return


def check_dec(widget):
    text = widget.text
    l = len(text)
    if l == 0:
        return
    if text[-1] == '.':
        if text.count('.') > 1:
            widget.text = text[0:-1]
        return
    if text[-1] not in '0123456789':
        widget.text = text[0:-1]
        return


def check_snum(widget):
    text = widget.text
    l = len(text)
    if l == 0:
        return
    if l == 1 and text[0] == '-':
        return
    if text[-1] not in '0123456789':
        widget.text = text[0:-1]
        return


class Frame(tk.Frame):
    def __init__(self):
        super().__init__(main, background=BG_COLOR)
        self.place(relwidth=1, relheight=1)
        self.lift()


class PropertyMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def text(self):
        return self['text']

    @text.setter
    def text(self, value):
        self.fg = TXT_COLOR
        self['text'] = value

    def error(self, value, focus=None):
        self.fg = ERR_COLOR
        self['text'] = value
        if focus:
            focus.focus()

    @property
    def fg(self):
        return self['foreground']

    @fg.setter
    def fg(self, value):
        self['foreground'] = value

    @property
    def bg(self):
        return self['background']

    @bg.setter
    def bg(self, value):
        self['background'] = value

    @property
    def anchor(self):
        return self['anchor']

    @anchor.setter
    def anchor(self, value):
        self['anchor'] = value

    @property
    def disabled(self):
        return self['state'] == tk.DISABLED

    @disabled.setter
    def disabled(self, state):
        self['state'] = tk.DISABLED if state else tk.NORMAL


class Label(PropertyMixin, tk.Label):
    def __init__(
        self,
        root,
        text,
        x,
        y,
        width=0.25,
        height=0.05,
        anchor=tk.CENTER,
        font=base_font,
    ):
        super().__init__(
            root, text=text, foreground=TXT_COLOR, background=BG_COLOR
        )
        self['font'] = font
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.anchor = anchor
        self.place(relx=x, rely=y, relwidth=width, relheight=height)


class Button(PropertyMixin, tk.Button):
    def __init__(
        self, root, text, x, y, width=0.25, height=0.05, font=base_font
    ):
        super().__init__(
            root, text=text, foreground=TXT_COLOR, background=BTN_COLOR
        )
        self['font'] = font
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.anchor = self['anchor']
        self.place(relx=x, rely=y, relwidth=width, relheight=height)


class Entry(PropertyMixin, tk.Entry):
    def __init__(self, root, text, x, y, width, height=0.05, focus=True):
        self._var = tk.StringVar(root)
        super().__init__(
            root,
            textvariable=self._var,
            foreground='black',
            background='white',
            takefocus=focus,
            font=base_font,
        )
        self['font'] = base_font
        self._var.set(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self['anchor'] = None
        self.place(relx=x, rely=y, relwidth=width, relheight=height)

    @property
    def text(self):
        return self._var.get()

    @text.setter
    def text(self, value):
        self._var.set(value)


class Checkbutton(PropertyMixin, tk.Checkbutton):
    def __init__(
        self, root, text, x, y, width, height=0.05, focus=True, font=base_font
    ):
        self._var = tk.IntVar(root)
        super().__init__(
            root,
            text=text,
            variable=self._var,
            foreground=TXT_COLOR,
            background=BG_COLOR,
            selectcolor=BG_COLOR,
            takefocus=focus,
        )
        self['font'] = font
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self['anchor'] = tk.W
        self.place(relx=x, rely=y, relwidth=width, relheight=height)

    @property
    def checked(self):
        return self._var.get()

    @checked.setter
    def checked(self, value):
        self._var.set(value)


class Radiogroup:
    def __init__(self, root):
        self._var = tk.IntVar(root)
        self._buttons = []

    @property
    def var(self):
        return self._var

    @property
    def value(self):
        return self._var.get()

    @value.setter
    def value(self, value):
        self._var.set(value)

    def append(self, rbtn):
        self._buttons.append(rbtn)

    @property
    def buttons(self):
        return self._buttons

    def focus(self):
        self.buttons[0].focus()


class Radiobutton(tk.Radiobutton):
    def __init__(
        self,
        root,
        group,
        value,
        text,
        x,
        y,
        width,
        height=0.05,
        focus=True,
        font=base_font,
    ):
        self._var = group.var
        super().__init__(
            root,
            text=text,
            variable=self._var,
            foreground=TXT_COLOR,
            background=BG_COLOR,
            selectcolor=BG_COLOR,
            value=value,
            takefocus=focus,
        )
        self['font'] = font
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self['anchor'] = tk.W
        self.place(relx=x, rely=y, relwidth=width, relheight=height)
        group.append(self)
