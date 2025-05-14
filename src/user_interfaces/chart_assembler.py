# Copyright 2025 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from copy import deepcopy
from src import *
from src.models.charts import ChartObject, ChartWheelRole
from src.models.options import Options
from src.swe import *
from src.user_interfaces.biwheel import Biwheel
from src.user_interfaces.triwheel import Triwheel
from src.user_interfaces.uniwheel import Uniwheel
from src.user_interfaces.widgets import *
from src.utils.chart_utils import make_chart_path
from src.utils.format_utils import (
    to360,
    version_is_supported,
    version_str_to_tuple,
)


class ChartAssembler:
    def __init__(self, params, temporary, burst=False):
        # chart['version'] = (
        #     version_str_to_tuple(VERSION)
        #     if 'version' not in chart
        #     else chart['version']
        # )
        # self.jd = julday(
        #     chart['year'],
        #     chart['month'],
        #     chart['day'],
        #     chart['time'] + chart['correction'],
        #     chart['style'],
        # )
        # self.long = chart['longitude']
        # if chart['zone'] == 'LAT':
        #     self.jd = calc_lat_to_lmt(self.jd, self.long)
        # self.ayan = calc_ayan(self.jd)
        # chart['ayan'] = self.ayan
        # self.oe = calc_obliquity(self.jd)
        # chart['oe'] = self.oe
        # self.lat = chart['latitude']
        # (cusps, angles) = calc_cusps(self.jd, self.lat, self.long)
        # self.ramc = angles[0]
        # chart['cusps'] = cusps
        # chart['ramc'] = self.ramc
        # chart['Vertex'] = [
        #     angles[1],
        #     calc_house_pos(
        #         self.ramc, self.lat, self.oe, to360(angles[1] + self.ayan), 0
        #     ),
        # ]
        # chart['Eastpoint'] = [
        #     angles[2],
        #     calc_house_pos(
        #         self.ramc, self.lat, self.oe, to360(angles[2] + self.ayan), 0
        #     ),
        # ]

        # for [long_name, planet_definition] in PLANETS.items():
        #     planet_index = planet_definition['number']
        #     [
        #         longitude,
        #         latitude,
        #         speed,
        #         right_ascension,
        #         declination,
        #     ] = calc_planet(self.jd, planet_index)
        #     [azimuth, altitude] = calc_azimuth(
        #         self.jd,
        #         self.long,
        #         self.lat,
        #         to360(longitude + self.ayan),
        #         latitude,
        #     )
        #     house_position = calc_house_pos(
        #         self.ramc,
        #         self.lat,
        #         self.oe,
        #         to360(longitude + self.ayan),
        #         latitude,
        #     )
        #     meridian_longitude = calc_meridian_longitude(azimuth, altitude)

        #     data = [
        #         longitude,
        #         latitude,
        #         speed,
        #         right_ascension,
        #         declination,
        #         azimuth,
        #         altitude,
        #         meridian_longitude,
        #         house_position,
        #     ]

        #     chart[long_name] = data

        self.save_and_print(params, temporary, burst)

    def save_and_print(self, params, temporary, burst):
        try:
            optfile = params['options'].replace(' ', '_') + '.opt'
            with open(os.path.join(OPTION_PATH, optfile)) as datafile:
                raw_options = json.load(datafile)
        except Exception:
            tkmessagebox.showerror(
                'File Error', f"Unable to open '{optfile}'."
            )
            return
        filename = make_chart_path(params, temporary)
        if not burst:
            try:
                with open(RECENT_FILE, 'r') as datafile:
                    recent = json.load(datafile)
            except Exception:
                recent = []
        if not os.path.exists(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        chart = ChartObject.from_calculation(params)

        try:
            chart.to_file(filename)
        except Exception as e:
            tkmessagebox.showerror('Unable to save file', f'{e}')
            return
        if not burst:
            if filename in recent:
                recent.remove(filename)
            recent.insert(0, filename)
            try:
                with open(RECENT_FILE, 'w') as datafile:
                    json.dump(recent, datafile, indent=4)
            except Exception:
                pass

        options = Options(raw_options)

        if params.get('ssr_chart', None):
            return_chart = ChartObject.from_calculation(params).with_role(
                ChartWheelRole.TRANSIT
            )

            # TODO - this is gonna have to be from calculation also
            ssr_chart = ChartObject.from_calculation(
                params['ssr_chart']
            ).with_role(ChartWheelRole.SOLAR)

            radix = ChartObject(params['base_chart']).with_role(
                ChartWheelRole.RADIX
            )

            self.report = Triwheel(
                [return_chart, ssr_chart, radix], temporary, options
            )

        elif params.get('base_chart', None):
            return_chart = ChartObject(params).with_role(
                ChartWheelRole.TRANSIT
            )
            radix = ChartObject(params['base_chart']).with_role(
                ChartWheelRole.RADIX
            )
            if not version_is_supported(radix.version):
                if not tkmessagebox.askyesno(
                    'Radix chart version is out of date and needs to be updated',
                    f'Do you want to recalculate the radix chart to the newest version?',
                ):
                    return None

                radix = self.recalculate_radix(params['base_chart'])
                if not radix:
                    return None

            self.report = Biwheel([return_chart, radix], temporary, options)
        else:
            single_chart = ChartObject(params).with_role(ChartWheelRole.NATAL)
            self.report = Uniwheel([single_chart], temporary, options)

    def recalculate_radix(self, chart):
        recalculated_chart = deepcopy(chart)
        recalculated_chart['version'] = version_str_to_tuple(VERSION)

        # Write recalculated data file
        filename = make_chart_path(recalculated_chart, False)
        with open(filename, 'w') as datafile:
            json.dump(recalculated_chart, datafile, indent=4)

        # Write recalculated chart file
        radix = ChartObject(recalculated_chart).with_role(ChartWheelRole.RADIX)
        try:
            optfile = recalculated_chart['options'].replace(' ', '_') + '.opt'
            if not os.path.exists(os.path.join(OPTION_PATH, optfile)):
                optfile = 'Natal_Default.opt'

            with open(os.path.join(OPTION_PATH, optfile)) as datafile:
                options = json.load(datafile)
        except Exception:
            tkmessagebox.showerror(
                'File Error',
                f"Unable to open '{optfile}' during recalculation of radix.",
            )
            return None

        # This is important because it's not actually a radix;
        # it is its own thing in this context.
        recalculated_natal = ChartObject(recalculated_chart).with_role(
            ChartWheelRole.NATAL
        )
        Uniwheel([recalculated_natal], False, Options(options))

        # But we still want to return the *radix* specifically
        return radix
