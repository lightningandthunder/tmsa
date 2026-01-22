from test.fixtures.tk_fixtures import mock_tk_main
from test.mocks.mockfile import MockFile


class TestMidpoints:
    def test_anything(self, monkeypatch, mock_tk_main):
        mockfile = MockFile()
        monkeypatch.setattr('builtins.open', lambda _, __: mockfile)

        # In natal: list all ecliptic contacts to angles and planets.
        # In natal: Ecliptic On: Any ecliptic contact to Asc/MC counts.
        # In natal: List all mundane contacts to major angles.

        # Assume 2 planets are straddling ascendant...
        # Ecliptic On / Direct: list as Asc.
        # Ecliptic On / Indirect: list as Asc.
        # Ecliptic No / Direct: list as Zenith.
        #   (i.e. include even if ecliptic is off)
        # Ecliptic No / Indirect: Not listed.

        # Ingress PVL, at least one planet angular in PVL: counts.
        # Ingress PVL, neither planet angular in PVL: doesn't count.
        # Ingress RA, both planets angular in RA: counts.
        # Ingress RA, one planet angular in RA: doesn't count.
        # In ingress: Both foreground on Z/N: ecliptic contact counts.
        # In ingress: Planets not foreground: doesn't count.

        # In ingress: ecliptic planet=planet/planet:
        #   if planet is foreground somehow, counts.
        #   if planet is not foreground somehow, doesn't count.
