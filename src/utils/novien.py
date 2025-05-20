from src.utils.format_utils import to360

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
