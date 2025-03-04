import os
import sys
import subprocess
import shutil

def build_windows_installer():
    """Build Windows MSI installer using PyInstaller and WiX"""
    print("Building PCPulse Windows application...")

    # Clean any previous build
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # Create PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=PCPulse",
        "--windowed",
        "--icon=resources/icons/pcpulse.ico",
        "--add-data=resources;resources",
        "--clean",
        "src/main.py"
    ]

    # Run PyInstaller
    subprocess.run(pyinstaller_cmd, check=True)

    print("PyInstaller build completed.")
    print("To create an MSI installer, install WiX Toolset and run:")
    print("candle -ext WixUIExtension PCPulse.wxs")
    print("light -ext WixUIExtension PCPulse.wixobj")

if __name__ == "__main__":
    build_windows_installer()
