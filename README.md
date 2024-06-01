# Time Matters
### Introduction
Time Matters (TM) is a desktop application formerly known as Time Matters Sidereal Astrology (TMSA).
It was originally developed by Mike Nelson in conjunction with the folks at [solunars.com](https://solunars.com).

### Status
Please see the [Trello board](https://trello.com/b/NpRZTYxh/tmsa-roadmap) to see the current state of development.

### Installation for users
More info forthcoming.

### Installation for developers
Make sure to have `dll` and `ephe` folders in your `src` directory for running the program directly from the command line!

### How to build this application
##### For 32-bit Windows:
```shell
conda create -n whatever
conda activate whatever
conda config --env --set subdir win-32
conda install python=3.10  # newest 32-bit version that Conda can find
pip install -r .\\etc\\requirements.txt

python setup.py bdist_msi
```

### Contributing

##### Formatting
`blue src` (ensure you have `blue` installed first!)