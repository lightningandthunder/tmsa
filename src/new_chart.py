# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters Sidereal Astrology (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, 
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>. 

from datetime import datetime as dt
import json
import os
import random

import pytz
from timezonefinder import TimezoneFinder
from init import *
from calc import Chart
from locations import Locations
from widgets import *
from geopy import Nominatim
import anglicize
import us
import tkinter.filedialog as tkfiledialog
from constants import DS, DQ

class NewChart(Frame):
    def __init__(self, oldchart = None):
        chart = {}
        super().__init__()          
        Label(self, "First Name", .15, 0, .15, anchor = tk.W)
        self.fne = Entry(self, "", .3, .0, .3)
        self.fne.focus()
        Label(self, "Last Name", .15, .05, .15, anchor = tk.W)
        self.lne = Entry(self, "", .3, .05, .3)
        Label(self, "Chart Type", .15, .1, .15, anchor = tk.W)
        self.ctype = Entry(self, "Natal", .3, .1, .3, focus = False)
        Label(self, "Date " + DATE_FMT, .15, .15, .15, anchor = tk.W)
        if DATE_FMT == "D M Y":
            self.dated = Entry(self, "", .3, .15, .1)
            self.datem = Entry(self, "", .4, .15, .1)
        else:
            self.datem = Entry(self, "", .3, .15, .1)
            self.dated = Entry(self, "", .4, .15, .1)
        self.datem.bind("<KeyRelease>", lambda _: delay(check_num, self.datem, 12))
        self.dated.bind("<KeyRelease>", lambda _: delay(check_num, self.dated, 31))
        self.datey = Entry(self, "", .5, .15, .1)
        self.datey.bind("<KeyRelease>", lambda _: delay(check_snum, self.datey, -2999, 3000))
        self.datey.bind("<FocusOut>", lambda _: delay(self.check_style)) 
        self.bce = Checkbutton(self, "BC/BCE", .6, .15, .1, focus = False)
        self.old = Checkbutton(self, "OS", .7, .15, .1, focus = False)
        Label(self, "Time H M S", .15, .2, .15, anchor = tk.W)
        self.timeh = Entry(self, "", .3, .2, .1)
        maxh = 12 if TIME_FMT == "AM/PM" else 23
        self.timeh.bind("<KeyRelease>", lambda _: delay(check_num, self.timeh, maxh))
        self.timem = Entry(self, "", .4, .2, .1)
        self.timem.bind("<KeyRelease>", lambda _: delay(check_num, self.timem, 59))
        self.times = Entry(self, "0", .5, .2, .1)
        self.times.bind("<KeyRelease>", lambda _: delay(check_num, self.times, 59))
        self.tmfmt = Radiogroup(self)
        if TIME_FMT == "24 Hour":
            Radiobutton(self, self.tmfmt, 2, "24 Hour Clock", .6, .2, .2)
            self.tmfmt.value = 2
        else:
            Radiobutton(self, self.tmfmt, 0, "AM", .6, .2, .1)
            Radiobutton(self, self.tmfmt, 1, "PM", .7, .2, .1)
        Label(self, "Location", .15, .25, .15, anchor = tk.W)
        self.loc = Entry(self, "", .3, .25, .3)
        self.loc.bind("<KeyRelease>", lambda _: self.enable_find)
        Button(self,"Recent", .6, .25, .1).bind("<Button-1>", lambda _ : delay(self.recent_loc))
        self.findbtn = Button(self, "Find", .7, .25, .1)
        self.findbtn.bind("<Button-1>", lambda _ : delay(self.find))
        Label(self, "Lat D M S", .15, .3, .15, anchor = tk.W)
        self.latd = Entry(self, "", .3, .3, .1)
        self.latd.bind("<KeyRelease>", lambda _: delay(check_num, self.latd, 89))
        self.latm = Entry(self, "", .4, .3, .1)
        self.latm.bind("<KeyRelease>", lambda _: delay(check_num, self.latm, 59))
        self.lats = Entry(self, "0", .5, .3, .1)
        self.lats.bind("<KeyRelease>", lambda _: delay(check_num, self.lats, 59))
        self.latdir = Radiogroup(self)
        Radiobutton(self, self.latdir, 0, "North", .6, .3, .1)
        Radiobutton(self, self.latdir, 1, "South", .7, .3, .1)
        Label(self, "Long D M S", .15, .35, .15, anchor = tk.W) 
        self.longd = Entry(self, "", .3, .35, .1)
        self.longd.bind("<KeyRelease>", lambda _: delay(check_num, self.longd, 180))
        self.longm = Entry(self, "", .4, .35, .1)
        self.longm.bind("<KeyRelease>", lambda _: delay(check_num, self.longm, 59))
        self.longs = Entry(self, "0", .5, .35, .1)
        self.longs.bind("<KeyRelease>", lambda _: delay(check_num, self.longs, 59))
        self.longdir = Radiogroup(self)
        Radiobutton(self, self.longdir, 0, "East ", .6, .35, .1)
        Radiobutton(self, self.longdir, 1, "West ", .7, .35, .1)
        self.longdir.value = "1"
        Label(self, "Time Zone", .15, .4, .15, anchor = tk.W)
        self.tz = Entry(self, "", .3, .4, .3)
        Label(self, "TZ Corr H M S", .15, .45, .15, anchor = tk.W)
        self.tzch = Entry(self, "", .3, .45, .1)
        self.tzch.bind("<KeyRelease>", lambda _: delay(check_num, self.tzch, 23))
        self.tzcm = Entry(self, "0", .4, .45, .1)
        self.tzcm.bind("<KeyRelease>", lambda _: delay(check_num, self.tzcm, 59))
        self.tzcs = Entry(self, "0", .5, .45, .1)
        self.tzcs.bind("<KeyRelease>", lambda _: delay(check_num, self.tzcs, 59))
        self.tzcdir = Radiogroup(self)
        Radiobutton(self, self.tzcdir, 0, "East ", .6, .45, .1)
        Radiobutton(self, self.tzcdir, 1, "West ", .7, .45, .1)
        self.tzcdir.value = 1
        Label(self, "Notes", .15, .5, .15, anchor = tk.W)
        self.notes = Entry(self, "", .3, .5, .3)
        Label(self, "Options", .15, .55, .15, anchor = tk.W)
        self.options = Entry(self, "Default Natal", .3, .55, .3)
        if os.path.exists(STUDENT_FILE): self.options.text = "Student Natal"
        Button(self, "Select", .6, .55, .1).bind("<Button-1>", lambda _ : delay(self.select_options))
        Button(self, "Temporary", .7, .55, .1).bind("<Button-1>", lambda _ : delay(self.temp_options))
        Button(self, "Calculate", .1, .7, .2).bind("<Button-1>", lambda _ : delay(self.calculate, chart))
        self.istemp = Radiogroup(self)
        Radiobutton(self, self.istemp, 0, "Permanent Chart", .3, .6, .25)
        Radiobutton(self, self.istemp, 1, "Temporary Chart", .5, .6, .25)
        Button(self, "Clear", .3, .7, .2).bind("<Button-1>", lambda _ : delay(self.clear))
        Button(self, "Help", .5, .7, .2).bind("<Button-1>", lambda _ : delay(ShowHelp, HELP_PATH + r"\newchart.txt"))
        Button(self, "Back", .7, .7, .20).bind("<Button-1>", lambda _ : delay(self.destroy))
        self.status = Label(self, "", 0, .8, 1)
        self.suffix = None
        if oldchart: 
            self.populate(oldchart)
        elif oldchart is not None:
            now = dt.utcnow()
            self.fne.text = "Chart Of The Moment"
            self.ctype.text = "Event"
            self.datem.text = now.strftime("%m")
            self.dated.text = now.strftime("%d")
            self.datey.text = now.strftime("%Y")
            self.old.checked = False
            h = "%I" if TIME_FMT == "AM/PM" else "%H"
            self.timeh.text = now.strftime(h)
            self.timem.text = now.strftime("%M")
            self.times.text = now.strftime("%S")
            if TIME_FMT != "24 Hour":
                self.tmfmt.value = 1 if now.strftime("%p") == "PM" else 0
            self.tz.text = "UT"
            self.tzch.text = 0
            self.tzcm.text = 0
            self.tzcs.text = 0
            self.tzcdir.value = 0  
            self.istemp.value = 1
        if HOME_LOC and not oldchart:
            self.loc.text = HOME_LOC[0]
            value = HOME_LOC[1]
            if value < 0:
                value = -value
                self.latdir.value = 1
            else:
                self.latdir.value = 0
            deg = int(value)
            value = (value - deg) * 60
            min = int(value)
            value = (value - min) * 60
            sec = round(value)
            if sec == 60:
                sec = 0
                min += 1
            if min == 60:
                min = 0
                deg += 1
            self.latd.text = deg
            self.latm.text = min
            self.lats.text = sec
            value = HOME_LOC[2]
            if value < 0:
                value = -value
                self.longdir.value = 1
            else:
                self.longdir.value = 0
            deg = int(value)
            value = (value - deg) * 60
            min = int(value)
            value = (value - min) * 60
            sec = round(value)
            if sec == 60:
                sec = 0
                min += 1
            if min == 60:
                min = 0
                deg += 1
            self.longd.text = deg
            self.longm.text = min
            self.longs.text = sec
            
        
            
    def enable_find(self): self.findbtn.disabled = False
        
                 
    def check_style(self):
        try:
            y = int(self.datey.text)
        except Exception:
            return
        self.old.checked = True if y < 1583 else False  
        
    def good_date_time(self, y, m, d, hour, min, sec):
        if not self.bce.checked and y < 1:
            self.datey.text = -y + 1
            self.bce.checked = True    
        if y < 1 or y > 3000:
            self.status.error("Year must be between 1 and 3000.", self.datey)
            return False
        if self.bce.checked: y = -y + 1
        if  m < 1 or m > 12:
            self.status.error("Month must be between 1 and 12.", self.datem)
            return False
        if d < 1 or d > 31:
            self.status.error("Day must be between 1 and 31.", self.dated)
            return False
        z = str(y) if y > 0 else  str(-y + 1) + " BCE"
        if self.old.checked and y > 1582:
            if  not tkmessagebox.askyesno("Are you sure?", f"Is {d} {month_abrev[m -1]} {z} old style (Julian)?"): return False
        elif not self.old.checked and y <= 1582:
            if  not tkmessagebox.askyesno("Are you sure?", f"Is {d} {month_abrev[m -1]} {z} new style (Gregorian)?"): return False
        time = hour + min/60 + sec/3600
        if TIME_FMT == "24 Hour":
            if time < 0 or time >= 24:
                self.status.error("Time must be between 0:0:0 and 23:59:59", self.timeh)
                return False
        else:
            if time == 12:
                if self.tmfmt.value:
                    message =  "The chosen time 12:00:00 PM means noon.\n"
                    message += "For midnight at the beginning of the day, chose AM.\n"
                    message += "For midnight at the end of the day, choose AM and add a day to the date."
                else:
                    message =  "The chosen time 12:00:00 AM means midnight at the beginning of the day.\n" 
                    message += "For noon, chose PM\n" 
                    message += "For midnight at the end of the day, choose AM and add a day to the date."
                if not tkmessagebox.askyesno("Is this correct?", message): return False
            if time < 0 or time >= 13:
                self.status.error("Time must be between 0:0:0 and 12:59:59", self.timeh)
                return False
            if time >= 12: time -= 12
            if self.tmfmt.value == 1: time += 12   
        return True
        
    def loc_finish(self, selected):
        if selected is None: return
        self.findbtn.disabled = True
        self.loc.text = selected[0]
        direc = "N"
        value = selected[1]
        if value < 0:
            value = -value
            direc = "S"
        latd = int(value)
        value = (value - latd) * 60
        latm = int(value)
        value = (value - latm) * 60
        lats = round(value)
        if lats == 60:
            lats == 0
            latm += 1
        if latm == 60:
            latm = 0
            latd += 1
        self.latd.text = latd
        self.latm.text = latm
        self.lats.text = lats
        self.latdir.value = 0 if direc == "N" else 1
        direc = "E"
        value = selected[2]
        if value < 0:
            value = -value
            direc = "W"
        longd = int(value)
        value = (value - longd) * 60
        longm = int(value)
        value = (value - longm) * 60
        longs = round(value)
        if longs == 60:
            longs == 0
            longm += 1
        if longm == 60:
            longm = 0
            longd += 1
        self.longd.text = longd
        self.longm.text = longm
        self.longs.text = longs
        self.longdir.value = 0 if direc == "E" else 1
        try:
            y = int(self.datey.text)
            mo = int(self.datem.text)
            d = int(self.dated.text)
            h = int(self.timeh.text)
            mi = int(self.timem.text)
            s = int(self.times.text or "0")
        except Exception:
            return self.status.error("Invalid date or time.")
        geolocator = Nominatim(user_agent = f"TMSA 0.4 {random.randrange(0, 100000):05d}")         
        try: location = geolocator.geocode(self.loc.text)
        except Exception: return self.status.error(f"Unable to connect to location database.")
        if not location: return self.status.error(f"'{self.loc.text}' not in database.")
        if y < 1880:
            self.tz.text = "LMT"
            value =  location.longitude / 15
            if value < 0: 
                value = -value
                self.tzcdir.value = 1
            else:
                self.tzcdir.value = 0
            hour = int(value)
            value = (value - hour) * 60
            min = int(value)
            value = (value - min) * 60
            sec = round(value)
            if sec == 60:
                sec = 0
                min += 1
            if min == 60:
                min = 0
                hour += 1
            self.tzch.text = hour
            self.tzcm.text = min
            self.tzcs.text = sec
        elif y < 1970:
            self.status.error("Must enter timezone information manually.", self.tz)
        else:
            try:    
                tz = pytz.timezone(TimezoneFinder().timezone_at(lng=location.longitude, lat=location.latitude))
                t = datetime(y, mo, d, h, mi, s)  
                if self.tz.text != "UT":
                    off = tz.utcoffset(t)
                    self.tz.text = tz.localize(t).tzname()
            except Exception as e:
                self.status.error(f"Database error.", self.tz)
                return
            if self.tz.text != "UT":    
                if "-1 day" in str(off):
                    self.tzcdir.value = 1
                    value = abs(off.seconds / 3600 - 24)
                else:
                    self.tzcdir.value = 0   
                    value = off.seconds / 3600
                hour = int(value)
                value = (value - hour) * 60
                min = int(value)
                value = (value - min) * 60
                sec = round(value)
                if sec == 60:
                    sec = 0
                    min += 1
                if min == 60:
                    min = 0
                    hour += 1
                self.tzch.text = hour
                self.tzcm.text = min
                self.tzcs.text = sec
            self.status.error("", self.notes) 
        
    def recent_loc(self):
        try:
            with open(LOCATIONS_FILE, "r") as datafile:
                recs = json.load(datafile)
            delay(Locations, recs, self.loc_finish)
            if len(recs) == 0 : self.status.error("No saved locations.")
        except Exception:
            self.status.error("Can't open 'locations.json'.")
                
    def find(self): 
        if self.findbtn.disabled: return
        self.status.text = ""
        if not self.loc.text: return self.status.error("Location required.", self.loc)
        geolocator = Nominatim(user_agent = f"TMSA 0.4 {random.randrange(0, 100000):05d}")  
        self.loc.text = normalize(self.loc.text)
        try: location = geolocator.geocode(self.loc.text)
        except Exception: return self.status.error(f"Unable to connect to location database.", self.latd)
        if not location: return self.status.error(f"'{self.loc.text}' not in database.", self.latd)
        loc = str(location).split(",")
        locx = []
        ok = True
        for i in range(len(loc)):
            temp = anglicize.anglicize(loc[i])
            ok = all(ord(c) <= 256 for c in loc[i])
            if not ok: break
            locx.append(temp)
        if ok:
            loc = locx
            city = loc[0].strip()
            country = loc[-1].strip()
            if country == "United States":
                state = None
                for i in range(1, len(loc) - 1):
                    state = us.states.lookup(loc[i])
                    if state: break
                if state: 
                    country =  f"{state.abbr} USA"
                else:
                    country = "USA"
            if country == "France" and len(loc) == 5:
                if "France" not in loc[-2]:
                    country = loc[-3].strip()
            self.loc.text = f"{city}, {country}"  
        direc = "N"
        value = location.latitude
        if value < 0:
            value = -value
            direc = "S"
        latd = int(value)
        value = (value - latd) * 60
        latm = int(value)
        value = (value - latm) * 60
        lats = round(value)
        if lats == 60:
            lats == 0
            latm += 1
        if latm == 60:
            latm = 0
            latd += 1
        self.latd.text = latd
        self.latm.text = latm
        self.lats.text = lats
        self.latdir.value = 0 if direc == "N" else 1
        direc = "E"
        value = location.longitude
        if value < 0:
            value = -value
            direc = "W"
        longd = int(value)
        value = (value - longd) * 60
        longm = int(value)
        value = (value - longm) * 60
        longs = round(value)
        if longs == 60:
            longs == 0
            longm += 1
        if longm == 60:
            longm = 0
            longd += 1
        self.longd.text = longd
        self.longm.text = longm
        self.longs.text = longs
        self.longdir.value = 0 if direc == "E" else 1
        try:
            y = int(self.datey.text)
            mo = int(self.datem.text)
            d = int(self.dated.text)
            h = int(self.timeh.text)
            mi = int(self.timem.text)
            s = int(self.times.text or "0")
        except Exception:
            return self.status.error("Invalid date or time.")
        if not self.good_date_time(y, mo, d, h, mi, s): return
        if y < 1880:
            self.tz.text = "LMT"
            value =  location.longitude / 15
            if value < 0: 
                value = -value
                self.tzcdir.value = 1
            else:
                self.tzcdir.value = 0
            hour = int(value)
            value = (value - hour) * 60
            min = int(value)
            value = (value - min) * 60
            sec = round(value)
            if sec == 60:
                sec = 0
                min += 1
            if min == 60:
                min = 0
                hour += 1
            self.tzch.text = hour
            self.tzcm.text = min
            self.tzcs.text = sec
        elif y < 1970:
            self.status.error("Must enter timezone information manually.", self.tz)
        else:
            try:    
                tz = pytz.timezone(TimezoneFinder().timezone_at(lng=location.longitude, lat=location.latitude))
                t = datetime(y, mo, d, h, mi, s)  
                if self.tz.text != "UT":
                    off = tz.utcoffset(t)
                    self.tz.text = tz.localize(t).tzname()
            except Exception as e:
                self.status.error(f"Database error.", self.tz)
                return
            if self.tz.text != "UT":
                if "-1 day" in str(off):
                    self.tzcdir.value = 1
                    value = abs(off.seconds / 3600 - 24)
                else:
                    self.tzcdir.value = 0   
                    value = off.seconds / 3600
                hour = int(value)
                value = (value - hour) * 60
                min = int(value)
                value = (value - min) * 60
                sec = round(value)
                if sec == 60:
                    sec = 0
                    min += 1
                if min == 60:
                    min = 0
                    hour += 1
                self.tzch.text = hour
                self.tzcm.text = min
                self.tzcs.text = sec
            self.status.error("", self.notes) 
        
    def populate(self, chart): 
        name = chart["name"]
        self.suffix = None
        if ";" in name:
            name = name.split(";")
            self.suffix = name[1]
            name = name[0]   
        if ", " in name:
            (last, first) = name.split(", ", 1)
        else:
            first = name
            last = ""
        self.fne.text = first
        self.lne.text = last
        self.ctype.text = chart["type"]
        self.loc.text = chart["location"]
        value = chart["latitude"]
        if value < 0:
            value = -value
            self.latdir.value = 1
        else:
            self.latdir.value = 0
        deg = int(value)
        value = (value - deg) * 60
        min = int(value)
        value = (value - min) * 60
        sec = round(value)
        if sec == 60:
            sec = 0
            min += 1
        if min == 60:
            min = 0
            deg += 1
        self.latd.text = deg
        self.latm.text = min
        self.lats.text = sec
        value = chart["longitude"]
        if value < 0:
            value = -value
            self.longdir.value = 1
        else:
            self.longdir.value = 0
        deg = int(value)
        value = (value - deg) * 60
        min = int(value)
        value = (value - min) * 60
        sec = round(value)
        if sec == 60:
            sec = 0
            min += 1
        if min == 60:
            min = 0
            deg += 1
        self.longd.text = deg
        self.longm.text = min
        self.longs.text = sec
        if chart["year"] < 1:
            self.datey.text = -chart["year"] + 1 
            self.bce.checked = True
        else:
            self.datey.text = chart["year"]
            self.bce.checked = False
        self.datem.text = chart["month"]
        self.dated.text = chart["day"]
        self.old.checked = not chart["style"]
        value = chart["time"]
        hour = int(value)
        value = (value - hour) * 60
        min = int(value)
        value = (value - min) * 60
        sec = round(value)
        if sec == 60:
            sec = 0
            min += 1
        if min == 60:
            min = 0
            hour += 1
        if TIME_FMT == "AM/PM":
            time = chart["time"]
            if time > 12:
                if hour > 12: hour -= 12
                self.tmfmt.value = 1
            elif time < 12: 
                if hour == 0: hour = 12
                self.tmfmt.value = 0   
            else:
                self.tmfmt.value = 0
        self.timeh.text = hour
        self.timem.text = min
        self.times.text = sec
        self.tz.text = chart["zone"]
        value = chart["correction"]
        if value < 0:
            value = -value
            self.tzcdir.value = 0
        else:
            self.tzcdir.value = 1
        hour = int(value)
        value = (value - hour) * 60
        min = int(value)
        value = (value - min) * 60
        sec = round(value)
        if sec == 60:
            sec = 0
            min += 1
        if min == 60:
            min = 0
            hour += 1
        self.tzch.text = hour
        self.tzcm.text = min
        self.tzcs.text = sec
        self.notes.text = chart["notes"]
        self.options.text = chart["options"]
        if self.options.text == "Temporary":
            self.select_options()
        
    def select_options(self): 
        name = tkfiledialog.askopenfilename(initialdir = OPTION_PATH, filetypes = [["Option Files", ".opt"]])
        if not name: return
        name = name.replace("/", "\\")
        if not name.startswith(OPTION_PATH): return
        text = name.replace(OPTION_PATH, "").replace("_", " ")
        self.options.text = text[1:-4]
        
    def temp_options(self):
        from chart_options import ChartOptions
        ChartOptions(self.options.text, True, self.options)
        
    def clear(self):
        self.destroy()
        NewChart()
        
    def calculate(self, chart): 
        self.status.text = ""  
        self.findbtn.disabled = False
        fn = normalize(self.fne.text)
        ln = normalize(self.lne.text)
        if fn and ln:
            name = ln + ", " + fn
        else:
            name = fn or ln 
        if not name: return self.status.error("Name must be specified.", self.fne)
        if self.suffix: name += f";{self.suffix}"
        chart["name"] = name
        ctype = normalize(self.ctype.text)
        if not ctype:  return self.status.error("Chart type must be specified.", self.ctype)
        chart["type"] = ctype
        chart["class"] = "N"
        try:
            y = int(self.datey.text)
            m = int(self.datem.text)
            d = int(self.dated.text)
        except Exception:
            ctl = self.datem if DATE_FMT =="M D Y" else self.dated
            return self.status.error("Date must be numeric.", ctl)
        if not self.bce.checked and y < 1:
            y = -y + 1
            self.datey.text = y
            self.bce.checked = True    
        if y < 1 or y > 3000: return self.status.error("Year must be between 1 and 3000.", self.datey)
        if self.bce.checked: y = -y + 1
        chart["year"] = y
        if  m < 1 or m > 12: return self.status.error("Month must be between 1 and 12.", self.datem)
        chart["month"] = m
        if d < 1 or d > 31: return self.status.error("Day must be between 1 and 31.", self.dated)   
        chart["day"] = d
        z = str(y) if y > 0 else  str(-y + 1) + " BCE"
        if self.old.checked and y > 1582:
            if  not tkmessagebox.askyesno("Are you sure?", f"Is {d} {month_abrev[m -1]} {z} old style (Julian)?"): return
        elif not self.old.checked and y <= 1582:
            if  not tkmessagebox.askyesno("Are you sure?", f"Is {d} {month_abrev[m -1]} {z} new style (Gregorian)?"): return
        chart["style"] =  0 if self.old.checked else 1
        try: time = int(self.timeh.text)  + int(self.timem.text)/60 + int(self.times.text or "0")/3600
        except Exception: return self.status.error("Time must be numeric.", self.timeh)
        if TIME_FMT == "24 Hour":
            if time < 0 or time >= 24: 
                return self.status.error("Time must be between 0:0:0 and 23:59:59", self.timeh)
        else:
            if time == 12:
                if self.tmfmt.value:
                    message =  "The chosen time 12:00:00 PM means noon.\n"
                    message += "For midnight at the beginning of the day, chose AM.\n"
                    message += "For midnight at the end of the day, choose AM and add a day to the date."
                else:
                    message =  "The chosen time 12:00:00 AM means midnight at the beginning of the day.\n" 
                    message += "For noon, chose PM\n" 
                    message += "For midnight at the end of the day, choose AM and add a day to the date."
                if not tkmessagebox.askyesno("Is this correct?", message): return
            if time < 0 or time >= 13:
                return self.status.error("Time must be between 0:0:0 and 12:59:59", self.timeh)
            if time >= 12: time -= 12
            if self.tmfmt.value == 1: time += 12
        chart["time"] = time
        chart["location"] = normalize(self.loc.text)
        if not chart["location"]: return self.status.error("Location must be specified.", self.loc)
        try: lat = int(self.latd.text) + int(self.latm.text)/60 + int(self.lats.text or "0")/3600
        except Exception: return self.status.error("Latitude must be numeric.", self.latd)
        if lat<0 or lat > 89.99: return self.status.error(f"Latitude must be between 0{DS} and 89{DS}59'59{DQ}.", self.latd)
        if self.latdir.value == 1: lat = -lat
        chart["latitude"] = lat
        try: long = int(self.longd.text) + int(self.longm.text)/60 + int(self.longs.text or "0")/3600
        except Exception: return self.status.error("Longitude must be numeric.", self.longd)
        if long < 0 or long > 180: return  self.status.error(f"Longitude must be between 0{DS} and 180{DS}.")
        if self.longdir.value == 1: long = -long
        chart["longitude"] = long
        self.save_location(chart)
        zone = normalize(self.tz.text) or "UT" 
        chart["zone"] = zone  
        if zone.upper() in ["LMT", "LAT"]:
            value =  chart["longitude"] / 15
            if value < 0: 
                value = -value
                self.tzcdir.value = 1
            else:
                self.tzcdir.value = 0
            hour = int(value)
            value = (value - hour) * 60
            min = int(value)
            value = (value - min) * 60
            sec = round(value)
            if sec == 60:
                sec = 0
                min += 1
            if min == 60:
                min = 0
                hour += 1
            self.tzch.text = hour
            self.tzcm.text = min
            self.tzcs.text = sec
        try: tzcorr = int(self.tzch.text) + int(self.tzcm.text or "0")/60 + int(self.tzcs.text or "0")/3600
        except Exception: return self.status.error("Time zone correction must be numeric.", self.tzch)
        if tzcorr < 0 or tzcorr >= 24: return self.status.error("Time zone correction be between 0:0:0 and 23:59:59", self.tzch)
        if self.tzcdir.value == 0: tzcorr = -tzcorr
        chart["correction"] = tzcorr
        chart["notes"] = normalize(self.notes.text, True)
        chart["options"] = self.options.text.strip() or "Default Natal"
        Chart(chart, self.istemp.value).report.show()
        
    def save_location(self, chart):
        try:
            with open(LOCATIONS_FILE, "r") as datafile:
                locs = json.load(datafile)
            newloc = [chart["location"], chart["latitude"], chart["longitude"]]
            if newloc in locs: locs.remove(newloc) 
            locs.insert(0, newloc)
            if len(locs) > 50: locs = locs[0:50]
            with open(LOCATIONS_FILE, "w") as datafile:
                locs = json.dump(locs, datafile, indent = 4)
        except Exception:
            pass
    