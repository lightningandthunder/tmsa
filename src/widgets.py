# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from init import *
import tkinter as tk
import tkinter.messagebox as tkmessagebox
from tkinter.font import Font as tkFont
import traceback
from constants import VERSION
from PIL import ImageTk

main = tk.Tk()
main.minsize(800, 600)
main.state('zoomed')
main.title(f'Time Matters {VERSION}')
main.iconbitmap(app_path(os.path.join('assets', 'tmsa3.ico')))

base_font = tkFont(family='Lucida Console', size=18, weight='normal')
small_font = tkFont(family='Lucida Console', size=16, weight='normal')
smallest_font = tkFont(family='Lucida Console', size=14, weight='normal')
ulfont = tkFont(family='Lucida Console', size=18, weight='normal', underline=1)
title_font = tkFont(family='Lucida Console', size=36, weight='bold')

# background = ImageTk.PhotoImage(file=app_path(os.path.join('assets', 'tmsa2.png')), size=1)
# background_label = tk.Label(main, image=background)
# background_label.place(x=0, y=0, relwidth=1,relheight=1)

# background_label.image = background


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


def check_num(widget, maxnum):
    text = widget.text
    l = len(text)
    if l == 0:
        return
    if text[-1] not in '0123456789':
        widget.text = text[0:-1]
        return
    num = int(text)
    if num * 10 > maxnum:
        widget.tk_focusNext().focus()
        return
    maxlen = len(str(maxnum))
    if l >= maxlen:
        widget.tk_focusNext().focus()
        return


def check_dec(widget, maxnum):
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


def check_snum(widget, minnum, maxnum):
    text = widget.text
    l = len(text)
    if l == 0:
        return
    if l == 1 and text[0] == '-':
        return
    if text[-1] not in '0123456789':
        widget.text = text[0:-1]
        return
    num = int(text)
    if num * 10 > maxnum:
        widget.tk_focusNext().focus()
    elif num * 10 < minnum:
        widget.tk_focusNext().focus()
    maxlen = len(str(maxnum)) if num >= 0 else len(str(minnum))
    if l >= maxlen:
        widget.tk_focusNext().focus()
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
