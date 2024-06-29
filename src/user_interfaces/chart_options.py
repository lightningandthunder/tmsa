# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json
import os
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from src import *
from src.user_interfaces.widgets import *
from src.utils.format_utils import normalize_text
from src.utils.gui_utils import ShowHelp

from .midpoint_options import MidpointOptions


class ChartOptions(Frame):
    def __init__(self, optname, istemp=False, output=None):
        super().__init__()
        self.istemp = istemp
        self.output = output
        Label(self, 'Chart Options', 0, 0, 1)
        self.optfile = Entry(self, optname, 0.3, 0.05, 0.3)
        self.optfile.focus()
        Button(self, 'Load', 0.6, 0.05, 0.1).bind(
            '<Button-1>', lambda _: delay(self.load)
        )
        self.eris = Checkbutton(self, 'Include Eris', 0.2, 0.1, 0.2)
        self.eris.checked = True
        self.sedna = Checkbutton(self, 'Include Sedna', 0.4, 0.1, 0.2)
        self.vertex = Checkbutton(self, 'Include Vertex', 0.6, 0.1, 0.2)
        self.node = Radiogroup(self)
        Radiobutton(self, self.node, 0, "Don't Use Node", 0.2, 0.15, 0.2)
        Radiobutton(self, self.node, 1, 'Use True Node', 0.4, 0.15, 0.2)
        Radiobutton(self, self.node, 2, 'Use Mean Node', 0.6, 0.15, 0.2)
        Label(self, 'Background   ', 0, 0.2, 0.2)
        self.bgcurve = Radiogroup(self)
        Radiobutton(self, self.bgcurve, 0, 'At Cadent Cusps', 0.2, 0.2, 0.2)
        Radiobutton(self, self.bgcurve, 1, 'At Mid-quadrant', 0.4, 0.2, 0.2)
        Radiobutton(
            self,
            self.bgcurve,
            2,
            'Eureka curve',
            0.6,
            0.2,
            0.2,
        )
        self.nobg = Checkbutton(self, "Don't Mark", 0.8, 0.2, 0.15)
        Label(self, 'C1 Orb', 0.225, 0.25, 0.1)
        Label(self, 'C2 0rb', 0.325, 0.25, 0.1)
        Label(self, 'C3 Orb', 0.425, 0.25, 0.1)
        Label(self, 'C1 Orb', 0.525, 0.25, 0.1)
        Label(self, 'C2 0rb', 0.625, 0.25, 0.1)
        Label(self, 'C3 0rb', 0.725, 0.25, 0.1)
        Label(self, 'Major Angles', 0.25, 0.3, 0.25)
        Label(self, 'Minor Angles', 0.55, 0.3, 0.25)
        Label(self, 'Foreground   ', 0, 0.35, 0.2)
        self.maj = []
        self.maj.append(Entry(self, '3', 0.25, 0.35, 0.05))
        self.maj.append(Entry(self, '7', 0.35, 0.35, 0.05))
        self.maj.append(Entry(self, '10', 0.45, 0.35, 0.05))
        for i in range(3):
            self.maj[i].bind(
                '<KeyRelease>', lambda e: delay(check_dec, e.widget)
            )
        self.min = []
        self.min.append(Entry(self, '2', 0.55, 0.35, 0.05))
        self.min.append(Entry(self, '3', 0.65, 0.35, 0.05))
        self.min.append(Entry(self, '', 0.75, 0.35, 0.05))
        for i in range(3):
            self.min[i].bind(
                '<KeyRelease>', lambda e: delay(check_dec, e.widget)
            )
        Label(self, 'Ecliptic Aspects', 0.25, 0.4, 0.25)
        Label(self, 'Mundane Aspects', 0.55, 0.4, 0.25)
        Label(self, 'Exact At', 0.85, 0.4, 0.1, anchor=tk.W)
        names = [
            'Conjunction',
            'Opposition',
            'Square',
            'Octile',
            'Trine',
            'Sextile',
            'Inconjuct',
        ]
        abbr = ['co ', 'op ', 'sq ', 'oc ', 'tr ', 'sx ', 'in ']
        exact = [0, 180, 90, [45, 135], 120, 60, [30, 150]]
        maxorb = [
            [3, 7, 10],
            [3, 7, 10],
            [3, 6, 7.5],
            [1, 2, 0],
            [3, 6, 7.5],
            [3, 6, 7.5],
            [0, 0, 0],
        ]
        mmaxorb = [[3, 0, 0], [3, 0, 0], [3, 0, 0], [0, 0, 0]]
        self.names = []
        self.abbrs = []
        self.maxorbs = []
        self.maxcls = []
        self.mmaxorbs = []
        self.mmaxcls = []
        for i in range(len(names)):
            self.names.append(
                Label(self, f'{names[i]:11}  ', 0, i * 0.05 + 0.45, 0.2)
            )
            self.abbrs.append(
                Label(self, f'{abbr[i]:3}  ', 0.2, i * 0.05 + 0.45, 0.05)
            )
            mxo = [None, None, None]
            mxo[0] = Entry(self, '', 0.25, i * 0.05 + 0.45, 0.05)
            mxo[1] = Entry(self, '', 0.35, i * 0.05 + 0.45, 0.05)
            mxo[2] = Entry(self, '', 0.45, i * 0.05 + 0.45, 0.05)
            maxorb = 5 if names[i] in ['oc', 'in'] else 15
            for j in range(3):
                mxo[j].bind(
                    '<KeyRelease>',
                    lambda e: delay(check_dec, e.widget),
                )
            self.maxorbs.append(mxo)
            if type(exact[i]) == list:
                mess = str(exact[i])[1:-1]
            else:
                mess = str(exact[i])
            Label(self, mess, 0.85, i * 0.05 + 0.45, 0.3, anchor=tk.W)
            if i < 4:
                mmxo = [None, None, None]
                mmxo[0] = Entry(self, '', 0.55, i * 0.05 + 0.45, 0.05)
                mmxo[1] = Entry(self, '', 0.65, i * 0.05 + 0.45, 0.05)
                mmxo[2] = Entry(self, '', 0.75, i * 0.05 + 0.45, 0.05)
                maxorb = 5 if names[i] in ['oc', 'in'] else 15
                for j in range(3):
                    mmxo[j].bind(
                        '<KeyRelease>',
                        lambda e: delay(check_dec, e.widget),
                    )
                self.mmaxorbs.append(mmxo)
        Label(
            self,
            'C1: close C2: moderate C3: wide. Leave blank to omit.',
            0,
            0.8,
            1,
        )
        Label(self, 'Show Aspects ', 0, 0.85, 0.2)
        self.showasp = Radiogroup(self)
        Radiobutton(self, self.showasp, 0, 'All', 0.2, 0.85, 0.1)
        Radiobutton(self, self.showasp, 1, '1+ FG', 0.3, 0.85, 0.1)
        Radiobutton(self, self.showasp, 2, '2 FG', 0.4, 0.85, 0.1)
        self.partile = Checkbutton(self, 'Partile', 0.5, 0.85, 0.1)
        self.mps = Button(self, 'Midpoints', 0.625, 0.85, 0.2).bind(
            '<Button-1>', lambda _: delay(self.midpoints)
        )
        self.status = Label(self, '', 0, 0.9, 1)
        Button(self, 'Save', 0.2, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.save)
        )
        Button(self, 'Help', 0.4, 0.95, 0.2).bind(
            '<Button-1>',
            lambda _: delay(
                ShowHelp, os.path.join(HELP_PATH, 'chart_options.txt')
            ),
        )
        backbtn = Button(self, 'Back', 0.6, 0.95, 0.2)
        backbtn.bind('<Button-1>', lambda _: delay(self.destroy))
        backbtn.bind('<Tab>', lambda _: delay(self.optfile.focus))
        optfile = normalize_text(optname).replace(' ', '_') + '.opt'
        self.optpath = os.path.join(OPTION_PATH, optfile)
        self.load(self.optpath)
        if istemp:
            self.optfile.text = 'Temporary'

    def load(self, filepath=None):
        self.status.text = ''
        if not filepath:
            filepath = tkfiledialog.askopenfilename(
                initialdir=OPTION_PATH, filetypes=[('Option Files', '*.opt')]
            )
        if not filepath:
            self.status.error('No option file specified.')
            return
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r') as datafile:
                options = json.load(datafile)
        except Exception as e:
            self.status.error(f"Unable to load option file: '{filename}'.")
            return
        self.optfile.text = filename[0:-4].replace('_', ' ')
        self.eris.checked = options.get('use_Eris', True)
        self.sedna.checked = options.get('use_Sedna', False)
        self.vertex.checked = options.get('use_Vertex', False)
        self.node.value = options.get('Node', 0)
        self.showasp.value = options.get('show_aspects', 0)
        self.partile.checked = options.get('partile_nf', False)
        ang = options.get('angularity', {})
        ea = options.get('ecliptic_aspects', {})
        ma = options.get('mundane_aspects', {})
        self.mpopt = options.get('midpoints', {})
        self.bgcurve.value = ang.get('model', 0)
        self.nobg.checked = ang.get('no_bg', False)
        ex = ['0', '180', '90', '45', '120', '60', '30']
        maja = ang.get('major_angles', [3.0, 7.0, 10.0])
        mina = ang.get('minor_angles', [1.0, 2.0, 3.0])
        self.mpopt = options.get('midpoints', {})
        for i in range(3):
            if maja[i] == 0:
                maja[i] = ''
            elif maja[i].is_integer():
                maja[i] = int(maja[i])
            self.maj[i].text = maja[i]
            if mina[i] == 0:
                mina[i] = ''
            elif mina[i].is_integer():
                mina[i] = int(mina[i])
            self.min[i].text = mina[i]
        for i in range(7):
            asp = ea[ex[i]]
            if not type(asp) == list:
                aspx = [0, 0, 0]
                if i in [0, 1]:
                    aspx = (
                        [max(0.4 * asp, 3), max(0.8 * asp, 7), asp]
                        if asp
                        else ['', '', '']
                    )
                if i in [2, 4, 5]:
                    aspx = (
                        [max(0.4 * asp, 3), max(0.8 * asp, 7), asp]
                        if asp
                        else ['', '', '']
                    )
                if i in [3, 6]:
                    aspx = (
                        [max(0.4 * asp, 1), max(0.8 * asp, 2), asp]
                        if asp
                        else ['', '', '']
                    )
            else:
                aspx = asp
                for k in range(3):
                    if aspx[k] == 0:
                        aspx[k] = ''
                    elif aspx[k].is_integer():
                        aspx[k] = int(aspx[k])
            for j in range(3):
                self.maxorbs[i][j].text = aspx[j]
        for i in range(4):
            asp = ma[ex[i]]
            if not type(asp) == list:
                aspx = [0, 0, 0]
                if i in [0, 1]:
                    aspx = (
                        [max(0.4 * asp, 3), max(0.8 * asp, 7), asp]
                        if asp
                        else ['', '', '']
                    )
                if i in [2]:
                    aspx = (
                        [max(0.4 * asp, 3), max(0.8 * asp, 7), asp]
                        if asp
                        else ['', '', '']
                    )
                if i in [3]:
                    aspx = (
                        [max(0.4 * asp, 1), max(0.8 * asp, 2), asp]
                        if asp
                        else ['', '', '']
                    )
            else:
                aspx = asp
                for k in range(3):
                    if aspx[k] == 0:
                        aspx[k] = ''
                    elif aspx[k].is_integer():
                        aspx[k] = int(aspx[k])
            for j in range(3):
                self.mmaxorbs[i][j].text = aspx[j]

    def save(self):
        if not self.optfile.text:
            self.status.error('No option file specified.')
            return
        else:
            self.status.text = ''
        majangs = []
        try:
            for i in range(3):
                majang = self.maj[i].text.strip()
                if not majang:
                    majangs.append(0)
                else:
                    f = float(majang)
                    majangs.append(f if f >= 0 else 0)
                if majangs[i] > 15:
                    self.status.error(
                        'Orb for foreground major angle must be less than or equal to 15.'
                    )
                    return
            err = False
            if majangs[2]:
                if not majangs[1]:
                    err = True
                elif majangs[1] >= majangs[2]:
                    err = True
            if majangs[1]:
                if not majangs[0]:
                    err = True
                elif majangs[0] >= majangs[1]:
                    err = True
            if err:
                self.status.error(
                    'Inconsistent orbs for foreground major angle.'
                )
                return
        except Exception:
            self.status.error(
                'Orb for foreground major angle must be numeric or blank.'
            )
            return
        minangs = []
        try:
            for i in range(3):
                minang = self.min[i].text.strip()
                if not minang:
                    minangs.append(0)
                else:
                    f = float(minang)
                    minangs.append(f if f >= 0 else 0)
                if minangs[i] > 5:
                    self.status.error(
                        'Orb for foreground minor angle must be less than or equal to 5.'
                    )
                    return
            err = False
            if minangs[2]:
                if not minangs[1]:
                    err = True
                elif minangs[1] >= minangs[2]:
                    err = True
            if minangs[1]:
                if not minangs[0]:
                    err = True
                elif minangs[0] >= minangs[1]:
                    err = True
            if err:
                self.status.error(
                    'Inconsistent orbs for foreground minor angle.'
                )
                return
        except Exception:
            self.status.error(
                'Orb for foreground minor angle must be numeric or blank.'
            )
            return
        maxorbs = [[], [], [], [], [], [], []]
        mmaxorbs = [[], [], [], []]
        abbrs = []
        for i in range(len(self.names)):
            abbrs.append(self.abbrs[i].text[0:2])
            if abbrs[i] in ['oc ', 'in']:
                mx = 5
            else:
                mx = 15
            try:
                for j in range(3):
                    maxorb = self.maxorbs[i][j].text.strip()
                    if not maxorb:
                        maxorbs[i].append(0)
                    else:
                        f = float(maxorb)
                        maxorbs[i].append(f if f >= 0 else 0)
                    if maxorbs[i][j] > mx:
                        self.status.error(
                            f'Orb for {self.names[i].text.strip().lower()} must be less than or equal to {mx}.'
                        )
                        return
                err = False
                if maxorbs[i][2]:
                    if not maxorbs[i][1]:
                        err = True
                    elif maxorbs[i][1] >= maxorbs[i][2]:
                        err = True
                if maxorbs[i][1]:
                    if not maxorbs[i][0]:
                        err = True
                    elif maxorbs[i][0] >= maxorbs[i][1]:
                        err = True
                if err:
                    self.status.error(
                        f'Inconsistent orbs for {self.names[i].text.strip().lower()}.'
                    )
                    return
            except Exception:
                self.status.error(
                    f'Orb for {self.names[i].text.strip().lower()} must be numeric or blank.'
                )
                return
            if i > 3:
                continue
            try:
                for j in range(3):
                    mmaxorb = self.mmaxorbs[i][j].text.strip()
                    if not mmaxorb:
                        mmaxorbs[i].append(0)
                    else:
                        f = float(mmaxorb)
                        mmaxorbs[i].append(f if f >= 0 else 0)
                    if mmaxorbs[i][j] > mx:
                        self.status.error(
                            f'Orb for mundane {self.names[i].text.strip().lower()} must be less than or equal to {mx}.'
                        )
                        return
                err = False
                if mmaxorbs[i][2]:
                    if not mmaxorbs[i][1]:
                        err = True
                    elif mmaxorbs[i][1] >= mmaxorbs[i][2]:
                        err = True
                if mmaxorbs[i][1]:
                    if not mmaxorbs[i][0]:
                        err = True
                    elif mmaxorbs[i][0] >= mmaxorbs[i][1]:
                        err = True
                if err:
                    self.status.error(
                        f'Inconsistent orbs for {self.names[i].text.strip().lower()}.'
                    )
                    return
            except Exception:
                self.status.error(
                    f'Orb for mundane {self.names[i].text.strip().lower()} must be numeric or blank.'
                )
                return
        options = self.optfile.text.strip()
        if self.output:
            self.output.text = options
        filename = options.replace(' ', '_') + '.opt'
        filepath = os.path.join(OPTION_PATH, filename)
        options = {}
        ang = 'angularity'
        ea = 'ecliptic_aspects'
        ma = 'mundane_aspects'
        options['use_Eris'] = self.eris.checked
        options['use_Sedna'] = self.sedna.checked
        options['use_Vertex'] = self.vertex.checked
        options['Node'] = self.node.value
        options['show_aspects'] = self.showasp.value
        options['partile_nf'] = self.partile.checked
        options[ang] = {}
        options[ang]['model'] = self.bgcurve.value
        options[ang]['no_bg'] = self.nobg.checked
        options[ang]['major_angles'] = majangs
        options[ang]['minor_angles'] = minangs
        ex = ['0', '180', '90', '45', '120', '60', '30']
        options[ea] = {}
        for i in range(7):
            options[ea][ex[i]] = []
        options[ma] = {}
        for i in range(4):
            options[ma][ex[i]] = []
        options[ang]['model'] = self.bgcurve.value
        for i in range(7):
            for j in range(3):
                text = self.maxorbs[i][j].text
                options[ea][ex[i]].append(float(text) if text else 0)
        for i in range(4):
            for j in range(3):
                text = self.mmaxorbs[i][j].text
                options[ma][ex[i]].append(float(text) if text else 0)
        options['midpoints'] = self.mpopt
        if os.path.exists(filepath):
            if not tkmessagebox.askyesno(
                'File Exists', f"Do you want to overwrite file '{filename}'?"
            ):
                return
        else:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        try:
            with open(filepath, 'w') as datafile:
                json.dump(options, datafile, indent=4)
        except Exception as e:
            self.status.error(f"Unable to save file '{filename}'.")
            return
        self.status.text = f"File '{filename}' saved."
        delay(self.destroy)

    def finish_mp(self):
        if self.mpopt:
            self.status.text = 'Midpoint options changed.'
        else:
            self.status.text = 'Midpoint options unchanged.'
            self.mpopt = {'0': 0, '90': 0, '45': 0, 'M': 0}

    def midpoints(self):
        MidpointOptions(self.optfile.text, self.mpopt, self.finish_mp)
