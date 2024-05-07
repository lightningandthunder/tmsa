from cx_Freeze import Executable, setup
import os
import sys
import zipfile
from src.constants import VERSION

base = ""
match sys.platform:
    case "win32":
        base = "Win32GUI"
    case _:
        raise RuntimeError(f"Unsupported architecture {sys.platform}")

executable = Executable(
        script=os.path.join("src", "tmsa.py"),
        copyright="Copyright (C) 2024 James A. Eshelman",
        base=base,
        icon="tmsa3.ico",
        # shortcut_name="Time Matters",
        # shortcut_dir="DesktopFolder"
    )

# https://stackoverflow.com/questions/15734703/use-cx-freeze-to-create-an-msi-that-adds-a-shortcut-to-the-desktop/15736406#15736406
# https://learn.microsoft.com/en-us/windows/win32/msi/shortcut-table
# shortcut_table = [
#     ("DesktopShortcut",        # Shortcut
#      "DesktopFolder",          # Directory_
#      "DTI Playlist",           # Name
#      "TARGETDIR",              # Component_
#      "[TARGETDIR]playlist.exe",# Target
#      None,                     # Arguments
#      None,                     # Description
#      None,                     # Hotkey
#      None,                     # Icon
#      None,                     # IconIndex
#      None,                     # ShowCmd
#      'TARGETDIR'               # WkDir
#      )
#     ]

# shortcut_table = [
# ("DesktopShortcut", # Shortcut
#  "DesktopFolder",   # Directory_
#  "Time Matters",# Name
#  "TARGETDIR",   # Component_
#  r"[TARGETDIR]tmsa.exe", # Target
#  None,              # Arguments
#  None,              # Description
#  None,              # Hotkey
#  "",                # Icon
#  0,                 # IconIndex
#  None,              # ShowCmd
#  "TARGETDIR",                   # WkDir
#  )
# ]

# Behavior is pretty detailed; see this link:
# https://learn.microsoft.com/en-us/windows/win32/msi/directory-table
# Directory (identifier), Directory_Parent, DefaultDir
# directory_table = [
#     ("ProgramMenuFolder", "TARGETDIR", "."),
#     ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
# ]

# These are database table entries for 32bit apps specifically;
# see this page for more details:
# https://learn.microsoft.com/en-us/windows/win32/msi/icon-table
# msi_data = {
#     # "Shortcut": shortcut_table,
#     "ProgId": [
#         # ProgId, ProgId_Parent, Class_, Description, Icon_, IconIndex
#         # ("TimeMatters", None, None, "This is a description", "IconId", 0),
#     ],
#     "Icon": [
#         # ("IconId", "star_icon.ico"),
#     ],
# }

options = {
    "build_exe": {
        "include_path": "src,public",
        "include_files": [
            (os.path.join("copy", "dll", "swedll32.dll"), os.path.join("dll", "swedll32.dll")),
            (os.path.join("copy", "ephe"), "ephe"),
            "tmsa3.ico",
            "help",
        ],
        "packages": [
            'distutils',    
        ],
        "includes": [
            "calc",
            "chart_options",
            "constants",
            "ingresses",
            "init",
            "libs",
            "locations",
            "midpoint_options",
            "more_charts",
            "new_chart",
            "program_options",
            "select_chart",
            "show_util",
            "show",
            "show2",
            "solunars",
            "swe",
            "tmsa",
            "widgets",
        ],
        'include_msvcr': True,
    },
    "bdist_msi": {
        "add_to_path": True,
        # "data": msi_data,
        # "environment_variables": [],
        "upgrade_code": "{1b179824-25df-4630-80a7-b3930038f5e9}",
    }
}

setup(
    name="Time Matters",
    version=VERSION,
    description="Time Matters",
    options=options,
    executables=[executable],
)

if sys.platform == "win32":
    zipped_file_name = f"Time Matters-{VERSION}.zip"
    zipped_path = os.path.join("dist", zipped_file_name)
    installer_path = os.path.join("dist", f"Time Matters-{VERSION}-win32.msi")
    with zipfile.ZipFile(zipped_path, 'w') as zipf:
        zipf.write(installer_path, zipped_file_name)