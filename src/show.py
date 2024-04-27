# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters Sidereal Astrology (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, 
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>. 

from datetime import datetime
import math
import os
from show_util import *
from constants import VERSION

def display(chart, planet):
    pd = chart[planet] 
    index = planet_names.index(planet)
    pa = planet_abrev[index]
    d = pa + " " + zod_min(pd[0]) 
    if index < 14:
        d += " " + fmt_dm(pd[-1] % 30)
    else:
        d = center(d, 16)
    return d
    
def get_class(value):
    value = value.lower()
    if value[0:3] in ["cap", "can", "ari" , "lib"]:
        return "SI" if "solar" in value else "LI"
    if "return" in value:
        return "SR" if "solar" in value else "LR"
    return "N"
    
class Report:
    def __init__(self, chart, temporary, options):
        rows = 65
        cols = 69
        arr = [[" " for i in range(cols)] for j in range(rows)]
        filename = make_chart_path(chart, temporary)
        filename = filename[0:-3] + "txt"
        try: 
            chartfile = open(filename, "w")
        except Exception as e:
            tkmessagebox.showerror(f"Unable to open file:", f"{e}") 
            return
        with chartfile:
            self.cclass = chart.get("class", None)
            if not self.cclass: self.cclass = get_class(chart["type"])
            chartfile.write("\n")
            for i in range(cols):
                arr[0][i] = "-"
                arr[16][i] = "-"
                if i <= 17 or i >= 51: arr[32][i] = "-"
                arr[48][i] = "-"
                arr[64][i] = "-"
            for i in range(rows): 
                arr[i][0] = "|"
                arr[i][17] = "|"
                if i <= 16 or i >= 48: arr[i][34] = "|"
                arr[i][51] = "|"
                arr[i][68] = "|"
            for i in range(0, rows, 16):
                for j in range(0, cols, 17):
                    if i == 32 and j == 34: continue 
                    arr[i][j] = "+"
            cusps = chart["cusps"]
            cusps = [zod_min(c) for c in cusps]
            arr[0][14:20] = cusps[11]    
            arr[0][31:37] = cusps[10]   
            arr[0][48:54] = cusps[9]    
            arr[16][0:6] = cusps[12]
            arr[16][63:69] = cusps[8]
            arr[32][0:6] = cusps[1]
            arr[32][63:69] = cusps[7]    
            arr[48][0:6] = cusps[2]
            arr[48][63:69] = cusps[6]     
            arr[64][14:20] = cusps[3]    
            arr[64][31:37] = cusps[4]   
            arr[64][48:54] = cusps[5]
            if chart["type"] not in ingresses:
                name = chart["name"]
                if ";" in name:
                    name = name.split(";")
                    name = name[0]
                arr[21][18:51] = center(name)
            chtype = chart["type"]
            if chtype.endswith(" Single Wheel"): chtype = chtype.replace(" Single Wheel", "")
            arr[23][18:51] = center(chtype)
            line = str(chart["day"]) + " " + month_abrev[chart["month"] - 1] + " " 
            line += f"{chart['year']} " if chart["year"] > 0 else f"{-chart['year'] + 1} BCE "
            if not chart["style"]: line += "OS "
            line += fmt_hms(chart["time"]) + " " + chart["zone"]
            arr[25][18:51] = center(line)
            arr[27][18:51] = center(chart["location"])
            arr[29][18:51] = center(fmt_lat(chart["latitude"]) + " " + fmt_long(chart["longitude"]))
            arr[31][18:51] = center("UT " + fmt_hms(chart["time"] + chart["correction"]))
            arr[33][18:51] = center("RAMC " + fmt_dms(chart["ramc"]))
            arr[35][18:51] = center("OE " + fmt_dms(chart["oe"]))
            arr[37][18:51] = center("SVP " + zod_sec(360 - chart["ayan"]))
            arr[39][18:51] = center("Sidereal Zodiac")
            arr[41][18:51] = center("Campanus Houses")
            arr[43][18:51] = center(chart["notes"] or "* * * * *")
            
            x = [ 1,  1, 18, 35, 52, 52, 52, 52, 35, 18, 1,  1]
            y = [33, 49, 49, 49, 49, 33, 17,  1,  1,  1, 1, 17]
            houses = [[] for i in range(12)]
            for i in range(12):
                houses[i] = self.sort_house(chart, i, options)
                if i > 3 and i < 9: 
                    houses[i].reverse()
                for j in range(15):
                    if houses[i][j]: 
                        temp = houses[i][j]
                        if len(temp)>2:
                            planet = houses[i][j][0]
                            arr[y[i]+j][x[i]:x[i]+16] = display(chart, planet)
                            
            for row in arr: 
                chartfile.write(" ")
                for col in row:
                    chartfile.write(col)
                chartfile.write("\n")
            
            chartfile.write("\n\n" + "-" * 72 + "\n")
            chartfile.write("Pl Longitude   Lat   Speed    RA    Decl    Azi     Alt     PVL    Ang G\n") 
            ang = options.get("angularity", {})
            majlimit = ang.get("major_angles", [3.0, 7.0, 10.0])
            minlimit = ang.get("minor_angles", [1.0, 2.0, 3.0])
            plfg = []
            plang = {}
            dormant = True if "I" in self.cclass else False
            for i in range(3):
                if majlimit[i] == 0: majlimit[i] = -3
                if minlimit[i] == 0: minlimit[i] = -3 
            for pl in planet_names:
                if pl == "Eastpoint": break
                if pl == "Eris" and not options.get("use_Eris", 1): continue
                if pl == "Sedna" and not options.get("use_Sedna", 0): continue
                if pl == "True Node" and options.get("Node", 0) != 1: continue   
                if pl == "Mean Node" and options.get("Node", 0) != 2: continue
                pd = chart[pl]
                i = planet_names.index(pl)
                chartfile.write(left(planet_abrev[i], 3))
                chartfile.write(zod_sec(pd[0]) + " ")
                chartfile.write(fmt_lat(pd[1], True) + " ")
                if abs(pd[2]) >= 1:
                    chartfile.write(s_dm(pd[2])+ " ")
                else:
                    chartfile.write(s_ms(pd[2])+ " ")
                chartfile.write(right(fmt_dm(pd[3], True),7)+ " ")
                chartfile.write(fmt_lat(pd[4], True) + " ")
                chartfile.write(right(fmt_dm(pd[5], True),7) + " ")
                chartfile.write(s_dm(pd[6]) + " ")
                chartfile.write(right(fmt_dm(pd[7], True),7) + " ")
                a1 = pd[7] % 90
                if ang["model"] == 1:
                    p1 = main_angularity_curve_2(a1)
                else:
                    p1 = main_angularity_curve(a1)    
                a2 = abs(chart["cusps"][1] - pd[0])
                if a2 > 180: a2 = 360 - a2
                if inrange(a2, 90 , 3):
                    p2 = minor_angularity_curve(abs(a2 - 90))
                else:
                    p2 = -2
                a3 = abs(chart["cusps"][10] - pd[0]) 
                if a3 > 180: a3 = 360 - a3
                if inrange(a3, 90, 3):
                    p3 = minor_angularity_curve(abs(a3 - 90))
                else:
                    p3 = -2
                a4 = abs(chart["ramc"] - pd[3]) 
                if a4 > 180: a4 = 360 - a4
                if inrange(a4, 90, 3):
                    p4 = minor_angularity_curve(abs(a4 - 90))
                else:
                    p4 = - 2
                p = max(p1, p2, p3, p4)
                fb = " "
                fbx = " "
                a = 90 - a1 if a1 > 45 else a1
                if a <= majlimit[0]: 
                    fb = "F"
                    dormant = False
                elif a <= majlimit[1]: fb = "F"
                elif a <= majlimit[2]: fb = "F"
                if fb == " ":
                    if ang["model"] == 0:
                        if a1 >= 60: a = a1 - 60
                        else: a = (60 - a1) / 2
                    else: 
                        a = abs(a - 45)
                    if a <= majlimit[0]: fb = "B"
                    elif a <= majlimit[1]: fb = "B"
                    elif a <= majlimit[2]: fb = "B" 
                    if fb == "B" and ang.get("no_bg", False): 
                        fbx = "B"
                        fb = " "
                a = abs(a2 - 90)
                if a <= minlimit[0]: 
                    fb = "F"
                    dormant = False
                elif a <= minlimit[1]: 
                    fb = "F"
                    dormant = False
                elif a <= minlimit[2]: fb = "F"              
                a =  abs(a3 - 90)
                if a <= minlimit[0]: 
                    fb = "F"
                    dormant = False
                elif a <= minlimit[1]:
                    fb = "F"
                    dormant = False
                elif a <= minlimit[2]: fb = "F" 
                a = abs(a4 - 90)
                if a <= minlimit[0]: 
                    fb = "F"
                    dormant = False
                elif a <= minlimit[1]: 
                    fb = "F"
                    dormant = False
                elif a <= minlimit[2]: fb = "F"
                if fb == "F" or (pl == "Moon" and "I" in self.cclass): plfg.append(pl)
                px = round((p + 1) * 50)
                if fb == " ":
                    if fbx == " ":
                        plang[planet_abrev[i]] = " " 
                    else:
                        plang[planet_abrev[i]] =  fbx
                else:
                    plang[planet_abrev[i]] = fb
                if fb == "F":
                    if p == p1:
                        if pd[7] >= 345 or pd[7] <= 15: fb = "A "
                        if inrange(pd[7], 90, 15): fb = "I "
                        if inrange(pd[7], 180, 15): fb = "D "
                        if inrange(pd[7], 270, 15): fb = "M "
                    if p == p2:
                        a = chart["cusps"][1] - pd[0]
                        if a < 0: a += 360
                        if inrange(a, 90, 5): fb = "Z "
                        if inrange(a, 270, 5): fb ="N "
                    if p == p3:
                        a = chart["cusps"][10] - pd[0]
                        if a < 0: a += 360
                        if inrange(a, 90, 5): fb = "W "
                        if inrange(a, 270, 5): fb ="E "
                    if p == p4:
                        a = chart["ramc"] - pd[3]
                        if a < 0: a += 360
                        if inrange(a, 90, 5): fb = "Wa"
                        if inrange(a, 270, 5): fb ="Ea"
                if fb == "B": fb = " b"
                if fb == " ": fb = "  "
                chartfile.write(f"{px:3d}% {fb}")
                chartfile.write("\n")
            if dormant:
                chartfile.write("-" * 72 + "\n")
                chartfile.write(center("Dormant Ingress", 72) + "\n")
            ea = options.get("ecliptic_aspects", default_ea)
            ma = options.get("mundane_aspects", default_ma)
            asp = [[], [], [], []]
            asph = ["Class 1", "Class 2", "Class 3", "Other Partile"]
            for i in range(14):
                for j in range(i + 1, 14):
                    (easp, cle, orbe) = self.find_easpect(chart, i, j, ea, options, plfg, dormant)
                    (masp, clm, orbm) = self.find_maspect(chart, i, j, ma, options, plfg, dormant)
                    if easp and masp:
                        if orbm < orbe: easp = ""
                        else: masp = ""        
                    if easp: asp[cle - 1].append(easp)
                    if masp: asp[clm - 1].append(masp)
            if len(asp[3]) == 0 or dormant:
                del asp[3]
                del asph[3]
                asp.append([])
                asph.append("")    
            for i in range(2, -1, -1):
                if len(asp[i]) == 0:
                    del asp[i]
                    del asph[i]
                    asp.append([])
                    asph.append("")
            if any(asph):
                chartfile.write("-" * 72 + "\n")
                for i in range(0, 3):
                    chartfile.write(center(f"{asph[i]} Aspects" if asph[i] else "" , 24))
                chartfile.write( "\n")
            for i in range(max(len(asp[0]), len(asp[1]), len(asp[2]))):
                if i < len(asp[0]):
                    chartfile.write(left(asp[0][i], 24))
                else:
                    chartfile.write(" " * 24)
                if i < len(asp[1]):
                    chartfile.write(center(asp[1][i], 24))
                else:
                    chartfile.write(" " * 24)
                if i < len(asp[2]):
                    chartfile.write(right(asp[2][i], 24))
                else:
                    chartfile.write(" " * 24)
                chartfile.write("\n")
            chartfile.write("-" * 72 + "\n")
            if asp[3]:
                chartfile. write(center(f"{asph[3]} Aspects",72) + "\n")
                for a in asp[3]:
                    chartfile. write(center(a ,72) + "\n")
                chartfile.write("-" * 72 + "\n")
            chartfile.write(center("Cosmic State",72) + "\n")
            moonsi = sign_abrev[int(chart["Moon"][0]//30)]
            sunsi = sign_abrev[int(chart["Sun"][0]//30)]
            cclass = chart["class"]
            for i in range(14): 
                if i == 10 and not options.get("use_Eris", 1): continue
                if i == 11 and not options.get("use_Sedna", 0): continue
                if i == 12 and options.get("Node" , 0) != 1: continue 
                if i == 13 and options.get("Node", 0) != 2: continue
                pa = planet_abrev[i]
                pn = planet_names[i]
                pd = chart[pn]
                if pa != "Mo": chartfile.write("\n")
                chartfile.write(pa + " ")
                sign = sign_abrev[int(pd[0]//30)]
                if sign in pos_sign[pa]: x = "+"
                elif sign in neg_sign[pa]: x = "-"
                else: x = " "
                chartfile.write(f"{sign}{x} ")
                chartfile.write(plang.get(pa, "") + " |")
                cr = False
                if cclass != "I":
                    if pa != "Mo":
                        if moonsi in pos_sign[pa]:
                            chartfile.write(f" Mo {moonsi}+")
                            cr = True
                        elif moonsi in neg_sign[pa]:
                            chartfile.write(f" Mo {moonsi}-")
                            cr = True
                    if pa != "Su":
                        if sunsi in pos_sign[pa]:
                            chartfile.write(f" Su {sunsi}+")
                            cr = True
                        elif sunsi in neg_sign[pa]:
                            chartfile.write(f" Su {sunsi}-")
                            cr = True
                asplist = []
                for j in range(3):
                    for entry in asp[j]:
                        if pa in entry:
                            pct = str(200 -int(entry[15:18]))
                            entry = entry[0:15] + entry[20:]
                            if entry[0:2] == pa: 
                                entry = entry[3:] 
                            else: 
                                entry =  f"{entry[3:5]} {entry[0:2]}{entry[8:]}"
                            asplist.append([entry, pct])
                asplist.sort(key  = lambda p: p[1] + p[0][6:11])
                if asplist: 
                    if cr: 
                        chartfile.write("\n" + (" " * 9) + "| ")
                        cr = False
                    else: 
                        chartfile.write(" ")
                for j, a in enumerate(asplist):
                    chartfile.write(a[0] + "   ")
                    if j % 4 == 3 and j != len(asplist) - 1:
                        chartfile.write("\n"+ (" " * 9) + "| ")
                plist = []
                for j in range(14):
                    if j == i: continue
                    if j == 10 and not options.get("use_Eris", 1): continue
                    if j == 11 and not options.get("use_Sedna", 0): continue
                    if j == 12 and options.get("Node" , 0) != 1: continue 
                    if j == 13 and options.get("Node", 0) != 2: continue
                    plna = planet_names[j]
                    plong = chart[plna][0]
                    plab = planet_abrev[j] 
                    if options.get("show_aspects", 0) == 0 or plna in plfg:
                        plist.append([plab, plong])
                plist.append(["As", chart["cusps"][1]])
                plist.append(["Mc", chart["cusps"][10]])
                if len(plist) > 1 and (options.get("show_aspects", 0) == 0 or pn in plfg):
                    emp = []
                    for j in range(len(plist)-1):
                        for k in range(j+1, len(plist)):
                            mp = self.find_midpoint([pa, pd[0]], plist, j, k, options)
                            if mp: emp.append(mp)
                    if emp:
                        emp.sort(key = lambda p: p[6:8])
                        if cr or asplist: chartfile.write("\n" + (" " * 9) + "| ")
                        else: chartfile.write(" ")
                        for j, a in enumerate(emp):
                            chartfile.write("   " + a + "   ")
                            if j % 4 == 3 and j != len(emp) - 1:
                                chartfile.write("\n"+ (" " * 9) + "| ")  
            sign = sign_abrev[int(chart["cusps"][1]//30)]
            plist = []
            for i in range(14):
                if i == 10 and not options.get("use_Eris", 1): continue
                if i == 11 and not options.get("use_Sedna", 0): continue
                if i == 12 and options.get("Node" , 0) != 1: continue 
                if i == 13 and options.get("Node", 0) != 2: continue
                plna = planet_names[i]
                plong = chart[plna][0]
                plra = chart[plna][3]
                plpvl = chart[plna][7]
                plab = planet_abrev[i] 
                if options.get("show_aspects", 0) == 0 or plna in plfg:
                    plist.append([plab, plong, plra, plpvl])
            plist.append(["Mc", chart["cusps"][10]]) 
            if len(plist) > 1:
                emp = []
                for j in range(len(plist)-1):
                    for k in range(j+1, len(plist)):
                        mp = self.find_midpoint(["As", chart["cusps"][1]], plist, j, k, options)
                        if mp: emp.append(mp)
                if emp:
                    emp.sort(key = lambda p: p[6:8])
                    chartfile.write(f"\nAs {sign}    | ")
                    for j, a in enumerate(emp):
                        chartfile.write("   " + a + "   ")
                        if j % 4 == 3 and j != len(emp) - 1:
                            chartfile.write("\n"+ (" " * 9) + "| ")  
            sign = sign_abrev[int(chart["cusps"][10]//30)]
            plist[-1] = ["As", chart["cusps"][1]]
            if len(plist) > 1:
                emp = []
                for j in range(len(plist)-1):
                    for k in range(j+1, len(plist)):
                        mp = self.find_midpoint(["Mc", chart["cusps"][10]], plist, j, k, options)
                        if mp: emp.append(mp)
                if emp:
                    emp.sort(key = lambda p: p[6:8])
                    chartfile.write(f"\nMc {sign}    | ")
                    for j, a in enumerate(emp):
                        chartfile.write("   " + a + "   ")
                        if j % 4 == 3 and j != len(emp) - 1:
                            chartfile.write("\n"+ (" " * 9) + "| ") 
            del plist[-1]
            if len(plist) > 1:
                emp = []
                ep = ["Ep", (chart["cusps"][10] + 90) % 360,  (chart["ramc"] + 90) % 360]
                ze = ["Ze", (chart["cusps"][1] - 90) % 360]
                for j in range(len(plist)-1):
                    for k in range(j+1, len(plist)):
                        mp = self.mmp_all(ep, ze, plist, j, k, options)
                        if mp: emp.append(mp)
                if emp:
                    empa = []
                    empe = []
                    empz = []
                    for x in emp:
                        if x[-1] == "A": empa.append(x[:-1])
                        elif x[-1] == "E": empe.append(x[:-1])
                        else: empz.append(x[:-1])  
                    empa.sort(key = lambda p: p[6:8])
                    empe.sort(key = lambda p: p[6:8])
                    empz.sort(key = lambda p: p[6:8])
                    if empa:
                        chartfile.write(f"\nAngle    | ")
                        for j, a in enumerate(empa):
                            chartfile.write("   " + a + "   ")
                            if j % 4 == 3 and j != len(empa) - 1:
                                chartfile.write("\n"+ (" " * 9) + "| ") 
                    if empe:
                        chartfile.write(f"\nEp       | ")
                        for j, a in enumerate(empe):
                            chartfile.write("   " + a + "   ")
                            if j % 4 == 3 and j != len(empe) - 1:
                                chartfile.write("\n"+ (" " * 9) + "| ")  
                    if empz:
                        chartfile.write(f"\nZe       | ")
                        for j, a in enumerate(empz):
                            chartfile.write("   " + a + "   ")
                            if j % 4 == 3 and j != len(empz) - 1:
                                chartfile.write("\n"+ (" " * 9) + "| ")      
            chartfile.write("\n" + "-" * 72 + "\n")
            chartfile.write(f"Created by TMSA {VERSION}  ({datetime.now().strftime('%d %b %Y')})")
            self.filename = filename
        return
        
    def sort_house(self, chart, h, options):
        house = []
        for pl in planet_names:
            if pl == "Eris" and not options.get("use_Eris", 1): continue
            if pl == "Sedna" and not options.get("use_Sedna", 0): continue
            if pl == "Vertex" and not options.get("use_Vertex", 0): continue
            if pl == "True Node" and options.get("Node" , 0) != 1: continue   
            if pl == "Mean Node" and options.get("Node", 0) != 2: continue
            pd = chart[pl]
            if pd[-1] // 30 == h:
                pos = (pd[-1] % 30) / 2
                house.append([pl, pd[-1], pos])
        house.sort(key = lambda h: h[1])
        return self.spread(house)
        
    def spread(self, old, start = 0):
        new  = [[] for i in range(15)]
        placed = 0
        for i in range(len(old)):
            x = int(old[i][-1]) + start
            limit = 15 - len(old) + placed
            if x > limit: x = limit
            while True:
                if len(new[x]):
                    x += 1
                else:
                    break
            new[x] = old[i]
            placed += 1
        return new
        
    def find_easpect(self, chart, i, j, ea, options, plfg, dormant):
        pn1 = planet_names[i]
        pn2 = planet_names[j]
        if (pn1 == "Eris" or pn2 == "Eris") and not options.get("use_Eris", 1): return ("", 0, 0)
        if (pn1 == "Sedna" or pn2 == "Sedna") and not options.get("use_Sedna", 0): return ("", 0, 0)        
        if (pn1 == "True Node" or pn2 == "True Node") and options.get("Node", 0) != 1: return ("", 0, 0)   
        if (pn1 == "Mean Node" or pn2 == "Mean Node") and options.get("Node",0) != 2: return ("", 0, 0)
        pd1 = chart[planet_names[i]]
        pd2 = chart[planet_names[j]]
        pa1 = planet_abrev[i]
        pa2 = planet_abrev[j]
        astr = ["0","180","90", "45", "45", "120", "60", "30", "30"]
        anum = [0, 180, 90, 45, 135, 120, 60, 30, 150]
        aname = [ "co", "op", "sq", "oc", "oc", "tr", "sx", "in", "in"] 
        d = abs(pd1[0] - pd2[0]) % 360
        if d > 180: d = 360 - d 
        for i in range(9):
            aspd = ea[astr[i]]
            if aspd[2]: maxorb = aspd[2]
            elif aspd[1]: maxorb = aspd[1] * 1.25
            elif aspd[0]: maxorb = aspd[0] * 2.5
            else: maxorb = -1
            if d >= anum[i] - maxorb and d <= anum[i] + maxorb:
                asp = aname[i]
                if maxorb <= 0: return ("", 0, 0) 
                m = 60 / maxorb
                d = abs(d - anum[i])
                if d <= aspd[0]: acl = 1
                elif d <= aspd[1]: acl = 2
                elif d <= aspd[2]: acl = 3
                else: return ("", 0, 0)
                if pn1 == "Moon" and "I" in self.cclass: break
                if dormant: return ("", 0, 0)
                if options.get("show_aspects", 0) == 1:
                    if pn1 not in plfg and pn2 not in plfg: 
                        if d <= 1 and options.get("partile_nf", False): acl = 4
                        else: return ("", 0, 0)
                elif options.get("show_aspects", 0) == 2:
                    if pn1 not in plfg or pn2 not in plfg: 
                        if d <= 1 and options.get("partile_nf", False): acl = 4
                        else: return ("", 0, 0)
                break
        else: 
            return ("", 0, 0)
        p = math.cos(math.radians(d * m))
        p = round((p - .5) * 200)
        p = f"{p:3d}"
        return (f"{pa1} {asp} {pa2} {fmt_dm(abs(d), True)}{p}%  ", acl, d)
    
    def find_maspect(self, chart, i, j, ma, options, plfg, dormant):
        pn1 = planet_names[i]
        pn2 = planet_names[j]
        if (pn1 == "Eris" or pn2 == "Eris") and not options.get("use_Eris", 1): return ("", 0, 0)
        if (pn1 == "Sedna" or pn2 == "Sedna") and not options.get("use_Sedna", 0): return ("", 0, 0)        
        if (pn1 == "True Node" or pn2 == "True Node") and options.get("Node", 0) != 1: return ("", 0, 0)   
        if (pn1 == "Mean Node" or pn2 == "Mean Node") and options.get("Node", 0) != 2: return ("", 0, 0)
        pd1 = chart[planet_names[i]]
        pd2 = chart[planet_names[j]]
        pa1 = planet_abrev[i]
        pa2 = planet_abrev[j]
        d = abs(pd1[7] - pd2[7]) % 360
        if d > 180: d = 360 - d
        astr = ["0","180","90", "45", "45"]
        anum = [0, 180, 90, 45, 135]
        aname = [ "co", "op", "sq", "oc", "oc"]   
        for i in range(5):
            aspd = ma[astr[i]]
            if aspd[2]: maxorb = aspd[2]
            elif aspd[1]: maxorb = aspd[1] * 1.25
            elif aspd[0]: maxorb = aspd[0] * 2.5
            else: maxorb = -1
            if d >= anum[i] - maxorb and d <= anum[i] + maxorb:
                asp = aname[i]
                if maxorb <= 0: return ("", 0, 0) 
                m = 60 / maxorb
                d = abs(d - anum[i])
                if d <= aspd[0]: acl = 1
                elif d <= aspd[1]: acl = 2
                elif d <= aspd[2]: acl = 3
                else: return ("", 0, 0) 
                if pn1 == "Moon" and "I" in self.cclass: break
                if dormant: return ("", 0, 0)
                if options.get("show_aspects", 0) == 1:
                    if pn1 not in plfg and pn2 not in plfg: 
                        if d <= 1 and options.get("partile_nf", False): acl = 4
                        else: return ("", 0, 0)
                elif options.get("show_aspects", 0) == 2:
                    if pn1 not in plfg or pn2 not in plfg: 
                        if d <= 1 and options.get("partile_nf", False): acl = 4
                        else: return ("", 0, 0)
                break
        else:
            return ("", 0, 0)
        p = math.cos(math.radians(d * m))
        p = round((p - .5) * 200)
        p = f"{p:3d}" 
        return (f"{pa1} {asp} {pa2} {fmt_dm(abs(d), True)}{p}% M", acl, d) 
        
    def find_midpoint(self, planet, plist, i, j, options):
        mpx = options.get("midpoints", {})
        if planet[0] == "Ep": return self.mmp_eastpoint(planet, mmp, plist, i, j)  
        if planet[0] == "Ze": return self.mmp_zenith(planet, mmp, plist, i, j)
        p = planet[1]
        m = (plist[i][1] + plist[j][1]) / 2
        d = (p - m) % 360
        if d > 180: d = 360 - d
        mp0 = mpx.get("0", 0) / 60
        if mp0:
            if d <= mp0 or d > 180 - mp0:
                if d < 90:  z = d
                else: z = 180 - d
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'d"
        mp90 = mpx.get("90", 0) / 60
        if mp90:
            if d >= 90 - mp90 and d <= 90 + mp90:
                z = abs(d - 90)
                di = mpx.get("is90", "d")
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'{di}"
        mp45 = mpx.get("45", 0) / 60
        if mp45:
            if d >= 45 - mp45 and d <= 45 + mp45:
                z = abs(d - 45)
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'i"
            if d >= 135 - mp45 and d <= 135 + mp45:
                z = abs(d - 135)
                return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'i"    
        return ""
        
        
    def mmp_major(self, plist, i, j, mmp):
        m = (plist[i][3] + plist[j][3]) / 2
        m %= 90
        if m > mmp and m < 90 - mmp: return "" 
        z = 90 - m if m > 45 else m
        return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'MA" 
        
        
    def mmp_eastpoint(self, planet, plist, i, j, mmp):
        m = (plist[i][1] + plist[j][1]) / 2
        p = planet[1] 
        d = (p - m) % 360
        if d > 180: d = 360 - d
        if d <= mmp or d >= 180 - mmp:
            if d < 90:  z1 = d
            else: z1 = 180 - d
        else:
            z1 = 1000
        m = (plist[i][2] + plist[j][2]) / 2
        p = planet[2]
        d = (p - m) % 360
        if d > 180: d = 360 - d
        if d <= mmp or d >= 180 - mmp:
            if d < 90:  z2 = d
            else: z2 = 180 - d
        else:
            z2 = 1000
        z = min(z1, z2) 
        xl1 = (plist[i][1] - planet[1]) % 360
        xa1 = (plist[i][2] - planet[2]) % 360
        if xl1 > 180: xl1 = 360 - xl1
        if xa1 > 180: xa1 = 360 - xa1
        xl2 = (plist[j][1] - planet[1]) % 360
        xa2 = (plist[j][2] - planet[2]) % 360
        if xl2 > 180: xl2 = 360 - xl2
        if xa2 > 180: xa2 = 360 - xa2
        if not any([xl1<=3, xl1>=177, xa1<=3, xa1>=177, xl2<=3, xl2>=177, xa2<=3, xa2>=177]): return ""
        if z < 1000:
            return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'ME"
        return ""
        
            
    def mmp_zenith(self, planet, plist, i, j, mmp):
        p = planet[1]
        x = (plist[i][1] - p) % 360
        if x > 180: x = 360 -x
        if x > 3 and x < 177: return ""
        x = (plist[i][2] - p % 360)
        if x > 180: x = 360 -x
        if x > 3 and x < 177: return ""
        m = (plist[i][1] + plist[j][1]) / 2
        d = (p - m) % 360
        if d > 180: d = 360 - d
        if d <= mmp or d >= 180 - mmp:
            if d < 90:  z = d
            else: z = 180 - d
            return f"{plist[i][0]}/{plist[j][0]} {round(z * 60):2}'MZ"  
        return ""
        
    def mmp_all(self, ep, ze, plist, i, j, options): 
        mmp = options.get("midpoints", {}).get("M", 0) / 60
        if not mmp: return ""
        a = self.mmp_major(plist, i, j, mmp)
        e = self.mmp_eastpoint(ep, plist, i, j, mmp)
        z = self.mmp_zenith(ze, plist, i, j, mmp)
        ai = a[6:8] if a else "99"
        ei = e[6:8] if e else "99"
        zi = e[6:8] if z else "99"
        if ai <= ei:
            x = a
            xi = ai
        else: 
            x = e 
            xi = ei
        x = x if xi <= zi else z
        return x
        
    def show(self):
        os.startfile(self.filename)
