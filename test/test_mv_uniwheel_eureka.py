from test.fixtures.base_chart import base_chart
from test.fixtures.natal_options import natal_options
from test.mocks.mockfile import MockFile
from test.fixtures.tk_fixtures import mock_tk_main
from test.utils import assert_line_contains

class TestUniwheelDisplay:
    def test_chart_center_info(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')

        assert_line_contains(lines[22], base_chart['name'], any_position=True)
        assert_line_contains(lines[24], base_chart['type'], any_position=True)
        assert_line_contains(lines[26], '20 Dec 1989 22:20:00 EST', any_position=True)
        assert_line_contains(lines[28], base_chart['location'], any_position=True)
        assert_line_contains(lines[30], '40N58\'47"', any_position=True)
        assert_line_contains(lines[30], '74W 7\'10"', any_position=True)
        assert_line_contains(lines[32], 'UT  3:20:00 +1 day', any_position=True)
        assert_line_contains(lines[34], 'RAMC 65°33\'42"', any_position=True)
        assert_line_contains(lines[36], 'OE 23°26\'33"', any_position=True)
        assert_line_contains(lines[38], 'SVP  5Pi23\'48"', any_position=True)
        
    def test_moon(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[70].strip(), 'Mo 17Vi 8\'16"  4S 9 +11°54\' 189° 9\'  8S28  73°16\' -30°39\' 189°41\'  31°45\'  50%')
        
    def test_sun(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[71].strip(), 'Su  4Sg37\'53"  0S 0 + 1° 1\' 269°10\' 23S26 304°21\' -63°35\' 228°38\' 112°18\'  53%')
        
    def test_mercury(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[72].strip(), 'Me 24Sg22\'55"  1S49 + 1°11\' 290°50\' 23S54 280° 8\' -48°43\' 191°20\' 130°50\'  43%')
        
    def test_venus(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[73].strip(), 'Ve 10Cp30\'51"  0S32 +18\'25" 307°37\' 19S31 272°35\' -33°33\' 181°43\' 146°26\'   3% Vx')

    def test_mars(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[74].strip(), 'Ma  7Sc26\'18"  0N 5 +41\'49" 239°58\' 20S29  14°44\' -68°58\' 248°19\'  84°25\'  92% I')
        
    def test_jupiter(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[75].strip(), 'Ju 12Ge 4\'57"  0S 9 - 8\' 2"  97°16\' 23N 8 114° 8\' +58° 1\'  33°12\' 299°41\'  50%')


    def test_saturn(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[76].strip(), 'Sa 19Sg43\'19"  0N18 + 6\'57" 285°31\' 22S22 286°39\' -51°42\' 199°56\' 127° 7\'  48%')

            
    def test_uranus(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[77].strip(), 'Ur 10Sg29\'57"  0S16 + 3\'36" 275°34\' 23S37 295°26\' -59°30\' 216° 6\' 118° 0\'  50%')


    def test_neptune(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[78].strip(), 'Ne 17Sg 0\'25"  0N51 + 2\'14" 282°33\' 22S 5 289°53\' -53°39\' 204°48\' 124°41\'  49%')



    def test_pluto(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[79].strip(), 'Pl 22Li 9\' 4" 15N13 + 1\'55" 228°35\'  2S13  26° 2\' -48°19\' 225°16\'  68°39\'  19%  b')


    def test_eris(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[80].strip(), 'Er 21Pi39\'39" 17S30 - 0\' 9"  21°43\'  9S46 228°58\' +25°10\'  17° 9\' 211°56\'  50%')