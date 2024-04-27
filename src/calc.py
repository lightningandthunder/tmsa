# Copyright 2021-2024 Mike Nelson, Mike Verducci

# This file is part of Time Matters Sidereal Astrology (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, 
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>. 

from init import *
from swe import *
from show import Report
from show2 import Report2
from widgets import *

planet_names = ["Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", \
               "Eris", "Sedna", "Mean Node", "True Node"]
planet_index = [1, 0] + [i for i in range(2, 10)] + [146199, 100377, 10, 11]

def to360(value):
    if value >= 0.0 and value < 360.0: return value   
    if value >= 360: return to360(value - 360.0)
    if value < 0.0: return to360(value + 360.0)       

class Chart: 
    def __init__(self, chart, temporary, burst = False):
        self.jd = julday(chart["year"], chart["month"], chart["day"], chart["time"] + chart["correction"], chart["style"])
        self.long = chart["longitude"]
        if chart["zone"] == "LAT":
            self.jd = calc_lat_to_lmt(self.jd, self.long)            
        self.ayan = calc_ayan(self.jd)
        chart["ayan"] = self.ayan
        self.oe = calc_oe(self.jd)
        chart["oe"] = self.oe
        self.lat = chart["latitude"]
        (cusps, angles) = calc_cusps(self.jd, self.lat , self.long)
        self.ramc = angles[0]
        chart["cusps"] = cusps
        chart["ramc"] = self.ramc
        chart["Vertex"] = [angles[1], calc_house_pos(self.ramc, self.lat, self.oe, to360(angles[1] + self.ayan), 0)]
        chart["Eastpoint"] = [angles[2], calc_house_pos(self.ramc, self.lat, self.oe, to360(angles[2] + self.ayan), 0)]
        for i in range(len(planet_index)):
            pi = planet_index[i]
            pn = planet_names[i]
            data = calc_planet(self.jd, pi)
            chart[pn] = data
            data = calc_azimuth(self.jd, self.long, self.lat, to360(chart[pn][0] + self.ayan), chart[pn][1])
            chart[pn] += data
            data = calc_house_pos(self.ramc, self.lat, self.oe, to360(chart[pn][0] + self.ayan), chart[pn][1])
            chart[pn] += [data]
        self.save_and_print(chart, temporary, burst)
                 
    def save_and_print(self, chart, temporary, burst):
        try:
            optfile = chart["options"].replace(" ", "_") + ".opt"
            with open(os.path.join(OPTION_PATH, optfile)) as datafile:
                options = json.load(datafile)
        except Exception:
            tkmessagebox.showerror("File Error", f"Unable to open '{optfile}'.")
            return
        filename = make_chart_path(chart, temporary)
        if not burst:
            try:
                with open(RECENT_FILE, "r") as datafile:
                    recent = json.load(datafile)
            except Exception:
                recent = []
        if not os.path.exists(filename): 
            os.makedirs(os.path.dirname(filename), exist_ok=True) 
        try:
            with open(filename, "w") as datafile:
                json.dump(chart, datafile, indent = 4)
        except Exception as e:
                tkmessagebox.showerror("Unable to save file", f"{e}")
                return
        if not burst:
            if filename in recent: recent.remove(filename)
            recent.insert(0, filename)
            try:
                with open(RECENT_FILE, "w") as datafile:
                    json.dump(recent, datafile, indent = 4)
            except Exception:
                pass
        if chart.get("base_chart", None):
            self.precess(chart["base_chart"])
            self.report = Report2(chart, temporary, options)
        else:
            self.report = Report(chart, temporary, options)
        
    def precess(self, chart):
        for pn in planet_names:
            pd = chart[pn]
            pd[3:5] = cotrans([pd[0] + self.ayan, pd[1], pd[2]], self.oe)
            pd[5:7] = calc_azimuth(self.jd, self.long, self.lat, to360(pd[0] + self.ayan), pd[1])
            pd[7] = calc_house_pos(self.ramc, self.lat, self.oe, to360(pd[0] + self.ayan), pd[1])
            chart[pn] = pd    
       
