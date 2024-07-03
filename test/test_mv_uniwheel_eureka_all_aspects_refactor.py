from src.models.charts import (
    AspectFramework,
    AspectType,
    ChartObject,
    ChartWheelRole,
)
from test.fixtures.base_chart import base_chart
from test.fixtures.natal_options import natal_options
import src.models.options as model_option
from test.mocks.mockfile import MockFile
from test.fixtures.tk_fixtures import mock_tk_main
from test.utils import (
    FixtureAspect,
    assert_aspect,
    assert_line_contains,
    assert_aspects_of_class,
)


class TestUniwheelDisplay:
    def init_test(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.core_chart import ChartReport

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        chart = ChartObject(base_chart).with_role(ChartWheelRole.RADIX)
        options = model_option.Options(natal_options)

        ChartReport(
            charts=[chart],
            temporary=False,
            options=options,
        )

        lines = mockfile.file.split('\n')

        return lines

    def test_chart_center_info(
        self, monkeypatch, base_chart, natal_options, mock_tk_main
    ):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(lines[22], base_chart['name'], any_position=True)
        assert_line_contains(lines[24], base_chart['type'], any_position=True)
        assert_line_contains(
            lines[26], '20 Dec 1989 22:20:00 EST', any_position=True
        )
        assert_line_contains(
            lines[28], base_chart['location'], any_position=True
        )
        assert_line_contains(lines[30], '40N58\'47"', any_position=True)
        assert_line_contains(lines[30], '74W 7\'10"', any_position=True)
        assert_line_contains(
            lines[32], 'UT  3:20:00 +1 day', any_position=True
        )
        assert_line_contains(lines[34], 'RAMC 65°33\'42"', any_position=True)
        assert_line_contains(lines[36], 'OE 23°26\'33"', any_position=True)
        assert_line_contains(lines[38], 'SVP  5Pi23\'48"', any_position=True)

    def test_moon(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[70].strip(),
            "Mo 17Vi 8'16\"  4S 9 +11°54' 189° 9'  8S28  73°16' -30°39' 189°41'  31°45'  50%",
        )

    def test_sun(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')

        assert_line_contains(
            lines[71].strip(),
            "Su  4Sg37'53\"  0S 0 + 1° 1' 269°10' 23S26 304°21' -63°35' 228°38' 112°18'  53%",
        )

    def test_mercury(
        self, monkeypatch, base_chart, natal_options, mock_tk_main
    ):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[72].strip(),
            "Me 24Sg22'55\"  1S49 + 1°11' 290°50' 23S54 280° 8' -48°43' 191°20' 130°50'  43%",
        )

    def test_venus(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[73].strip(),
            "Ve 10Cp30'51\"  0S32 +18'25\" 307°37' 19S31 272°35' -33°33' 181°43' 146°26'   3% Vx",
        )

    def test_mars(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[74].strip(),
            "Ma  7Sc26'18\"  0N 5 +41'49\" 239°58' 20S29  14°44' -68°58' 248°19'  84°25'  92% I",
        )

    def test_jupiter(
        self, monkeypatch, base_chart, natal_options, mock_tk_main
    ):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[75].strip(),
            "Ju 12Ge 4'57\"  0S 9 - 8' 2\"  97°16' 23N 8 114° 8' +58° 1'  33°12' 299°41'  50%",
        )

    def test_saturn(
        self, monkeypatch, base_chart, natal_options, mock_tk_main
    ):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[76].strip(),
            "Sa 19Sg43'19\"  0N18 + 6'57\" 285°31' 22S22 286°39' -51°42' 199°56' 127° 7'  48%",
        )

    def test_uranus(
        self, monkeypatch, base_chart, natal_options, mock_tk_main
    ):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[77].strip(),
            "Ur 10Sg29'57\"  0S16 + 3'36\" 275°34' 23S37 295°26' -59°30' 216° 6' 118° 0'  50%",
        )

    def test_neptune(
        self, monkeypatch, base_chart, natal_options, mock_tk_main
    ):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[78].strip(),
            "Ne 17Sg 0'25\"  0N51 + 2'14\" 282°33' 22S 5 289°53' -53°39' 204°48' 124°41'  49%",
        )

    def test_pluto(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[79].strip(),
            "Pl 22Li 9' 4\" 15N13 + 1'55\" 228°35'  2S13  26° 2' -48°19' 225°16'  68°39'  19%  b",
        )

    def test_eris(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        assert_line_contains(
            lines[80].strip(),
            "Er 21Pi39'39\" 17S30 - 0' 9\"  21°43'  9S46 228°58' +25°10'  17° 9' 211°56'  50%",
        )

    def test_aspects_class_1(
        self, monkeypatch, base_chart, natal_options, mock_tk_main
    ):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )
        for index, line in enumerate(lines):
            print(index, line)
        lines = lines[83:96]

        aspects = [
            FixtureAspect(
                'Mo',
                'Ju',
                AspectType.SQUARE,
                2,
                4,
                92,
                AspectFramework.MUNDANE,
            ),
            FixtureAspect('Mo', 'Sa', AspectType.SQUARE, 2, 35, 87),
            FixtureAspect('Mo', 'Ne', AspectType.SQUARE, 0, 8, 100),
            FixtureAspect(
                'Mo',
                'Er',
                AspectType.OPPOSITION,
                0,
                11,
                100,
                AspectFramework.MUNDANE,
            ),
            FixtureAspect('Me', 'Pl', AspectType.SEXTILE, 2, 14, 90),
            FixtureAspect('Me', 'Er', AspectType.SQUARE, 2, 43, 86),
            FixtureAspect('Ma', 'Er', AspectType.OCTILE, 0, 47, 89),
            FixtureAspect('Ju', 'Ur', AspectType.OPPOSITION, 1, 35, 97),
            FixtureAspect(
                'Ju',
                'Er',
                AspectType.SQUARE,
                2,
                15,
                90,
                AspectFramework.MUNDANE,
            ),
            FixtureAspect(
                'Sa',
                'Ne',
                AspectType.CONJUNCTION,
                2,
                26,
                89,
                AspectFramework.MUNDANE,
            ),
            FixtureAspect('Sa', 'Pl', AspectType.SEXTILE, 2, 26, 89),
            FixtureAspect('Sa', 'Er', AspectType.SQUARE, 1, 56, 93),
            FixtureAspect(
                'Ne',
                'Er',
                AspectType.SQUARE,
                2,
                46,
                85,
                AspectFramework.MUNDANE,
            ),
        ]

        assert_aspects_of_class(lines, 1, aspects)

    def test_aspects_class_2(
        self, monkeypatch, base_chart, natal_options, mock_tk_main
    ):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )

        lines = lines[83:90]

        aspects = [
            FixtureAspect('Su', 'Ur', AspectType.CONJUNCTION, 5, 52, 63),
            FixtureAspect('Me', 'Ma', AspectType.OCTILE, 1, 57, 37),
            FixtureAspect('Me', 'Sa', AspectType.CONJUNCTION, 4, 40, 77),
            FixtureAspect('Ve', 'Ma', AspectType.SEXTILE, 3, 5, 82),
            FixtureAspect('Ju', 'Ne', AspectType.OPPOSITION, 4, 55, 74),
            FixtureAspect('Ur', 'Ne', AspectType.CONJUNCTION, 6, 30, 55),
            FixtureAspect('Ne', 'Pl', AspectType.SEXTILE, 5, 9, 51),
        ]

        assert_aspects_of_class(lines, 2, aspects)

    def test_aspects_class_3(
        self, monkeypatch, base_chart, natal_options, mock_tk_main
    ):
        lines = self.init_test(
            monkeypatch, base_chart, natal_options, mock_tk_main
        )
        lines = lines[83:90]

        aspects = [
            FixtureAspect('Mo', 'Me', AspectType.SQUARE, 7, 15, 6),
            FixtureAspect('Mo', 'Ve', AspectType.TRINE, 6, 37, 20),
            FixtureAspect('Mo', 'Ur', AspectType.SQUARE, 6, 38, 20),
            FixtureAspect('Su', 'Ju', AspectType.OPPOSITION, 7, 27, 42),
            FixtureAspect('Me', 'Ne', AspectType.CONJUNCTION, 7, 22, 43),
            FixtureAspect('Ju', 'Sa', AspectType.OPPOSITION, 7, 38, 39),
            FixtureAspect('Sa', 'Ur', AspectType.CONJUNCTION, 9, 13, 14),
        ]

        assert_aspects_of_class(lines, 3, aspects)
