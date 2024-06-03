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
pip install -r .\\etc\\requirements-win32.txt

python setup.py bdist_msi
```

##### For 64-bit Linux:
First, install Pyenv so you can easily install a specific Python version and make a virtualenv using it. https://github.com/pyenv/pyenv

Unfortunately, you can't use Conda, as this breaks all of the fonts.
```shell
pyenv install 3.10
pyenv global 3.10
python3 -m venv venv

sudo apt install python3-dev tcl-dev tk-dev \
    fontconfig libfontconfig1 libfontconfig1-dev \
    cmake cmake-data extra-cmake-modules build-essential
python -m pip install scikit-build

pip install -r etc/requirements-linux.txt

# Give permissions for lib and log file directories
sudo mkdir -p /var/lib/tmsa
# enter sudo password
sudo chown $USER:$USER /var/lib/tmsa
sudo chmod 755 /var/lib/tmsa
sudo mkdir -p /var/log/tmsa
sudo chown $USER:$USER /var/log/tmsa
sudo chmod 755 /var/log/tmsa


```

### Contributing

##### Formatting
`blue src` (ensure you have `blue` installed first!)