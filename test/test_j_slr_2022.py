from test.fixtures.j_slr import j_slr
from test.mocks.mockfile import MockFile
from test.fixtures.tk_fixtures import mock_tk_main
from test.utils import assert_line_contains
from test.fixtures.return_options import return_options


class TestBiwheelDisplay:
    def test_chart_center_info(
        self, monkeypatch, j_slr, return_options, mock_tk_main
    ):
        from src.user_interfaces.biwheelV2 import BiwheelV2

        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        BiwheelV2(chart=j_slr, temporary=True, options=return_options)

        lines = mockfile.file.split('\n')
        for idx, line in enumerate(lines):
            print(f'{idx}: {line}')

        assert_line_contains(
            lines[20], 'Transiting (t) Chart', any_position=True
        )
        assert_line_contains(lines[21], j_slr['name'], any_position=True)
        assert_line_contains(lines[22], j_slr['type'], any_position=True)
        assert_line_contains(
            lines[23], '7 Jan 2022 15:38:31 UT', any_position=True
        )
        assert_line_contains(lines[24], j_slr['location'], any_position=True)
        assert_line_contains(lines[25], '34N 3\'46"', any_position=True)
        assert_line_contains(lines[25], '118W18\'47"', any_position=True)

        assert_line_contains(lines[27], 'RAMC 223°30\' 1"', any_position=True)
        assert_line_contains(lines[28], 'OE 23°26\'15"', any_position=True)
        assert_line_contains(lines[29], 'SVP  4Pi57\'21"', any_position=True)

        assert_line_contains(lines[34], 'Radical (r) Chart', any_position=True)
        assert_line_contains(
            lines[35], j_slr['base_chart']['name'], any_position=True
        )
        assert_line_contains(
            lines[36], j_slr['base_chart']['type'], any_position=True
        )
        assert_line_contains(
            lines[37], '10 Oct 1954  4:13:00 UT', any_position=True
        )
        assert_line_contains(
            lines[38], j_slr['base_chart']['location'], any_position=True
        )
        assert_line_contains(
            lines[39], '41N 3\'54"  86W12\'58"', any_position=True
        )
        assert_line_contains(
            lines[40], 'UT 10:13:00', any_position=True
        )
        assert_line_contains(lines[41], 'RAMC 85°31\' 0"', any_position=True)
        assert_line_contains(lines[42], 'OE 23°26\'45"', any_position=True)
        assert_line_contains(lines[43], 'SVP  5Pi53\'13"', any_position=True)
