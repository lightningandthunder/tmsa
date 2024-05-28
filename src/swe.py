# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from ctypes import (
    CDLL,
    byref,
    c_char_p,
    c_int,
    c_void_p,
    c_double,
    POINTER,
    c_char,
    create_string_buffer,
)
from init import *

dll = CDLL(DLL_PATH)

swe_set_ephe = getattr(dll, '_swe_set_ephe_path@4')
swe_set_ephe.argtypes = [c_char_p]
swe_set_ephe.restype = c_void_p
swe_set_ephe(EPHE_PATH.encode())

swe_julday = getattr(dll, '_swe_julday@24')
swe_julday.argtypes = [c_int, c_int, c_int, c_double, c_int]
swe_julday.restype = c_double

swe_revjul = getattr(dll, '_swe_revjul@28')
swe_revjul.argtypes = [
    c_double,
    c_int,
    POINTER(c_int),
    POINTER(c_int),
    POINTER(c_int),
    POINTER(c_double),
]
swe_revjul.restype = c_void_p

swe_calc_ut = getattr(dll, '_swe_calc_ut@24')
swe_calc_ut.argtypes = [
    c_double,
    c_int,
    c_int,
    POINTER(c_double * 6),
    POINTER(c_char * 256),
]

swe_get_ayanamsa_ex_ut = getattr(dll, '_swe_get_ayanamsa_ex_ut@20')
swe_get_ayanamsa_ex_ut.argtypes = [
    c_double,
    c_int,
    POINTER(c_double),
    POINTER(c_char * 256),
]

swe_houses_ex = getattr(dll, '_swe_houses_ex@40')
swe_houses_ex.argtypes = [
    c_double,
    c_int,
    c_double,
    c_double,
    c_int,
    POINTER(c_double * 13),
    POINTER(c_double * 10),
]

swe_house_pos = getattr(dll, '_swe_house_pos@36')
swe_house_pos.argtypes = [
    c_double,
    c_double,
    c_double,
    c_int,
    POINTER(c_double * 2),
    POINTER(c_char * 256),
]
swe_house_pos.restype = c_double

swe_azalt = getattr(dll, '_swe_azalt@40')
swe_azalt.argtypes = [
    c_double,
    c_int,
    POINTER(c_double * 3),
    c_double,
    c_double,
    POINTER(c_double * 3),
    POINTER(c_double * 3),
]

swe_lat_to_lmt = getattr(dll, '_swe_lat_to_lmt@24')
swe_lat_to_lmt.argtypes = [
    c_double,
    c_double,
    POINTER(c_double),
    POINTER(c_char * 256),
]

swe_solcross_ut = getattr(dll, '_swe_solcross_ut@24')
swe_solcross_ut.argtypes = [c_double, c_double, c_int, POINTER(c_char * 256)]
swe_solcross_ut.restype = c_double

swe_mooncross_ut = getattr(dll, '_swe_mooncross_ut@24')
swe_mooncross_ut.argtypes = [c_double, c_double, c_int, POINTER(c_char * 256)]
swe_mooncross_ut.restype = c_double.restype = c_double

swe_cotrans = getattr(dll, '_swe_cotrans@16')
swe_cotrans.argtypes = [POINTER(c_double * 3), POINTER(c_double * 3), c_double]


def julday(year, month, day, hour, isgreg):
    return swe_julday(year, month, day, hour, isgreg)


def calc_planet(ut, pl):
    err = create_string_buffer(256)
    pos = (c_double * 6)()
    swe_calc_ut(ut, pl, 64 * 1024 + 256, byref(pos), byref(err))
    result = []
    for i in range(len(pos)):
        if i in [0, 1, 3]:
            result.append(pos[i])
    swe_calc_ut(ut, pl, 2048 + 256, byref(pos), byref(err))
    for i in range(len(pos)):
        if i in [0, 1]:
            result.append(pos[i])
    return result


def calc_oe(ut):
    err = create_string_buffer(256)
    pos = (c_double * 6)()
    swe_calc_ut(ut, -1, 0, byref(pos), byref(err))
    result = []
    for p in pos:
        result.append(p)
    return result[0]


def calc_ayan(ut):
    err = create_string_buffer(256)
    pos = c_double()
    swe_get_ayanamsa_ex_ut(ut, 0, byref(pos), byref(err))
    return pos.value


def calc_cusps(ut, lat, long):
    cusps = (c_double * 13)()
    angles = (c_double * 10)()
    swe_houses_ex(
        ut, 64 * 1024, lat, long, ord('C'), byref(cusps), byref(angles)
    )
    cc = []
    for c in cusps:
        cc.append(c)
    aa = []
    for i in range(len(angles)):
        if i in [2, 3, 4]:
            aa.append(angles[i])
    return [cc, aa]


def calc_house_pos(ramc, glat, oe, tlong, elat):
    err = create_string_buffer(256)
    pos = (c_double * 2)(tlong, elat)
    return swe_house_pos(ramc, glat, oe, ord('C'), pos, err) * 30 - 30


def calc_azimuth(ut, glong, glat, tlong, elat):
    geo = (c_double * 3)(glong, glat, 0)
    pl = (c_double * 3)(tlong, elat, 0)
    az = (c_double * 3)()
    swe_azalt(ut, 0, byref(geo), 0, 0, byref(pl), byref(az))
    aa = []
    for i in range(len(az)):
        if i in [0, 1]:
            aa.append(az[i])
    aa[0] = (aa[0] + 180) % 360
    return aa


def calc_lat_to_lmt(lat, long):
    err = create_string_buffer(256)
    lat = c_double(lat)
    long = c_double(long)
    lmt = c_double()
    swe_lat_to_lmt(lat, long, byref(lmt), byref(err))
    return lmt.value


def revjul(ut, isgreg):
    year = c_int()
    month = c_int()
    day = c_int()
    time = c_double()
    swe_revjul(ut, isgreg, byref(year), byref(month), byref(day), byref(time))
    return (year.value, month.value, day.value, time.value)


def calc_sun_crossing(pos, ut):
    err = create_string_buffer(256)
    cross = swe_solcross_ut(pos, ut, 64 * 1024, byref(err))
    s = calc_planet(cross, 0)
    sun = s[0]
    if sun > pos + 180:
        sun -= 360
    if sun < pos:
        cross += (pos - sun + 0.5 / 86400) / s[2]
    return cross


def calc_moon_crossing(pos, ut):
    err = create_string_buffer(256)
    cross = swe_mooncross_ut(pos, ut, 64 * 1024, byref(err))
    m = calc_planet(cross, 1)
    moon = m[0]
    if moon > pos + 180:
        moon -= 360
    if moon < pos:
        cross += (pos - moon + 0.5 / 86400) / m[2]
    return cross


def cotrans(ecliptic, oe):
    ec = (c_double * 3)(*ecliptic)
    eq = (c_double * 3)()
    swe_cotrans(ec, byref(eq), -oe)
    equator = []
    for i in range(2):
        equator.append(eq[i])
    return equator
