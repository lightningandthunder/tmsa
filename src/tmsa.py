# Copyright 2024 Mike Nelson, Mike Verducci

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

COPYRIGHT = """Time Matters Sidereal Astrology 0.4.9.2\n
A freeware program for calculating geometrically accurate astrological charts
in the Sidereal Zodiac, as rediscovered by Cyril Fagan and Donald Bradley.
\u00a9 December 2021 by Mike Nelson (mikestar13 on Solunars).\n
Released under the GNU Affero General Public License"""
LICENSE = "https://www.gnu.org/licenses/agpl-3.0.en.html\n"
DEDEDICATION = "Dedicated to Jim Eshelman and all the good people at solunars."
SOLUNARS = "https://www.solunars.com/"
FURTHER = "For more information about Sidereal Astrology in the Western tradition, see:"
POINTS = "https://www.solunars.com/viewtopic.php?f=8&t=2259"


class StartPage(Frame):
    def __init__(self):
        super().__init__()
        global startup
        Label(self, COPYRIGHT, 0, 0, 1, .25)
        Label(self, LICENSE, 0, .25, 1, .1, font = ulfont).bind("<Button-1>", lambda _: webbrowser.open_new(LICENSE))
        Label(self, DEDEDICATION, 0, .35, 1)
        Label(self, SOLUNARS, 0, .4, 1, font = ulfont).bind("<Button-1>", lambda _: webbrowser.open_new(SOLUNARS))
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