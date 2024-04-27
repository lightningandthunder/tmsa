from cx_Freeze import Executable, setup
import os

executable = Executable(
        os.path.join('src', 'tmsa.py'),
        copyright="Copyright (C) 2024 AAAAA",
        base="gui",
        icon="python",
        shortcut_name="TMSA Test",
    )

# https://stackoverflow.com/questions/15734703/use-cx-freeze-to-create-an-msi-that-adds-a-shortcut-to-the-desktop/15736406#15736406
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

directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
]

msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", None, None, "This is a description", "IconId", None),
    ],
    # "Icon": [
    #     ("IconId", "icon.ico"),
    # ],
}


options = {
    "build_exe": {
        "include_path": "src",
        "include_files": [
            (r"C:\sweph\dll\swedll32.dll", r"dll\swedll32.dll"),
            (r"C:\sweph\ephe", r"ephe"),
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
        "data": msi_data,
        "environment_variables": [],
        "upgrade_code": "{6B29FC40-CA47-1067-B31D-00DD010662DB}",  # ???
}
}

setup(
    name="Time Matters",
    version="0.0.0.0.0.1",
    description="Sample cx_Freeze script",
    options=options,
    executables=[executable],
)