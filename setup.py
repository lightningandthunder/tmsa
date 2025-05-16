import os
import shutil
import subprocess
import sys
import zipfile

from cx_Freeze import Executable, setup
from setuptools import Command

from src.constants import VERSION

base = ""
out_dir = "dist"
build_dir = None
copyright = "Copyright (C) 2024 James A. Eshelman"

match sys.platform:
    case "win32":
        base = "Win32GUI"
    case "linux":
        base = None
        import glob

        build_dirs = glob.glob("build/exe.linux-*")
        build_dir = build_dirs[0] if build_dirs else None
        if build_dir is None:
            raise RuntimeError("Could not find the cx_Freeze build output directory")

    case "darwin":
        base = None
    case _:
        raise RuntimeError(f"Unsupported architecture {sys.platform}")

match sys.platform:
        case "win32":
            executable = Executable(
                    script=os.path.join("src", "tmsa.py"),
                    copyright=copyright,
                    base=base,
                    icon=os.path.join("src", "assets", "tmsa3.ico"),
                    shortcut_name="Time Matters",
                    shortcut_dir="DesktopFolder"
                )
        case "linux":
            executable = Executable(
                    script=os.path.join("src", "tmsa.py"),
                    copyright=copyright,
                    base=base,
                )
        case "darwin":
            executable = Executable(
                    script=os.path.join("src", "tmsa.py"),
                    copyright=copyright,
                    base=base,
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

source_files = []
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            source_files.append(os.path.join(root, file))

options = {
    "build_exe": {
        "include_path": "src,public",
        "include_files": [
            (os.path.join("src", "dll"), "dll"),
            (os.path.join("src", "ephe"), "ephe"),
            (os.path.join("src", "assets"), "assets"),
            (os.path.join("src", "help"), "help"),
            *source_files
        ],
        "packages": [
            'distutils',    
        ],
        'include_msvcr': True,
    },
    "bdist_msi": {
        "add_to_path": True,
        # "data": msi_data,
        # "environment_variables": [],
        "upgrade_code": "{1b179824-25df-4630-80a7-b3930038f5e9}",
    },
    "bdist_dmg": {
        "volume_label": f"Time Matters {VERSION}",
        "applications_shortcut": True,
    },
}

class BuildInstaller(Command):
    description = "Build the executable and create a makeself installer"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # First, run the build command from cx_Freeze
        self.run_command('build_exe')

        # Name of the output installer
        installer_name = f"TimeMatters-{VERSION}-linux-x86_64.sh"

        # symlink_path = os.path.join(build_dir, 'run-tmsa')  # INSIDE exe.linux-*/ folder
        # target_path = './tmsa'  # Relative path to tmsa from symlink

        # # Clean up if needed
        # if os.path.lexists(symlink_path):
        #     os.remove(symlink_path)

        # os.symlink(target_path, symlink_path)

        # Path to postinstall.sh relative to project root
        postinstall_src = os.path.join(os.path.dirname(__file__), "postinstall.sh")
        postinstall_dst = os.path.join(build_dir, "postinstall.sh")
        shutil.copyfile(postinstall_src, postinstall_dst)
        os.chmod(postinstall_dst, 0o755)  # make sure it's executable

        # Command to create the self-extracting installer using makeself
        makeself_command = [
            'makeself',
            '--notemp',
            build_dir,
            installer_name,
            f'Time Matters {VERSION} Installer',
            './postinstall.sh',
        ]

        # Run the makeself command
        subprocess.check_call(makeself_command)

cmdclass = {
    'build_installer': BuildInstaller,
}

setup(
    name="Time Matters",
    version=VERSION,
    description="Time Matters",
    options=options,
    executables=[executable],
    **({"cmdclass": cmdclass} if sys.platform == "linux" else {})
)

if sys.platform == "win32":
    file_name = f"Time Matters-{VERSION}-win32"
    zipped_file_name = f"{file_name}.zip"
    zipped_path = os.path.join(out_dir, zipped_file_name)
    installer_path = os.path.join(out_dir, f"{file_name}.msi")
    with zipfile.ZipFile(zipped_path, 'w') as zipf:
        zipf.write(installer_path, arcname=f"{file_name}.msi")
elif sys.platform == 'linux':
    os.makedirs(out_dir, exist_ok=True)
    installer_name = f"TimeMatters-{VERSION}-linux-x86_64.sh"
    if os.path.exists(os.path.join(build_dir, installer_name)):
        os.remove(os.path.join(build_dir, installer_name))

    shutil.move(installer_name, build_dir)
    
    file_name = f"TimeMatters-{VERSION}-linux-x86_64"
    zipped_file_name = f"{file_name}.zip"
    zipped_path = os.path.join(out_dir, zipped_file_name)
    installer_path = os.path.join(build_dir, f"{file_name}.sh")

    if os.path.exists(zipped_path):
        os.remove(zipped_path)
    
    with zipfile.ZipFile(zipped_path, 'w') as zipf:
        zipf.write(installer_path, arcname=os.path.basename(installer_path))

