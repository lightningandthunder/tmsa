# Copyright 2025 James Eshelman, Mike Nelson, Mike Verducci

# This file is part of Time Matters: A Sidereal Astrology Toolkit (TMSA).
# TMSA is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# TMSA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with TMSA. If not, see <https://www.gnu.org/licenses/>.

from src.user_interfaces.widgets import *

# https://stackoverflow.com/questions/71677889/create-a-scrollbar-to-a-full-window-tkinter-in-python


def add_markdown_text(container):
    def add_header(text, size=24, pady=(20, 5)):
        header_font = tk.font.Font(
            family='Lucida Console', size=size, weight='bold'
        )
        label = tk.Label(
            container,
            text=text,
            font=header_font,
            anchor='w',
            bg=BG_COLOR,
            fg=TXT_COLOR,
        )
        label.pack(fill='x', padx=10, pady=pady)

    def add_paragraph(content_parts, height=10):
        text = tk.Text(
            container,
            wrap='word',
            height=height,
            borderwidth=0,
            highlightthickness=0,
            bg=BG_COLOR,
            fg=TXT_COLOR,
            font=font_14,
            insertbackground=TXT_COLOR,
        )
        text.configure(state='normal')

        text.tag_configure(
            'italic',
            font=tk.font.Font(
                family='Lucida Console', size=14, slant='italic'
            ),
        )
        text.tag_configure(
            'underline',
            font=tk.font.Font(
                family='Lucida Console', size=14, underline=True
            ),
        )
        text.tag_configure(
            'bold',
            font=tk.font.Font(family='Lucida Console', size=14, weight='bold'),
        )

        for parts in content_parts:
            if len(parts) == 2:
                text.insert('end', parts[0], parts[1])
            else:
                text.insert('end', parts, ())

        text.configure(state='disabled')
        text.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    add_header('SIDEREAL ASTROLOGY LANDMARKS', size=32)
    add_paragraph(
        [
            (
                'A summary of common ground on which most Sidereal astrologers agree, updated from the 1975 "Points of Agreement" of the Registry of Sidereal Astrologers (ROSA).'
            ),
        ],
        height=3,
    )

    add_header('Defining Sidereal Astrology')
    add_paragraph(
        [
            ('1. '),
            ('Sidereal Astrology ', ('bold')),
            (
                'is the name of a school of astrological thought and practice founded by Cyril Fagan, Donald A. Bradley (“Garth Allen”), and their close collaborators. It has both commonalities and differences in methodology with modern Western Tropical astrology and is most distinguished by a different theory of the zodiac. It shares much of its zodiac theory with traditional and modern Indian astrology while differing dramatically in methodology.'
            ),
        ],
        height=6,
    )
    add_paragraph(
        [
            (
                '2. While we greatly respect Fagan and Bradley’s original work as foundational source literature, Sidereal Astrology is a living, growing study, influenced as much by its founders’ commitment to uncovering truth as to their actual discoveries and teachings. We affirm our commitment to their standards of competent, honest inquiry and investigation.'
            ),
        ],
        height=5,
    )

    add_header('The Sidereal Zodiac')
    add_paragraph(
        [
            (
                '3. Astrology began from visual observation of the heavens. Fixed stars were the basis of the zodiac’s original frame of reference and continue to reflect its essential framework.'
            ),
        ],
        height=3,
    )
    add_paragraph(
        [
            ('4. The Sidereal zodiac is the classical '),
            ('fixed ', ('bold')),
            (
                'zodiac of constellations originally found in all ancient cultures where a zodiac has been found. It is both an '
            ),
            ('ancient recovery ', ('bold')),
            ('and a '),
            ('modern discovery'),
            (
                ': Archaeological research into astrology’s origins and statistical research into astrology’s behavior '
            ),
            ('independently ', ('bold')),
            ('disclosed the same boundaries for the zodiacal signs.'),
        ],
        height=5,
    )
    add_paragraph(
        [
            (
                '5. Now as in antiquity, the zodiac consists of twelve constellations, each exactly 30° wide. Although astronomers have remapped ancient constellation boundaries for their own purposes, their modern definitions are not (and have never been) astrology’s definitions. (The two models overlap more than they differ.)'
            ),
        ],
        height=5,
    )

    add_header('The Vernal Point')
    add_paragraph(
        [
            (
                "6. The northern hemisphere's vernal equinoctial point (“vernal point” or “VP”) retrogrades (precesses) along the zodiac 0°00'50\" per year (1° in about 72 years). Tropical astrologers consider the VP fundamental to defining the zodiac; Sidereal Astrology does not."
            ),
        ],
        height=4,
    )
    add_paragraph(
        [
            ('7. The Sidereal zodiac, having no reliance on the '),
            ('moving ', ('bold')),
            ('vernal point, is a '),
            ('fixed ', ('bold')),
            (
                'reference system unmoved by precession. The Tropical zodiac, relying on the vernal point for its definition, is a moving reference system that must be constantly adjusted for precession.'
            ),
        ],
        height=4,
    )
    add_paragraph(
        [
            (
                '8. Whereas the Tropical zodiac defines the VP as 0° Aries for all time, Sidereal Astrology recognizes that it continuously moves and currently (2024) is at 5° Pisces. Thus, boundaries of the two zodiac models presently differ by 25°. This '
            ),
            ('slowly increasing divergence ', ('bold')),
            ('is known by the Sanskrit term '),
            ('ayanamsa.', ('italic')),
        ],
        height=4,
    )
    add_paragraph(
        [
            (
                '9. Sidereal Astrology defines the mean longitude of the vernal point as Pisces 5°57\'28".64 for the epoch 1950.0. This definition is called the '
            ),
            ('Synetic Vernal Point (SVP) ', ('bold')),
            ('or, colloquially, the "Fagan-Allen (or Fagan-Bradley) '),
            ('ayanamsa', ('italic')),
            ('.'),
            ('"'),
        ],
        height=3,
    )

    add_header('Personal and Mundane Astrology')
    add_paragraph(
        [
            (
                "10. Personal astrology (astrology of an individual) requires an astrological chart for the moment and place of the person's birth. Complete, correct birth data (date, time, and place of birth) are paramount for thorough, reliable evaluation. Absence of complete birth data limits the reliability and range of astrological analysis."
            )
        ],
        height=5,
    )
    add_paragraph(
        [
            (
                '11. Sidereal solar and lunar returns were important predictive tools of ancient astrologers. Modern Sidereal astrologers (who term them, collectively, '
            ),
            ('Solunars', ('bold')),
            (
                ') regard them as among the most important astrological prediction instruments.'
            ),
        ],
        height=4,
    )
    add_paragraph(
        [
            (
                '12. Mundane astrology (astrology of the collective) relies on many techniques, foremost of which are maps for the ingresses of Sun or Moon into Capricorn, Aries, Cancer, and Libra. Calculation of these maps relies on knowing exactly where 0°00\'00" of the signs falls. The high accuracy and reliability of these maps for portraying mass events (historically and predictively) continue to confirm the SVP definition of the Sidereal zodiac.'
            )
        ],
        height=6,
    )

    add_header('Angles')
    add_paragraph(
        [
            ('13. Angles of an astrological chart (primarily meaning the '),
            ('horizon', ('bold')),
            (' and '),
            ('meridian ', ('bold')),
            (
                'and planets proximate to these angles are primary analytic considerations in all areas of Sidereal Astrology.'
            ),
        ],
        height=3,
    )

    add_header('Planets')
    add_paragraph(
        [
            (
                '14. The intrinsic natures of the planets are invariable. So-called "accidental dignities" do not alter them. Traditional characterization of some planets as '
            ),
            ('benefic', ('bold')),
            (' or '),
            ('malefic', ('bold')),
            (
                ', while crude, correctly portrays the most common expressions of these planets.'
            ),
        ],
        height=4,
    )
    add_paragraph(
        [
            ('15. '),
            ('Natal planets', ('bold')),
            (
                " reflect an individual's inherent nature, needs, and potential. "
            ),
            ('Progressed planets', ('bold')),
            (' reflect developments in that inherent nature.'),
        ],
        height=2,
    )
    add_paragraph(
        [
            ('16. '),
            ('Transiting planets', ('bold')),
            (
                ' most often are experienced as reflecting external circumstances interacting (causatively or responsively) with the personal actions or conditions reflected by aspected natal planets.'
            ),
        ],
        height=3,
    )

    add_header('Aspects')
    add_paragraph(
        [
            ('17. The '),
            ('type', ('bold')),
            (
                ' of aspect between two planets (the angular separation) does not reflect a positive/negative or fortune/misfortune outcome, which, instead, arises from the planets involved, life conditions, and personal choices.'
            ),
        ],
        height=3,
    )
    add_paragraph(
        [
            ('18. '),
            ('Conjunctions, oppositions, and squares', ('bold')),
            (' indicate dynamic action, incentive, and movement. '),
            ('Trines and sextiles', ('bold')),
            (' are placid, quiet, and still.'),
        ],
        height=2,
    )
    add_paragraph(
        [
            ('19. Aspect '),
            ('strength', ('bold')),
            (' depends on orb. The '),
            ('pressure toward outward expression', ('bold')),
            (' of an aspect depends on planet angularity.'),
        ],
        height=2,
    )

    add_header('Planetary Dignities')
    add_paragraph(
        [
            ('20. Planets and the constellations they '),
            ('rule', ('bold')),
            (' or in which they are '),
            ('exalted'),
            (
                ' share common traits. However, we give no importance to so-called house rulers or dispositors.'
            ),
        ],
        height=3,
    )

    add_header('Astrology is Astrology')
    add_paragraph(
        [
            (
                '21. Neither Fagan nor Bradley set out to found a variant branch of astrology but, rather, to discover what is true in astrology as a whole. Their work forms a distinct school of thought and practice, collegial within a broader field that does not currently embrace many of the above points.'
            ),
        ],
        height=4,
    )
    add_paragraph(
        [
            ('22. Yet, '),
            ('astrology is astrology.', ('bold')),
            (
                ' Facts of nature exist independent of our opinions about them. If (as we believe strong evidence shows) '
            ),
            ('the zodiac is actual', ('bold')),
            (
                ' and long misconceived as being tropical, we anticipate an era when astrologers collectively recognize '
            ),
            ('astrology’s inherently sidereal nature.', ('bold')),
            (
                ' At that point, the “sidereal” adjective will be redundant. Astrologers, united around astrology’s original and still authentic zodiac, will tackle other, newer controversies together.'
            ),
        ],
        height=7,
    )


def make_scrollable_container(root):
    canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient='vertical', command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

    # This frame is placed inside the canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

    # Scroll region will resize when frame size changes
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    scrollable_frame.bind('<Configure>', on_configure)

    # Mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    canvas.bind_all('<MouseWheel>', _on_mousewheel)  # Windows/macOS
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side='left', fill='both', expand=True, padx=50)
    scrollbar.pack(side='right', fill='y')

    return scrollable_frame


class SiderealLandmarks(Frame):
    def __init__(self):
        super().__init__()

        outer_frame = tk.Frame(self, bg=BG_COLOR)
        outer_frame.pack(fill='both', expand=True)

        back_button = Button(
            outer_frame,
            text='Back',
            x=0.85,
            y=0.95,
            width=0.1,
        )
        back_button.bind('<Button-1>', lambda _: delay(self.destroy))
        scrollable_area = tk.Frame(outer_frame, bg=BG_COLOR)
        scrollable_area.pack(side='top', fill='both', expand=True)

        inner_frame = make_scrollable_container(scrollable_area)
        add_markdown_text(inner_frame)

        back_button.lift()
