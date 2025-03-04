import sys
from cx_Freeze import setup, Executable

# Define dependencies
build_exe_options = {
    "packages": ["os", "PySide6", "psutil", "cpuinfo", "wmi", "win32com", "win32con", "win32api"],
    "excludes": [],
    "include_msvcr": True,
}

# Windows GUI application base
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    # Package metadata
    name="PCPulse",
    version="1.0.0",
    author="Anthony Wagonis",
    author_email="barefaced.storm@gmail.com",
    description="Cross-platform hardware monitoring application",
    keywords="hardware, monitoring, temperature, cpu, gpu",

    # Package definition
    packages=["src", "src.ui"],

    # Dependencies
    install_requires=[
        "psutil>=5.9.0",
        "py-cpuinfo>=8.0.0",
        "GPUtil>=1.4.0",
        "PySide6>=6.4.0",
        "wmi>=1.5.1",
        "pywin32>=305",
    ],

    # Platform-specific extras (still useful for pip installs)
    extras_require={
        "windows": ["pywin32>=305", "wmi>=1.5.1"],
        "macos": [""],
    },

    # Python requirements
    python_requires=">=3.7",

    # cx_Freeze specific options for MSI generation
    options={
        "build_exe": build_exe_options,
        "bdist_msi": {
            "upgrade_code": "{65BC2EC6-7A93-4EAE-A76A-BDA92A64F4E5}",
            "add_to_path": True,
            "initial_target_dir": r"[ProgramFilesFolder]\PCPulse",
        }
    },

    # Executables to create
    executables=[
        Executable(
            "src/main.py",
            base=base,
            target_name="PCPulse.exe",
            shortcut_name="PCPulse",
            shortcut_dir="ProgramMenuFolder",
            copyright="Copyright (c) 2025 Anthony Wagonis",
            icon="src/PCPulse.ico",
        )
    ],

    # Entry points (for pip install usage)
    entry_points={
        "console_scripts": [
            "pcpulse=src.main:main",
        ],
    },
)
