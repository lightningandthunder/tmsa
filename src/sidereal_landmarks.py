# Copyright 2021-2024 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.


from init import *
from widgets import *

from constants import LABEL_X_COORD, LABEL_HEIGHT_UNIT, LABEL_WIDTH

# https://stackoverflow.com/questions/71677889/create-a-scrollbar-to-a-full-window-tkinter-in-python

header = 'Where Sidereal Astrologers Usually Agree'

intro = """To help articulate our common ground, we offer the 
following SIDEREAL ASTROLOGY LANDMARKS. No one has to agree with all points, 
of course, though we recommend that all site participants be aware of them as 
a foundation of commonly held views by most Sidereal astrologers. 
In the spirit of scientific inquiry, these points are subject to modification 
and open to collegial debate."""

defining_sidereal_astrology_header = 'Defining Sidereal Astrology'

defining_sidereal_astrology = """
1. Sidereal Astrology is the name of a school of astrological thought 
and practice founded by Cyril Fagan, Donald A. Bradley (“Garth Allen”), 
and their close collaborators. It has both commonalities and differences 
in methodology with modern Western Tropical astrology and is most 
distinguished by a different theory of the zodiac. 
It shares much of its zodiac theory with traditional and modern Indian 
astrology while differing dramatically in methodology.
"""

living_study = """
2. While we greatly respect Fagan and Bradley’s original work as foundational 
source literature, Sidereal Astrology is a living, growing study, 
influenced as much by its founders’ commitment to uncovering truth as to their 
actual discoveries and teachings. We affirm our commitment to their standards of 
competent, honest inquiry and investigation.
"""

the_sidereal_zodiac = 'The Sidereal Zodiac'

astrology_began = """
3. Astrology began from visual observation of the heavens. 
Fixed stars were the basis of the zodiac’s original frame of reference 
and continue to reflect its essential framework."""

classical_fixed_zodiac = """
4. The Sidereal zodiac is the classical fixed zodiac of constellations 
originally found in all ancient cultures where a zodiac has been found. 
It is both an ancient recovery and a modern discovery: 
Archaeological research into astrology’s origins and statistical research 
into astrology’s behavior independently disclosed the same boundaries for 
the zodiacal signs."""

twelve_constellations = """
5. Now as in antiquity, the zodiac consists of twelve constellations, 
each exactly 30° wide. Although astronomers have remapped ancient 
constellation boundaries for their own purposes, their modern definitions 
are not (and have never been) astrology’s definitions. (The two models 
overlap more than they differ.)"""

the_vernal_point_header = 'The Vernal Point'

the_vernal_point = """
6. The northern hemisphere's vernal equinoctial point (“vernal point” or “VP”) 
retrogrades (precesses) along the zodiac 0°00'50" per year (1° in about 72 years). 
Tropical astrologers consider the VP fundamental to defining the zodiac; 
Sidereal Astrology does not."""

fixed_reference_system = """

7. The Sidereal zodiac, having no reliance on the moving vernal point, 
is a fixed reference system unmoved by precession. The Tropical zodiac, 
relying on the vernal point for its definition, is a moving reference system 
that must be constantly adjusted for precession."""

increasing_ayanamsa = """
8. Whereas the Tropical zodiac defines the VP as 0° Aries for all time, 
Sidereal Astrology recognizes that it continuously moves and currently 
(2024) is at 5° Pisces. Thus, boundaries of the two zodiac models presently 
differ by 25°. This slowly increasing divergence is known by the 
Sanskrit term ayanamsa."""

synetic_vernal_point = """
9. Sidereal Astrology defines the mean longitude of the vernal point as 
Pisces 5°57'28".64 for the epoch 1950.0. This definition is called the 
Synetic Vernal Point (SVP) or, colloquially, the 
"Fagan-Allen (or Fagan-Bradley) ayanamsa."""

personal_and_mundane_astrology_header = 'Personal and Mundane Astrology'

personal_astrology = """
10. Personal astrology (astrology of an individual) requires an astrological 
chart for the moment and place of the person's birth. Complete, correct 
birth data (date, time, and place of birth) are paramount for thorough, 
reliable evaluation. Absence of complete birth data limits the 
reliability and range of astrological analysis.
"""

solunar_returns = """
11. Sidereal solar and lunar returns were important predictive tools of 
ancient astrologers. Modern Sidereal astrologers (who term them, collectively, 
Solunars) regard them as among the most important astrological 
prediction instruments."""

mundane_astrology = """
12. Mundane astrology (astrology of the collective) relies on many techniques, 
foremost of which are maps for the ingresses of Sun or Moon into Capricorn, 
Aries, Cancer, and Libra. Calculation of these maps relies on knowing 
exactly where 0°00'00" of the signs falls. The high accuracy and 
reliability of these maps for portraying mass events (historically and predictively) 
continue to confirm the SVP definition of the Sidereal zodiac."""

angles_header = 'Angles'

angles = """
13. Angles of an astrological chart (primarily meaning the horizon and meridian) 
and planets proximate to these angles are primary analytic considerations 
in all areas of Sidereal Astrology."""

planets_header = 'Planets'

planets = """
14. The intrinsic natures of the planets are invariable. 
So-called "accidental dignities" do not alter them. 
Traditional characterization of some planets as benefic or malefic, 
while crude, correctly portrays the most common expressions of these planets."""

natal_planets = """
15. Natal planets reflect an individual's inherent nature, needs, and potential. 
Progressed planets reflect developments in that inherent nature."""

transiting_planets = """
16. Transiting planets most often are experienced as reflecting external 
circumstances interacting (causatively or responsively) with the personal 
actions or conditions reflected by aspected natal planets."""

aspects_header = 'Aspects'

angular_separation = """
17. The type of aspect between two planets (the angular separation) 
does not reflect a positive/negative or fortune/misfortune outcome, 
which, instead, arises from the planets involved, life conditions, 
and personal choices."""

aspect_types = """
18. Conjunctions, oppositions, and squares indicate dynamic action, incentive, 
and movement. Trines and sextiles are placid, quiet, and still."""

strength_and_expressiveness = """
19. Aspect strength depends on orb. The pressure toward outward expression 
of an aspect depends on planet angularity."""

planetary_dignities_header = 'Planetary Dignities'

planetary_dignities = """
20. Planets and the constellations they rule or in which they are exalted 
share common traits. However, we give no importance to so-called house 
rulers or dispositors."""

astrology_is_astrology = 'Astrology is Astrology'

holistic_astrology = """
21. Neither Fagan nor Bradley set out to found a variant branch of astrology but, 
rather, to discover what is true in astrology as a whole. 
Their work forms a distinct school of thought and practice, collegial within a 
broader field that does not currently embrace many of the above points."""

facts_of_nature = """
22. Yet, astrology is astrology. Facts of nature exist independent of our opinions 
about them. If (as we believe strong evidence shows) the zodiac is actual and 
long misconceived as being tropical, we anticipate an era when astrologers 
collectively recognize astrology’s inherently sidereal nature. At that point, 
the “sidereal” adjective will be redundant. Astrologers, united around 
astrology’s original and still authentic zodiac, will tackle other, newer 
controversies together."""


class NewChart(Frame):
    def __init__(self):
        super().__init__()

        self.intro = Label(
            self,
            intro,
            LABEL_X_COORD,
            0.125,
            LABEL_WIDTH,
            LABEL_HEIGHT_UNIT * 3,
            font=base_font,
        )
