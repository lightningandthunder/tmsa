# Copyright 2025 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

import os
import json

from src import OPTION_PATH, RECENT_FILE
from src.models.charts import ChartObject, ChartWheelRole
from src.models.options import Options
from src.user_interfaces.biwheel import Biwheel
from src.user_interfaces.quadwheel import Quadwheel
from src.user_interfaces.triwheel import Triwheel
from src.user_interfaces.uniwheel import Uniwheel
from src.utils.chart_utils import make_chart_path
from src.user_interfaces.widgets import tkmessagebox


def assemble_charts(params, temporary, burst=False):
    try:
        optfile = params['options'].replace(' ', '_') + '.opt'
        with open(os.path.join(OPTION_PATH, optfile)) as datafile:
            raw_options = json.load(datafile)
    except Exception:
        tkmessagebox.showerror('File Error', f"Unable to open '{optfile}'.")
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

    chart = ChartObject(params)

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

    if params.get('chart_type', None) == 'snq':
        if params.get('use_transit'):
            transit_chart = ChartObject(params).with_role(
                ChartWheelRole.TRANSIT
            )
            progressed_chart = ChartObject(
                params['progressed_chart']
            ).with_role(ChartWheelRole.PROGRESSED)
            radix = ChartObject(params['base_chart']).with_role(
                ChartWheelRole.RADIX
            )
            return Triwheel(
                [transit_chart, progressed_chart, radix],
                temporary,
                options,
                use_progressed_angles=True,
            )

        else:
            progressed_chart = ChartObject(
                params['progressed_chart']
            ).with_role(ChartWheelRole.PROGRESSED)
            radix = ChartObject(params['base_chart']).with_role(
                ChartWheelRole.RADIX
            )

            return Biwheel(
                [progressed_chart, radix],
                temporary,
                options,
                use_progressed_angles=True,
            )

    # Kinetic Anlunar
    if params.get('progressed_chart', None) and params.get('ssr_chart', None):
        progressed_chart = params['progressed_chart']
        transit_chart = ChartObject(params).with_role(ChartWheelRole.TRANSIT)
        radix = ChartObject(params['base_chart']).with_role(
            ChartWheelRole.RADIX
        )
        ssr_chart = params['ssr_chart'].with_role(ChartWheelRole.SOLAR)

        return Quadwheel(
            [transit_chart, progressed_chart, ssr_chart, radix],
            temporary,
            options,
        )

    # Anlunar
    elif params.get('ssr_chart', None):
        return_chart = ChartObject(params).with_role(ChartWheelRole.TRANSIT)

        # This has to be pre-calculated
        ssr_chart = params['ssr_chart'].with_role(ChartWheelRole.SOLAR)

        radix = ChartObject(params['base_chart']).with_role(
            ChartWheelRole.RADIX
        )

        return Triwheel([return_chart, ssr_chart, radix], temporary, options)

    # Kinetic Solar or Lunar
    elif params.get('progressed_chart', None):
        progressed_chart = params['progressed_chart']
        transit_chart = ChartObject(params).with_role(ChartWheelRole.TRANSIT)
        radix = ChartObject(params['base_chart']).with_role(
            ChartWheelRole.RADIX
        )

        return Triwheel(
            [transit_chart, progressed_chart, radix], temporary, options
        )

    # Any other return
    elif params.get('base_chart', None):
        return_chart = ChartObject(params).with_role(ChartWheelRole.TRANSIT)
        radix = ChartObject(params['base_chart']).with_role(
            ChartWheelRole.RADIX
        )

        return Biwheel([return_chart, radix], temporary, options)
    else:
        single_chart = ChartObject(params).with_role(ChartWheelRole.NATAL)
        return Uniwheel([single_chart], temporary, options)
