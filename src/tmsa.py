# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters Sidereal Astrology (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, 
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>. 


from init import *
from chart_options import ChartOptions
from ingresses import Ingresses
from new_chart import NewChart
from program_options import ProgramOptions
from select_chart import SelectChart
from widgets import *
import webbrowser
import os
import shutil
import json
from constants import VERSION

COPYRIGHT = f"""Time Matters Sidereal Astrology {VERSION}\n
A freeware program for calculating geometrically \n
accurate astrological charts in the Sidereal Zodiac, \n
as rediscovered by Cyril Fagan and Donald Bradley.\n
\u00a9 2021-2024 James A. Eshelman.
Created by Mike Nelson (mikestar13)
and developed further by Mike Verducci.\n
Released under the GNU Affero General Public License"""
LICENSE = "www.gnu.org/licenses/agpl-3.0.en.html"
DEDEDICATION = "Dedicated to our colleagues and collaborators at"
SOLUNARS = "www.solunars.com"
FURTHER = "For more information about Sidereal Astrology, see:"
POINTS = "www.solunars.com/viewtopic.php?f=8&t=2259"


class StartPage(Frame):
    def __init__(self):
        super().__init__()
        global startup
        Label(self, COPYRIGHT, 0, 0, 1, .30)
        Label(self, LICENSE, 0, .30, 1, .05, font = ulfont).bind("<Button-1>", lambda _: webbrowser.open_new(LICENSE))
        Label(self, DEDEDICATION, 0, .35, 1)
        Label(self, SOLUNARS, 0, .40, 1, font = ulfont).bind("<Button-1>", lambda _: webbrowser.open_new(SOLUNARS))
        Label(self, FURTHER, 0,.45, 1)
        Label(self, POINTS, 0, .5, 1, font = ulfont).bind("<Button-1>", lambda _: webbrowser.open_new(POINTS))
        start = Button(self,"Chart Of The Moment", .2, .6, .2)
        start.bind("<Button-1>", lambda _ : delay(NewChart, False))    
        start.focus()
        Button(self,"New Chart", .4, .6, .2).bind("<Button-1>", lambda _ : delay(NewChart)) 
        Button(self,"Select Chart", .6, .6, .2).bind("<Button-1>", lambda _ : delay(SelectChart))
        Button(self, "Ingresses", .2, .65, .2).bind("<Button-1>", lambda _ : delay(Ingresses))
        default = "Student Natal" if os.path.exists(STUDENT_FILE) else "Default Natal"
        Button(self,"Chart Options", .4, .65, .2).bind("<Button-1>", lambda _ : delay(ChartOptions, default))
        Button(self, "Predictive Options", .6 ,.65, .2).bind("<Button-1>", lambda _ : delay(NotImplemented))
        Button(self, "Help", .2, .7, .2).bind("<Button-1>", lambda _ : delay(ShowHelp, HELP_PATH + r"\main.txt"))
        Button(self, "Program Options", .4, .7, .2).bind("<Button-1>", lambda _ : delay(ProgramOptions)) 
        Button(self, "Exit Program", .6, .7, .2).bind("<Button-1>", lambda _ : delay(main.destroy))
        if not startup: return   
        startup = False    
        try:
            if os.path.exists(TEMP_CHARTS): shutil.rmtree(TEMP_CHARTS)
            os.mkdir(TEMP_CHARTS)
        except Exception:
            return
        try:
            with open(RECENT_FILE, "r") as datafile:
                recs = json.load(datafile)
        except Exception:
            return
        recs = [rec for rec in recs if "\\temporary\\" not in rec]
        if len(recs) > 100: recs = recs[0:100]
        try:
            with open(RECENT_FILE, "w") as datafile:
                recs = json.dump(recs, datafile, indent = 4)
        except Exception:
            pass
            
        
StartPage()
main.mainloop()