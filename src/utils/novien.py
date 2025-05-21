from io import TextIOWrapper
from src.models.charts import Aspect, ChartObject, ChartWheelRole, PlanetData
from src.models.options import Options
from src.utils.chart_utils import (
    NEG_SIGN,
    POS_SIGN,
    SIGNS_SHORT,
    center_align,
    left_align,
    signed_degree_minute,
    signed_minute_second,
    write_triple_columns_to_file,
    zod_sec_with_sign,
)
from src.utils.format_utils import to360


def write_novien_data_table_to_file(
    chart: ChartObject, options: Options, chartfile: TextIOWrapper
) -> dict[str, PlanetData]:
    novien_planets: dict[str, PlanetData] = {}

    # Calculate novien positions
    for [key, data] in chart.iterate_points(options):
        novien_longitude = calc_novien_longitude(data.longitude)
        novien_planets[key] = PlanetData(
            name=key,
            short_name=data.short_name,
            number=data.number,
            longitude=novien_longitude,
            latitude=0,
            speed=data.speed * 9,
            right_ascension=0,
            declination=0,
            azimuth=0,
            role=ChartWheelRole.NOVIEN,
            is_stationary=data.is_stationary,
        )

    moon_noviens = calc_successive_noviens(
        novien_planets['Moon'].longitude, first_already_novien=True
    )
    sun_noviens = calc_successive_noviens(
        novien_planets['Sun'].longitude, first_already_novien=True
    )

    # Headers
    chartfile.write('\nPl  Nov. Long  Speed   Natal Long')

    # Set up the extra fields floating off to the side, by row index

    extras = [
        "   Moon's Noviens",
        f'    1 {zod_sec_with_sign(moon_noviens[0])}',
        f'    2 {zod_sec_with_sign(moon_noviens[1])}',
        f'    3 {zod_sec_with_sign(moon_noviens[2])}',
        '',
        "   Sun's Noviens",
        f'    1 {zod_sec_with_sign(sun_noviens[0])}',
        f'    2 {zod_sec_with_sign(sun_noviens[1])}',
        f'    3 {zod_sec_with_sign(sun_noviens[2])}',
    ]

    for (index, (key, data)) in enumerate(novien_planets.items()):
        chartfile.write('\n')
        chartfile.write(left_align(data.short_name, 2))

        sign = SIGNS_SHORT[int(data.longitude // 30)]

        if sign in POS_SIGN[data.short_name]:
            plus_minus = '+'
        elif sign in NEG_SIGN[data.short_name]:
            plus_minus = '-'
        else:
            plus_minus = ' '
        chartfile.write(f'{plus_minus} ')

        # Write planet data to info table
        chartfile.write(zod_sec_with_sign(data.longitude))

        if data.is_stationary:
            chartfile.write('S')
        else:
            chartfile.write(' ')

        if abs(data.speed) >= 100:
            chartfile.write(
                signed_degree_minute(data.speed, degree_digits=3) + ' '
            )
        elif abs(data.speed) >= 1:
            chartfile.write(
                signed_degree_minute(data.speed, degree_digits=3) + ' '
            )
        else:
            chartfile.write(
                signed_minute_second(data.speed, minute_digits=3) + ' '
            )

        chartfile.write(zod_sec_with_sign(chart.planets[key].longitude))

        if index < len(extras):
            chartfile.write(extras[index])

    chartfile.write('\n')
    return novien_planets


def write_novien_aspectarian(
    aspects_by_class: list[list[Aspect]],
    chartfile: TextIOWrapper,
    table_width: int,
):
    aspect_class_headers = [
        ' Class 1  ',
        ' Class 2  ',
        ' Novien-to-Natal',
    ]

    # find aspect width by finding the longest aspect name
    aspect_width = 0
    for aspect_class in aspects_by_class:
        if aspect_class:
            aspect_width = len(str(aspect_class[0]))
            break

    if len(aspects_by_class[2]) and not len(aspects_by_class[1]):
        del aspects_by_class[1]
        del aspect_class_headers[1]

    if any(
        [
            True
            for aspect_class in aspect_class_headers
            if len(aspect_class) > 0
        ]
    ):
        chartfile.write('-' * table_width + '\n')

        # Class 1
        left_header = aspect_class_headers[0]

        chartfile.write(
            center_align(
                left_header,
                width=max(aspect_width, len(left_header)),
            )
        )

        center_header = aspect_class_headers[1]

        # This represents how much of a shift right there is between
        # the left-aligned first column and the center-aligned second column
        gap = (26 - aspect_width) + ((26 - aspect_width) // 2)
        if gap > 0:
            chartfile.write(' ' * gap)

        chartfile.write(
            center_align(
                center_header, width=max(aspect_width, len(center_header))
            )
        )

        # The same math applies to the gap between the center-aligned second column
        # and the right-aligned third column
        if gap > 0:
            chartfile.write(' ' * gap)

        right_header = aspect_class_headers[2]

        chartfile.write(
            left_align(
                right_header, width=max(aspect_width, len(right_header))
            )
        )
        chartfile.write('\n')

    # Write aspects from all classes to file
    write_triple_columns_to_file(aspects_by_class, chartfile)


# This should not be needed anymore; same output as the other one below
def __calc_novien_longitude_using_0_taurus(longitude: float) -> float:
    # Re-express longitude as distance past 0° Taurus
    taurus_offset = longitude

    if taurus_offset < 30:
        taurus_offset += 330
    else:
        taurus_offset -= 30

    # Convert to 9th harmonic
    taurus_offset = (taurus_offset * 9) % 360

    # To get the appropriate sign, this needs to remain
    # based on 0° Taurus
    return to360(taurus_offset + 30)


def calc_novien_longitude(longitude: float) -> float:
    navamsa_position = (longitude * 9) % 360

    # To get the appropriate sign, this needs to be converted
    # to be based on 0° Taurus
    return to360(navamsa_position + 120)


def calc_successive_noviens(
    longitude: float, count=3, first_already_novien=False
) -> list[float]:
    noviens = []

    previous_longitude = longitude
    counter = count

    if first_already_novien:
        noviens.append(longitude)
        counter -= 1

    for _ in range(counter):
        previous_longitude = calc_novien_longitude(previous_longitude)
        noviens.append(previous_longitude)

    return noviens
