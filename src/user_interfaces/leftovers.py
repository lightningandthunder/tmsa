def write_cosmic_state(
    self,
    chartfile: TextIOWrapper,
    planet_foreground_angles: dict[str, str],
    aspects_by_class: list[list[str]],
    planets_foreground: list[str],
):
    chart = self.charts[0]
    chartfile.write(
        chart_utils.center_align('Cosmic State', self.table_width) + '\n'
    )
    moon_sign = constants.SIGNS_SHORT[
        int(chart.planets['Moon'].longitude // 30)
    ]
    sun_sign = constants.SIGNS_SHORT[int(chart.planets['Sun'].longitude // 30)]

    for index, (planet_name, planet_info) in enumerate(
        chart_utils.iterate_allowed_planets()
    ):
        planet_short_name = planet_info['short_name']
        planet_data = chart.planets[planet_name]

        if index != 0:
            chartfile.write('\n')

        chartfile.write(planet_short_name + ' ')

        sign = constants.SIGNS_SHORT[int(planet_data.longitude // 30)]

        if sign in constants.POS_SIGN[planet_short_name]:
            plus_minus = '+'
        elif sign in constants.NEG_SIGN[planet_short_name]:
            plus_minus = '-'
        else:
            plus_minus = ' '
        chartfile.write(f'{sign}{plus_minus} ')

        # TODO - I think this is right but I'm not positive
        angle = planet_foreground_angles.get(
            planet_short_name, angles_models.NonForegroundAngles.BLANK
        )
        if angle.strip() == '':
            angle = ' '
        elif angle.strip() in [
            a.value.strip().upper() for a in angles_models.ForegroundAngles
        ]:
            angle = 'F'
        else:
            angle = 'B'
        chartfile.write(angle + ' |')

        need_another_row = False

        if self.chart.type not in chart_utils.INGRESSES:
            if planet_short_name != 'Mo':
                if moon_sign in constants.POS_SIGN[planet_short_name]:
                    chartfile.write(f' Mo {moon_sign}+')
                    need_another_row = True
                elif moon_sign in constants.NEG_SIGN[planet_short_name]:
                    chartfile.write(f' Mo {moon_sign}-')
                    need_another_row = True
            if planet_short_name != 'Su':
                if sun_sign in constants.POS_SIGN[planet_short_name]:
                    chartfile.write(f' Su {sun_sign}+')
                    need_another_row = True
                elif sun_sign in constants.NEG_SIGN[planet_short_name]:
                    chartfile.write(f' Su {sun_sign}-')
                    need_another_row = True

        aspect_list = []

        for class_index in range(3):
            for entry in aspects_by_class[class_index]:
                if planet_short_name in entry:
                    percent = str(200 - int(entry[15:18]))
                    entry = entry[0:15] + entry[20:]
                    if entry[0:2] == planet_short_name:
                        entry = entry[3:]
                    else:
                        entry = f'{entry[3:5]} {entry[0:2]}{entry[8:]}'
                    aspect_list.append([entry, percent])

        aspect_list.sort(key=lambda p: p[1] + p[0][6:11])
        if aspect_list:
            if need_another_row:
                chartfile.write('\n' + (' ' * 9) + '| ')
                need_another_row = False
            else:
                chartfile.write(' ')

        for aspect_index, aspect in enumerate(aspect_list):
            chartfile.write(aspect[0] + '   ')
            if aspect_index % 4 == 3 and aspect_index != len(aspect_list) - 1:
                chartfile.write('\n' + (' ' * 9) + '| ')

        points_to_show_midpoint_aspects_to = []
        for index, (planet_name, planet_info) in enumerate(
            chart_utils.iterate_allowed_planets(self.options)
        ):
            planet_longitude = chart.planets[planet_name].longitude
            planet_short_name = planet_info['short_name']
            if (
                (self.options.show_aspects or option_models.ShowAspect.ALL)
                == option_models.ShowAspect.ALL
                or planet_short_name in planets_foreground
            ):
                points_to_show_midpoint_aspects_to.append(
                    [planet_short_name, planet_longitude]
                )

        points_to_show_midpoint_aspects_to.append(['As', chart.cusps[1]])
        points_to_show_midpoint_aspects_to.append(['Mc', chart.cusps[10]])
        if len(points_to_show_midpoint_aspects_to) > 1 and (
            (self.options.show_aspects or option_models.ShowAspect.ALL)
            == option_models.ShowAspect.ALL
            or planet_name in planets_foreground
        ):
            # ecliptic midpoints?
            emp = []
            for remaining_planet in range(
                len(points_to_show_midpoint_aspects_to) - 1
            ):
                for k in range(
                    remaining_planet + 1,
                    len(points_to_show_midpoint_aspects_to),
                ):
                    mp = self.find_midpoint(
                        [planet_short_name, planet_data.longitude],
                        points_to_show_midpoint_aspects_to,
                        remaining_planet,
                        k,
                        self.options,
                    )
                    if mp:
                        emp.append(mp)
            if emp:
                emp.sort(key=lambda p: p[6:8])
                if need_another_row or aspect_list:
                    chartfile.write('\n' + (' ' * 9) + '| ')
                else:
                    chartfile.write(' ')
                for remaining_planet, a in enumerate(emp):
                    chartfile.write('   ' + a + '   ')
                    if (
                        remaining_planet % 4 == 3
                        and remaining_planet != len(emp) - 1
                    ):
                        chartfile.write('\n' + (' ' * 9) + '| ')

    sign = constants.SIGNS_SHORT[int(chart.cusps[1] // 30)]
    points_to_show_midpoint_aspects_to = []
    for planet_index in range(14):
        if planet_index == 10 and not self.options.get('use_Eris', 1):
            continue
        if planet_index == 11 and not self.options.get('use_Sedna', 0):
            continue
        if planet_index == 12 and self.options.get('Node', 0) != 1:
            continue
        if planet_index == 13 and self.options.get('Node', 0) != 2:
            continue
        plna = constants.PLANET_NAMES[planet_index]
        planet_longitude = chart[plna][0]
        plra = chart[plna].right_ascension
        plpvl = chart[plna].house
        planet_short_name = constants.PLANET_NAMES_SHORT[planet_index]
        if (
            self.options.get('show_aspects', 0) == 0
            or plna in planets_foreground
        ):
            points_to_show_midpoint_aspects_to.append(
                [planet_short_name, planet_longitude, plra, plpvl]
            )
    points_to_show_midpoint_aspects_to.append(['Mc', chart.cusps[10]])
    if len(points_to_show_midpoint_aspects_to) > 1:
        emp = []
        for remaining_planet in range(
            len(points_to_show_midpoint_aspects_to) - 1
        ):
            for k in range(
                remaining_planet + 1,
                len(points_to_show_midpoint_aspects_to),
            ):
                mp = self.find_midpoint(
                    ['As', chart.cusps[1]],
                    points_to_show_midpoint_aspects_to,
                    remaining_planet,
                    k,
                    self.options,
                )
                if mp:
                    emp.append(mp)
        if emp:
            emp.sort(key=lambda p: p[6:8])
            chartfile.write(f'\nAs {sign}    | ')
            for remaining_planet, a in enumerate(emp):
                chartfile.write('   ' + a + '   ')
                if (
                    remaining_planet % 4 == 3
                    and remaining_planet != len(emp) - 1
                ):
                    chartfile.write('\n' + (' ' * 9) + '| ')
    sign = constants.SIGNS_SHORT[int(chart.cusps[10] // 30)]
    points_to_show_midpoint_aspects_to[-1] = ['As', chart.cusps[1]]
    if len(points_to_show_midpoint_aspects_to) > 1:
        emp = []
        for remaining_planet in range(
            len(points_to_show_midpoint_aspects_to) - 1
        ):
            for k in range(
                remaining_planet + 1,
                len(points_to_show_midpoint_aspects_to),
            ):
                mp = self.find_midpoint(
                    ['Mc', chart.cusps[10]],
                    points_to_show_midpoint_aspects_to,
                    remaining_planet,
                    k,
                    self.options,
                )
                if mp:
                    emp.append(mp)
        if emp:
            emp.sort(key=lambda p: p[6:8])
            chartfile.write(f'\nMc {sign}    | ')
            for remaining_planet, a in enumerate(emp):
                chartfile.write('   ' + a + '   ')
                if (
                    remaining_planet % 4 == 3
                    and remaining_planet != len(emp) - 1
                ):
                    chartfile.write('\n' + (' ' * 9) + '| ')
    del points_to_show_midpoint_aspects_to[-1]
    if len(points_to_show_midpoint_aspects_to) > 1:
        emp = []
        ep = [
            'Ep',
            (chart.cusps[10] + 90) % 360,
            (chart.ramc + 90) % 360,
        ]
        ze = ['Ze', (chart.cusps[1] - 90) % 360]
        for remaining_planet in range(
            len(points_to_show_midpoint_aspects_to) - 1
        ):
            for k in range(
                remaining_planet + 1,
                len(points_to_show_midpoint_aspects_to),
            ):
                mp = self.mmp_all(
                    ep,
                    ze,
                    points_to_show_midpoint_aspects_to,
                    remaining_planet,
                    k,
                    self.options,
                )
                if mp:
                    emp.append(mp)
        if emp:
            empa = []
            empe = []
            empz = []
            for x in emp:
                if x[-1] == 'A':
                    empa.append(x[:-1])
                elif x[-1] == 'E':
                    empe.append(x[:-1])
                else:
                    empz.append(x[:-1])
            empa.sort(key=lambda p: p[6:8])
            empe.sort(key=lambda p: p[6:8])
            empz.sort(key=lambda p: p[6:8])
            if empa:
                chartfile.write(f'\nAngle    | ')
                for remaining_planet, a in enumerate(empa):
                    chartfile.write('   ' + a + '   ')
                    if (
                        remaining_planet % 4 == 3
                        and remaining_planet != len(empa) - 1
                    ):
                        chartfile.write('\n' + (' ' * 9) + '| ')
            if empe:
                chartfile.write(f'\nEp       | ')
                for remaining_planet, a in enumerate(empe):
                    chartfile.write('   ' + a + '   ')
                    if (
                        remaining_planet % 4 == 3
                        and remaining_planet != len(empe) - 1
                    ):
                        chartfile.write('\n' + (' ' * 9) + '| ')
            if empz:
                chartfile.write(f'\nZe       | ')
                for remaining_planet, a in enumerate(empz):
                    chartfile.write('   ' + a + '   ')
                    if (
                        remaining_planet % 4 == 3
                        and remaining_planet != len(empz) - 1
                    ):
                        chartfile.write('\n' + (' ' * 9) + '| ')
