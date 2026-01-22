# Copyright 2026 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import json
import math
import os
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from src import *
from src.user_interfaces.extra_planet_options import ExtraPlanetOptions
from src.user_interfaces.pvp_options import PVPOptions
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
        self.vertex = Checkbutton(self, 'Include Vertex', 0.6, 0.1, 0.2)
        self.node = Radiogroup(self)
        Radiobutton(self, self.node, 0, "Don't Use Node", 0.2, 0.15, 0.2)
        Radiobutton(self, self.node, 1, 'Use True Node', 0.4, 0.15, 0.2)
        Radiobutton(self, self.node, 2, 'Use Mean Node', 0.6, 0.15, 0.2)
        Label(self, 'Background', 0.03, 0.2, 0.2, anchor='w')
        self.bgcurve = Radiogroup(self)
        Radiobutton(self, self.bgcurve, 2, 'At Cadent Cusps', 0.2, 0.2, 0.2)
        Radiobutton(self, self.bgcurve, 1, 'At Mid-quadrant', 0.4, 0.2, 0.2)

        self.nobg = Checkbutton(self, "Don't Mark", 0.6, 0.2, 0.15)
        Label(self, 'C1 Orb', 0.225, 0.25, 0.1)
        Label(self, 'C2 0rb', 0.325, 0.25, 0.1)
        Label(self, 'C3 Orb', 0.425, 0.25, 0.1)
        Label(self, 'C1 Orb', 0.525, 0.25, 0.1)
        Label(self, 'C2 0rb', 0.625, 0.25, 0.1)
        Label(self, 'C3 0rb', 0.725, 0.25, 0.1)
        Label(self, 'Major Angles', 0.25, 0.3, 0.25)
        Label(self, 'Minor Angles', 0.55, 0.3, 0.25)
        Label(self, 'Foreground', 0.03, 0.35, 0.2, anchor='w')
        self.maj = []
        self.maj.append(Entry(self, '3', 0.25, 0.35, 0.05))
        self.maj.append(Entry(self, '7', 0.35, 0.35, 0.05))
        self.maj.append(Entry(self, '10', 0.45, 0.35, 0.05))
        for aspect_name_index in range(3):
            self.maj[aspect_name_index].bind(
                '<KeyRelease>', lambda e: delay(check_dec, e.widget)
            )
        self.min = []
        self.min.append(Entry(self, '2', 0.55, 0.35, 0.05))
        self.min.append(Entry(self, '3', 0.65, 0.35, 0.05))
        self.min.append(Entry(self, '', 0.75, 0.35, 0.05))
        for aspect_name_index in range(3):
            self.min[aspect_name_index].bind(
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
            '10° Series',
        ]
        abbr = ['co', 'op', 'sq', 'oc', 'tr', 'sx', 'in', 'dc']
        exact = [0, 180, 90, [45, 135], 120, 60, [30, 150], 10]
        self.names = []
        self.abbrs = []
        self.maxorbs = []
        self.maxcls = []
        self.mmaxorbs = []
        self.mmaxcls = []

        self.allowed_ecliptic = {}
        self.allowed_mundane = {}

        for aspect_name_index in range(len(names)):
            self.names.append(
                Label(
                    self,
                    f'{names[aspect_name_index]:11}',
                    0.03,
                    aspect_name_index * 0.05 + 0.45,
                    0.2,
                    0.05,
                    anchor='w',
                )
            )
            self.abbrs.append(
                Label(
                    self,
                    f'{abbr[aspect_name_index]:3}',
                    0.2,
                    aspect_name_index * 0.05 + 0.45,
                    0.05,
                )
            )
            max_orb_row = [
                Entry(self, '', 0.25, aspect_name_index * 0.05 + 0.45, 0.05),
                Entry(self, '', 0.35, aspect_name_index * 0.05 + 0.45, 0.05),
                Entry(self, '', 0.45, aspect_name_index * 0.05 + 0.45, 0.05),
            ]
            for max_orb_aspect_class in range(3):
                max_orb_row[max_orb_aspect_class].bind(
                    '<KeyRelease>',
                    lambda e: delay(check_dec, e.widget),
                )
            self.maxorbs.append(max_orb_row)
            if type(exact[aspect_name_index]) == list:
                exact_degree_label = str(exact[aspect_name_index])[1:-1]
            else:
                exact_degree_label = str(exact[aspect_name_index])
            Label(
                self,
                exact_degree_label,
                0.85,
                aspect_name_index * 0.05 + 0.45,
                0.3,
                anchor=tk.W,
            )

            # Mundane orbs
            if aspect_name_index < 3:
                mundane_max_orb_row = [
                    Entry(
                        self, '', 0.55, aspect_name_index * 0.05 + 0.45, 0.05
                    ),
                    Entry(
                        self, '', 0.65, aspect_name_index * 0.05 + 0.45, 0.05
                    ),
                    Entry(
                        self, '', 0.75, aspect_name_index * 0.05 + 0.45, 0.05
                    ),
                ]
                for max_orb_aspect_class in range(3):
                    mundane_max_orb_row[max_orb_aspect_class].bind(
                        '<KeyRelease>',
                        lambda e: delay(check_dec, e.widget),
                    )
                self.mmaxorbs.append(mundane_max_orb_row)

        Label(self, 'Show Aspects ', 0.03, 0.85, 0.2, anchor=tk.W)
        self.showasp = Radiogroup(self)
        Radiobutton(self, self.showasp, 0, 'All', 0.2, 0.85, 0.1)
        Radiobutton(self, self.showasp, 1, '1+ FG', 0.3, 0.85, 0.1)
        Radiobutton(self, self.showasp, 2, '2 FG', 0.4, 0.85, 0.1)
        self.partile = Checkbutton(self, 'Partile', 0.5, 0.85, 0.1)
        self.include_fg_under_aspects = Checkbutton(
            self, 'Include FG in aspects', 0.6, 0.85, 0.3
        )

        Label(self, 'Show Novien', 0.03, 0.9, 0.2, anchor=tk.W)
        self.enable_novien = Checkbutton(self, '', 0.2, 0.9, 0.1)

        self.status = Label(self, '', 0.4, 0.9, 0.25, anchor=tk.W)
        Button(self, 'Save', 0.05, 0.95, 0.15).bind(
            '<Button-1>', lambda _: delay(self.save)
        )
        Button(self, 'Help', 0.20, 0.95, 0.15).bind(
            '<Button-1>',
            lambda _: delay(
                ShowHelp, os.path.join(HELP_PATH, 'chart_options.txt')
            ),
        )

        Button(self, 'Planets', 0.35, 0.95, 0.15).bind(
            '<Button-1>', lambda _: delay(self.extra_planets)
        )

        self.mps = Button(self, 'Midpoints', 0.5, 0.95, 0.15).bind(
            '<Button-1>', lambda _: delay(self.midpoints)
        )

        self.pvp_button = Button(
            self, 'Paran Aspects', 0.65, 0.95, 0.15, font=font_14
        ).bind('<Button-1>', lambda _: delay(self.prime_vertical_parans))
        backbtn = Button(self, 'Back', 0.8, 0.95, 0.15)

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
        self.vertex.checked = options.get('use_Vertex', False)
        self.node.value = options.get('Node', 0)
        self.showasp.value = options.get('show_aspects', 0)
        self.partile.checked = options.get('partile_nf', False)
        ang = options.get('angularity', {})
        ecliptical_aspects: dict = options.get('ecliptic_aspects', {})

        # Make sure the "newer" aspects considered have defaults
        for key in ['10', '7', '72', '11', '13']:
            ecliptical_aspects.setdefault(key, [0, 0, 0])

        mundane_aspects = options.get('mundane_aspects', {})

        angularity_model = ang.get('model', 2)
        if angularity_model == 0:
            # Migrate from the removed "TMSA Classic"
            angularity_model = 2

        self.bgcurve.value = angularity_model

        self.nobg.checked = ang.get('no_bg', False)
        aspect_key = ['0', '180', '90', '45', '120', '60', '30', '10']
        major_angles = ang.get('major_angles', [3.0, 7.0, 10.0])
        minor_angles = ang.get('minor_angles', [1.0, 2.0, 3.0])
        self.mpopt = options.get('midpoints', {})
        self.include_fg_under_aspects.checked = options.get(
            'include_fg_under_aspects', False
        )

        self.enable_novien.checked = options.get('enable_novien', False)

        self.pvp_aspects = options.get(
            'pvp_aspects',
            {
                'enabled': False,
                '0': [1.25, 2.0, 3.0],
                '180': [1.25, 2.0, 3.0],
                '90': [1.25, 2.0, 3.0],
            },
        )

        self.paran_aspects = options.get(
            'paran_aspects',
            {
                'enabled': False,
                '0': [1, 2, 3],
            },
        )

        # Migrate to the "allowed stuff" model

        if not 'allowed_ecliptic' in options:
            options['allowed_ecliptic'] = NATAL_DEFAULT['allowed_ecliptic']

            # User might have some aspects "disabled" by leaving orbs blank
            for key in options['allowed_ecliptic']:
                # If there's a class 1 orb specified, turn that aspect type on
                options['allowed_ecliptic'][key]['full'] = bool(
                    key in options['ecliptic_aspects']
                    and options['ecliptic_aspects'][key][0]
                )

        self.allowed_ecliptic = options['allowed_ecliptic']

        if not 'allowed_mundane' in options:
            options['allowed_mundane'] = NATAL_DEFAULT['allowed_mundane']

            for key in options['allowed_mundane']:
                options['allowed_mundane'][key]['full'] = bool(
                    key in options['mundane_aspects']
                    and options['mundane_aspects'][key][0]
                )

        self.allowed_mundane = options['allowed_mundane']

        self.extra_bodies = options.get('extra_bodies', [])
        if 'Use_Eris' in options and 'Er' not in self.extra_bodies:
            self.extra_bodies.append('Er')
        if 'Use_Sedna' in options and 'Se' not in self.extra_bodies:
            self.extra_bodies.append('Se')

        for angle_class in range(3):
            if major_angles[angle_class] == 0:
                major_angles[angle_class] = ''
            elif major_angles[angle_class].is_integer():
                major_angles[angle_class] = int(major_angles[angle_class])
            self.maj[angle_class].text = major_angles[angle_class]
            if minor_angles[angle_class] == 0:
                minor_angles[angle_class] = ''
            elif minor_angles[angle_class].is_integer():
                minor_angles[angle_class] = int(minor_angles[angle_class])
            self.min[angle_class].text = minor_angles[angle_class]

        for aspect_type in range(8):
            aspect_orbs = ecliptical_aspects[aspect_key[aspect_type]]
            if not type(aspect_orbs) == list:
                default_aspect_orbs = [0, 0, 0]
                if aspect_type in [0, 1]:
                    default_aspect_orbs = (
                        [
                            max(0.4 * aspect_orbs, 3),
                            max(0.8 * aspect_orbs, 7),
                            aspect_orbs,
                        ]
                        if aspect_orbs
                        else ['', '', '']
                    )
                if aspect_type in [2, 4, 5]:
                    default_aspect_orbs = (
                        [
                            max(0.4 * aspect_orbs, 3),
                            max(0.8 * aspect_orbs, 7),
                            aspect_orbs,
                        ]
                        if aspect_orbs
                        else ['', '', '']
                    )
                if aspect_type in [3, 6]:
                    default_aspect_orbs = (
                        [
                            max(0.4 * aspect_orbs, 1),
                            max(0.8 * aspect_orbs, 2),
                            aspect_orbs,
                        ]
                        if aspect_orbs
                        else ['', '', '']
                    )
            else:
                default_aspect_orbs = aspect_orbs
                for aspect_class in range(3):
                    if default_aspect_orbs[aspect_class] == 0:
                        default_aspect_orbs[aspect_class] = ''
                    elif isinstance(
                        default_aspect_orbs[aspect_class], (int, float)
                    ) and not isinstance(
                        default_aspect_orbs[aspect_class], bool
                    ):
                        default_aspect_orbs[aspect_class] = int(
                            default_aspect_orbs[aspect_class]
                        )
            for aspect_class in range(3):
                self.maxorbs[aspect_type][
                    aspect_class
                ].text = default_aspect_orbs[aspect_class]

        for mundane_aspect_type in range(3):
            aspect_orbs = mundane_aspects[aspect_key[mundane_aspect_type]]
            if not type(aspect_orbs) == list:
                default_aspect_orbs = [0, 0, 0]
                if mundane_aspect_type in [0, 1]:
                    default_aspect_orbs = (
                        [
                            max(0.4 * aspect_orbs, 3),
                            max(0.8 * aspect_orbs, 7),
                            aspect_orbs,
                        ]
                        if aspect_orbs
                        else ['', '', '']
                    )
                if mundane_aspect_type in [2]:
                    default_aspect_orbs = (
                        [
                            max(0.4 * aspect_orbs, 3),
                            max(0.8 * aspect_orbs, 7),
                            aspect_orbs,
                        ]
                        if aspect_orbs
                        else ['', '', '']
                    )
                if mundane_aspect_type in [3]:
                    default_aspect_orbs = (
                        [
                            max(0.4 * aspect_orbs, 1),
                            max(0.8 * aspect_orbs, 2),
                            aspect_orbs,
                        ]
                        if aspect_orbs
                        else ['', '', '']
                    )
            else:
                default_aspect_orbs = aspect_orbs
                for aspect_class in range(3):
                    if default_aspect_orbs[aspect_class] == 0:
                        default_aspect_orbs[aspect_class] = ''
                    elif default_aspect_orbs[aspect_class].is_integer():
                        default_aspect_orbs[aspect_class] = int(
                            default_aspect_orbs[aspect_class]
                        )
            for aspect_class in range(3):
                self.mmaxorbs[mundane_aspect_type][
                    aspect_class
                ].text = default_aspect_orbs[aspect_class]

    def save(self):
        if not self.optfile.text:
            self.status.error('No option file specified.')
            return
        else:
            self.status.text = ''
        majangs = []
        try:
            for aspect_label_index in range(3):
                majang = self.maj[aspect_label_index].text.strip()
                if not majang:
                    majangs.append(0)
                else:
                    f = float(majang)
                    majangs.append(f if f >= 0 else 0)
                if majangs[aspect_label_index] > 15:
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
            for aspect_label_index in range(3):
                minang = self.min[aspect_label_index].text.strip()
                if not minang:
                    minangs.append(0)
                else:
                    f = float(minang)
                    minangs.append(f if f >= 0 else 0)
                if minangs[aspect_label_index] > 5:
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
        ecliptical_max_orbs = [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ]
        mundane_max_orbs = [[], [], []]

        for aspect_label_index in range(len(self.names)):
            if self.abbrs[aspect_label_index].text[0:2] in [
                'oc ',
                'in ',
                'dc ',
            ]:
                max_allowed_orb = 5
            else:
                max_allowed_orb = 15
            try:
                for aspect_class in range(3):
                    maxorb = self.maxorbs[aspect_label_index][
                        aspect_class
                    ].text.strip()
                    if not maxorb:
                        ecliptical_max_orbs[aspect_label_index].append(0)
                    else:
                        f = float(maxorb)
                        ecliptical_max_orbs[aspect_label_index].append(
                            f if f >= 0 else 0
                        )
                    if (
                        ecliptical_max_orbs[aspect_label_index][aspect_class]
                        > max_allowed_orb
                    ):
                        self.status.error(
                            f'Orb for {self.names[aspect_label_index].text.strip().lower()} must be less than or equal to {max_allowed_orb}.'
                        )
                        return
                err = False
                if ecliptical_max_orbs[aspect_label_index][2]:
                    if (
                        ecliptical_max_orbs[aspect_label_index][1] or math.inf
                    ) >= ecliptical_max_orbs[aspect_label_index][2]:
                        err = True
                if ecliptical_max_orbs[aspect_label_index][1]:
                    if (
                        ecliptical_max_orbs[aspect_label_index][0] or math.inf
                    ) >= ecliptical_max_orbs[aspect_label_index][1]:
                        err = True
                if err:
                    self.status.error(
                        f'Inconsistent orbs for {self.names[aspect_label_index].text.strip().lower()}.'
                    )
                    return
            except Exception:
                self.status.error(
                    f'Orb for {self.names[aspect_label_index].text.strip().lower()} must be numeric or blank.'
                )
                return
            if aspect_label_index > 2:
                continue
            try:
                for aspect_class in range(3):
                    mmaxorb = self.mmaxorbs[aspect_label_index][
                        aspect_class
                    ].text.strip()
                    if not mmaxorb:
                        mundane_max_orbs[aspect_label_index].append(0)
                    else:
                        f = float(mmaxorb)
                        mundane_max_orbs[aspect_label_index].append(
                            f if f >= 0 else 0
                        )
                    if (
                        mundane_max_orbs[aspect_label_index][aspect_class]
                        > max_allowed_orb
                    ):
                        self.status.error(
                            f'Orb for mundane {self.names[aspect_label_index].text.strip().lower()} must be less than or equal to {max_allowed_orb}.'
                        )
                        return
                err = False
                if mundane_max_orbs[aspect_label_index][2]:
                    if not mundane_max_orbs[aspect_label_index][1]:
                        err = True
                    elif (
                        mundane_max_orbs[aspect_label_index][1]
                        >= mundane_max_orbs[aspect_label_index][2]
                    ):
                        err = True
                if mundane_max_orbs[aspect_label_index][1]:
                    if not mundane_max_orbs[aspect_label_index][0]:
                        err = True
                    elif (
                        mundane_max_orbs[aspect_label_index][0]
                        >= mundane_max_orbs[aspect_label_index][1]
                    ):
                        err = True
                if err:
                    self.status.error(
                        f'Inconsistent orbs for {self.names[aspect_label_index].text.strip().lower()}.'
                    )
                    return
            except Exception:
                self.status.error(
                    f'Orb for mundane {self.names[aspect_label_index].text.strip().lower()} must be numeric or blank.'
                )
                return
        options = self.optfile.text.strip()
        if self.output:
            self.output.text = options
        filename = options.replace(' ', '_') + '.opt'
        filepath = os.path.join(OPTION_PATH, filename)
        options = {}

        options['use_Vertex'] = self.vertex.checked
        options['Node'] = self.node.value
        options['show_aspects'] = self.showasp.value
        options['partile_nf'] = self.partile.checked
        options['angularity'] = {}
        options['angularity']['model'] = self.bgcurve.value
        options['angularity']['no_bg'] = self.nobg.checked
        options['angularity']['major_angles'] = majangs
        options['angularity']['minor_angles'] = minangs
        options['extra_bodies'] = self.extra_bodies
        options[
            'include_fg_under_aspects'
        ] = self.include_fg_under_aspects.checked
        options['enable_novien'] = self.enable_novien.checked

        aspect_key_list = [
            '0',
            '180',
            '90',
            '45',
            '120',
            '60',
            '30',
            '10',
            '16',
            '5',
            '7',
            '11',
            '13',
        ]

        options['allowed_ecliptic'] = self.allowed_ecliptic
        options['allowed_mundane'] = self.allowed_mundane

        options['ecliptic_aspects'] = {}
        for aspect_label_index in range(len(aspect_key_list)):
            options['ecliptic_aspects'][
                aspect_key_list[aspect_label_index]
            ] = []

        options['mundane_aspects'] = {}
        for aspect_label_index in range(3):
            options['mundane_aspects'][
                aspect_key_list[aspect_label_index]
            ] = []
        options['angularity']['model'] = self.bgcurve.value

        for aspect_label_index in range(len(aspect_key_list)):
            if aspect_label_index >= len(self.maxorbs):
                options['ecliptic_aspects'][
                    aspect_key_list[aspect_label_index]
                ] = [0, 0, 0]
            else:
                for aspect_class in range(3):
                    text = self.maxorbs[aspect_label_index][aspect_class].text
                    options['ecliptic_aspects'][
                        aspect_key_list[aspect_label_index]
                    ].append(float(text) if text else 0)
        for aspect_label_index in range(3):
            for aspect_class in range(3):
                text = self.mmaxorbs[aspect_label_index][aspect_class].text
                options['mundane_aspects'][
                    aspect_key_list[aspect_label_index]
                ].append(float(text) if text else 0)

        options['midpoints'] = self.mpopt

        options['pvp_aspects'] = self.pvp_aspects
        options['paran_aspects'] = self.paran_aspects

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

    def finish_pvp_options(self):
        status_text = ''
        if self.paran_aspects:
            status_text = 'Paran'
        else:
            self.paran_aspects = {
                'enabled': False,
                '0': [1, 2, 3],
            }

        if self.pvp_aspects:
            if self.paran_aspects:
                status_text = 'Paran, prime vertical paran options'
            else:
                status_text = 'Prime vertical paran options'
        else:
            self.pvp_aspects = {
                'enabled': False,
                '0': [1.25, 2.0, 3.0],
                '180': [1.25, 2.0, 3.0],
                '90': [1.25, 2.0, 3.0],
            }

        self.status.text = (
            f'{status_text} changed.'
            if status_text
            else 'Paran and PVP options unchanged.'
        )

    def finish_extra_bodies(self, extra_bodies):
        if sorted(self.extra_bodies) != sorted(extra_bodies):
            self.status.text = 'Extra planet options changed.'
            self.extra_bodies = extra_bodies
        else:
            self.status.text = 'Extra planet options unchanged.'

    def midpoints(self):
        MidpointOptions(self.optfile.text, self.mpopt, self.finish_mp)

    def extra_planets(self):
        ExtraPlanetOptions(
            self.optfile.text, self.extra_bodies, self.finish_extra_bodies
        )

    def prime_vertical_parans(self):
        PVPOptions(
            self.optfile.text,
            self.pvp_aspects,
            self.paran_aspects,
            self.finish_pvp_options,
        )
