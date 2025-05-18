# Copyright 2025 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from src import *
from src.models.options import ProgramOptions
from src.swe import *
from src.user_interfaces.widgets import *


class MoreSolunars(Frame):
    def __init__(
        self, more_charts: dict, program_options: ProgramOptions, callback
    ):
        super().__init__()
        self.more_charts = more_charts
        self.program_options = program_options
        self.callback = callback

        Label(self, 'Solar Returns', 0.5, 0, 0.3, anchor=tk.W)
        self.nsr = Checkbutton(self, 'NSR', 0.325, 0.05, 0.1)
        self.ten_day_solar = Checkbutton(self, '10-Dy SR', 0.45, 0.05, 0.1)

        self.nsr.bind(
            '<Button-1>',
            lambda _: delay(self.handle_nsr_click),
        )
        self.ten_day_solar.bind(
            '<Button-1>',
            lambda _: delay(self.handle_10_day_click),
        )

        self.ksr = Checkbutton(self, 'KSR', 0.325, 0.1, 0.1)
        self.demi_ksr = Checkbutton(self, 'DKSR', 0.45, 0.1, 0.1)

        self.ksr.config(state=tk.DISABLED)
        self.demi_ksr.config(state=tk.DISABLED)

        if self.program_options.quarti_returns_enabled:
            self.quarti_ksr_1 = Checkbutton(self, 'QKSR1', 0.575, 0.1, 0.1)
            self.quarti_ksr_3 = Checkbutton(self, 'QKSR3', 0.7, 0.1, 0.1)

            self.quarti_ksr_1.config(state=tk.DISABLED)
            self.quarti_ksr_3.config(state=tk.DISABLED)

        Label(self, 'Lunar Returns', 0.5, 0.15, 0.3, anchor=tk.W)
        self.nlr = Checkbutton(self, 'NLR', 0.325, 0.2, 0.1)
        self.eighteen_hour_lunar = Checkbutton(
            self, '18-Hr LR', 0.45, 0.2, 0.1
        )

        self.nlr.bind(
            '<Button-1>',
            lambda _: delay(self.handle_nlr_click),
        )
        self.eighteen_hour_lunar.bind(
            '<Button-1>',
            lambda _: delay(self.handle_18_hour_click),
        )

        self.klr = Checkbutton(self, 'KLR', 0.325, 0.25, 0.1)
        self.demi_klr = Checkbutton(self, 'DKLR', 0.45, 0.25, 0.1)

        if self.program_options.quarti_returns_enabled:
            self.quarti_klr_1 = Checkbutton(self, 'QKLR1', 0.575, 0.25, 0.1)
            self.quarti_klr_3 = Checkbutton(self, 'QKLR3', 0.7, 0.25, 0.1)

            self.quarti_klr_1.config(state=tk.DISABLED)
            self.quarti_klr_3.config(state=tk.DISABLED)

        self.sar = Checkbutton(self, 'SAR', 0.325, 0.3, 0.1)
        self.dsar = Checkbutton(self, 'DSAR', 0.45, 0.3, 0.1)

        if self.program_options.quarti_returns_enabled:
            self.quarti_sar_1 = Checkbutton(self, 'QSAR1', 0.575, 0.3, 0.1)
            self.quarti_sar_3 = Checkbutton(self, 'QSAR3', 0.7, 0.3, 0.1)

        self.ksar = Checkbutton(self, 'KSAR', 0.325, 0.35, 0.1)
        self.dksar = Checkbutton(self, 'DKSAR', 0.45, 0.35, 0.1)

        if self.program_options.quarti_returns_enabled:
            self.quarti_ksar_1 = Checkbutton(self, 'QKSAR1', 0.575, 0.35, 0.1)
            self.quarti_ksar_3 = Checkbutton(self, 'QKSAR3', 0.7, 0.35, 0.1)

            self.quarti_ksar_1.config(state=tk.DISABLED)
            self.quarti_ksar_3.config(state=tk.DISABLED)

        self.klr.config(state=tk.DISABLED)
        self.demi_klr.config(state=tk.DISABLED)

        self.ksar.config(state=tk.DISABLED)
        self.dksar.config(state=tk.DISABLED)

        Label(self, 'Other Returns', 0.5, 0.4, 0.3, anchor=tk.W)
        self.solilunar = Checkbutton(self, 'SoLu', 0.325, 0.45, 0.1)
        self.demi_solilunar = Checkbutton(self, 'DSoLu', 0.45, 0.45, 0.1)

        if self.program_options.quarti_returns_enabled:
            self.quarti_solilunar_1 = Checkbutton(
                self, 'QSoLu1', 0.575, 0.45, 0.1
            )
            self.quarti_solilunar_3 = Checkbutton(
                self, 'QSoLu3', 0.7, 0.45, 0.1
            )

        self.lunisolar = Checkbutton(self, 'LuSo', 0.325, 0.5, 0.1)
        self.demi_lunisolar = Checkbutton(self, 'DLuSo', 0.45, 0.5, 0.1)

        if self.program_options.quarti_returns_enabled:
            self.quarti_lunisolar_1 = Checkbutton(
                self, 'QLuSo1', 0.575, 0.5, 0.1
            )
            self.quarti_lunisolar_3 = Checkbutton(
                self, 'QLuSo3', 0.7, 0.5, 0.1
            )

        self.syr = Checkbutton(self, 'SYR', 0.325, 0.55, 0.1)
        self.syr.config(state=tk.DISABLED)

        self.lsr = Checkbutton(self, 'LSR', 0.325, 0.6, 0.1)
        self.dlsr = Checkbutton(self, 'DLSR', 0.45, 0.6, 0.1)

        if self.program_options.quarti_returns_enabled:
            self.quarti_lsr_1 = Checkbutton(self, 'QLSR1', 0.575, 0.6, 0.1)
            self.quarti_lsr_3 = Checkbutton(self, 'QLSR3', 0.7, 0.6, 0.1)

        self.nsr.checked = more_charts.get('nsr', False)
        self.ten_day_solar.checked = more_charts.get('10-day', False)

        if self.nsr.checked:
            self.ten_day_solar.checked = False
            self.ten_day_solar.config(state=tk.DISABLED)

        if self.ten_day_solar.checked:
            self.nsr.checked = False
            self.nsr.config(state=tk.DISABLED)

        self.ksr.checked = more_charts.get('ksr', False)
        self.demi_ksr.checked = more_charts.get('demi-ksr', False)

        if self.program_options.quarti_returns_enabled:
            self.quarti_ksr_1.checked = more_charts.get('quarti-ksr-1', False)
            self.quarti_ksr_3.checked = more_charts.get('quarti-ksr-3', False)

        self.nlr.checked = more_charts.get('nlr', False)
        self.eighteen_hour_lunar.checked = more_charts.get('18-hour', False)

        if self.nlr.checked:
            self.eighteen_hour_lunar.checked = False
            self.eighteen_hour_lunar.config(state=tk.DISABLED)

        if self.eighteen_hour_lunar.checked:
            self.nlr.checked = False
            self.nlr.config(state=tk.DISABLED)

        self.klr.checked = more_charts.get('klr', False)
        self.demi_klr.checked = more_charts.get('demi-klr', False)

        if self.program_options.quarti_returns_enabled:
            self.quarti_klr_1.checked = more_charts.get('quarti-klr-1', False)
            self.quarti_klr_3.checked = more_charts.get('quarti-klr-3', False)

        self.sar.checked = more_charts.get('sar', False)
        self.dsar.checked = more_charts.get('demi-sar', False)

        if self.program_options.quarti_returns_enabled:
            self.quarti_sar_1.checked = more_charts.get('quarti-sar-1', False)
            self.quarti_sar_3.checked = more_charts.get('quarti-sar-3', False)

        self.ksar.checked = more_charts.get('ksar', False)
        self.dksar.checked = more_charts.get('demi-ksar', False)

        if self.program_options.quarti_returns_enabled:
            self.quarti_ksar_1.checked = more_charts.get(
                'quarti-ksar-1', False
            )
            self.quarti_ksar_3.checked = more_charts.get(
                'quarti-ksar-3', False
            )

        self.solilunar.checked = more_charts.get('solu', False)
        self.demi_solilunar.checked = more_charts.get('demi-solu', False)

        if self.program_options.quarti_returns_enabled:
            self.quarti_solilunar_1.checked = more_charts.get(
                'quarti-solu-1', False
            )
            self.quarti_solilunar_3.checked = more_charts.get(
                'quarti-solu-3', False
            )

        self.lunisolar.checked = more_charts.get('luso', False)
        self.demi_lunisolar.checked = more_charts.get('demi-luso', False)

        if self.program_options.quarti_returns_enabled:
            self.quarti_lunisolar_1.checked = more_charts.get(
                'quarti-luso-1', False
            )
            self.quarti_lunisolar_3.checked = more_charts.get(
                'quarti-luso-3', False
            )

        self.syr.checked = more_charts.get('syr', False)

        self.lsr.checked = more_charts.get('lsr', False)
        self.dlsr.checked = more_charts.get('demi-lsr', False)

        if self.program_options.quarti_returns_enabled:
            self.quarti_lsr_1.checked = more_charts.get('quarti-lsr-1', False)
            self.quarti_lsr_3.checked = more_charts.get('quarti-lsr-3', False)

        Button(self, 'Save', 0.2, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.save)
        )
        Button(self, 'Clear', 0.4, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.clear)
        )
        Button(self, 'Back', 0.6, 0.95, 0.2).bind(
            '<Button-1>', lambda _: delay(self.back)
        )

    def handle_nsr_click(self):
        self.ten_day_solar.checked = False
        self.ten_day_solar.config(
            state=tk.NORMAL if self.nsr.checked else tk.DISABLED
        )

    def handle_10_day_click(self):
        self.nsr.checked = False
        self.nsr.config(
            state=tk.NORMAL if self.ten_day_solar.checked else tk.DISABLED
        )

    def handle_nlr_click(self):
        self.eighteen_hour_lunar.checked = False
        self.eighteen_hour_lunar.config(
            state=tk.NORMAL if self.nlr.checked else tk.DISABLED
        )

    def handle_18_hour_click(self):
        self.nlr.checked = False
        self.nlr.config(
            state=tk.NORMAL
            if self.eighteen_hour_lunar.checked
            else tk.DISABLED
        )

    def clear(self):
        self.nsr.checked = False
        self.ten_day_solar.checked = False
        self.ksr.checked = False
        self.demi_ksr.checked = False

        if self.program_options.quarti_returns_enabled:
            self.quarti_ksr_1.checked = False
            self.quarti_ksr_3.checked = False

        self.nlr.checked = False
        self.eighteen_hour_lunar.checked = False

        self.klr.checked = False
        self.demi_klr.checked = False

        if self.program_options.quarti_returns_enabled:
            self.quarti_klr_1.checked = False
            self.quarti_klr_3.checked = False

        self.sar.checked = False
        self.dsar.checked = False

        if self.program_options.quarti_returns_enabled:
            self.quarti_sar_1.checked = False
            self.quarti_sar_3.checked = False

        self.ksar.checked = False
        self.dksar.checked = False

        if self.program_options.quarti_returns_enabled:
            self.quarti_ksar_1.checked = False
            self.quarti_ksar_3.checked = False

        self.solilunar.checked = False
        self.demi_solilunar.checked = False

        if self.program_options.quarti_returns_enabled:
            self.quarti_solilunar_1.checked = False
            self.quarti_solilunar_3.checked = False

        self.lunisolar.checked = False
        self.demi_lunisolar.checked = False

        if self.program_options.quarti_returns_enabled:
            self.quarti_lunisolar_1.checked = False
            self.quarti_lunisolar_3.checked = False

        self.syr.checked = False

        self.lsr.checked = False
        self.dlsr.checked = False

        if self.program_options.quarti_returns_enabled:
            self.quarti_lsr_1.checked = False
            self.quarti_lsr_3.checked = False

    def save(self):
        self.more_charts = {
            'nsr': self.nsr.checked,
            '10-day': self.ten_day_solar.checked,
            'ksr': self.ksr.checked,
            'demi-ksr': self.demi_ksr.checked,
            'nlr': self.nlr.checked,
            '18-hour': self.eighteen_hour_lunar.checked,
            'klr': self.klr.checked,
            'demi-klr': self.demi_klr.checked,
            'sar': self.sar.checked,
            'demi-sar': self.dsar.checked,
            'ksar': self.ksar.checked,
            'demi-ksar': self.dksar.checked,
            'solu': self.solilunar.checked,
            'demi-solu': self.demi_solilunar.checked,
            'luso': self.lunisolar.checked,
            'demi-luso': self.demi_lunisolar.checked,
            'syr': self.syr.checked,
            'lsr': self.lsr.checked,
            'demi-lsr': self.dlsr.checked,
        }

        if self.program_options.quarti_returns_enabled:
            self.more_charts.update(
                {
                    'quarti-ksr-1': self.quarti_ksr_1.checked,
                    'quarti-ksr-3': self.quarti_ksr_3.checked,
                    'quarti-klr-1': self.quarti_klr_1.checked,
                    'quarti-klr-3': self.quarti_klr_3.checked,
                    'quarti-sar-1': self.quarti_sar_1.checked,
                    'quarti-sar-3': self.quarti_sar_3.checked,
                    'quarti-ksar-1': self.quarti_ksar_1.checked,
                    'quarti-ksar-3': self.quarti_ksar_3.checked,
                    'quarti-solu-1': self.quarti_solilunar_1.checked,
                    'quarti-solu-3': self.quarti_solilunar_3.checked,
                    'quarti-luso-1': self.quarti_lunisolar_1.checked,
                    'quarti-luso-3': self.quarti_lunisolar_3.checked,
                    'quarti-lsr-1': self.quarti_lsr_1.checked,
                    'quarti-lsr-3': self.quarti_lsr_3.checked,
                }
            )

        self.callback(self.more_charts)
        self.destroy()

    def back(self):
        self.callback(self.more_charts)
        self.destroy()
