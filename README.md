# Time Matters Sidereal Astrology
### Introduction
TMSA is a desktop application originally developed by Mike Nelson in conjunction with the folks at [solunars.com](https://solunars.com).

After contact with him was lost and not re-established over some 6 months, at his wishes, the management of Solunars took ownership
over TMSA to ensure its continued development. At this point, I (Mike Verducci) volunteered to lead development on the project going forward.

Unfortunately, much code that Mike N had written but not distributed was lost once he became unreachable.
Aside from this, all we have are the prior releases of his source code and commentary on Solunars to base future development on.

### Status
Please see the [Trello board](https://trello.com/b/NpRZTYxh/tmsa-roadmap) to see the current state of development.

### Installation for users
More info forthcoming.

### Installation for developers
More info forthcoming.

### How to build this application
##### For 32-bit Windows:
```shell
conda create -n whatever
conda activate whatever
conda config --env --set subdir win-32
conda install python=3.10  # newest version that Conda can find
pip install -r .\\etc\\requirements.txt

pyinstaller --add-binary C:\sweph\dll\swedll32.dll:. src\tmsa.py
```

### Contributing
More info forthcoming.