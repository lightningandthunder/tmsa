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

        assert_line_contains(lines[22], base_chart['name'])
        assert_line_contains(lines[24], base_chart['type'])
        assert_line_contains(lines[26], '20 Dec 1989 22:20:00 EST')
        assert_line_contains(lines[28], base_chart['location'])
        assert_line_contains(lines[30], '40N58\'47"')
        assert_line_contains(lines[30], '74W 7\'10"')
        assert_line_contains(lines[32], 'UT  3:20:00 +1 day')
        assert_line_contains(lines[34], 'RAMC 65°33\'42"')
        assert_line_contains(lines[36], 'OE 23°26\'33"')
        assert_line_contains(lines[38], 'SVP  5Pi23\'48"')
        
    def test_mars_angular(self, monkeypatch, base_chart, natal_options, mock_tk_main):
        from src.user_interfaces.uniwheelV2 import UniwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        UniwheelV2(chart=base_chart, temporary=False, options=natal_options)

        lines = mockfile.file.split('\n')
        
        assert_line_contains(lines[74], ' I ', starts_at=78)

        for index, line in enumerate(lines):
            print(f'{index: <3}: {line}')
