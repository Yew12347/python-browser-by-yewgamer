import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine-tuning.
build_exe_options = {"packages": ["os"]}

# Replace "main.py" with the name of your main Python script.
executables = [Executable("main.py", base="Win32GUI", icon="icon.ico")]

setup(
    name="Yewgamer Browser",
    version="1.0.0",
    description="Browser by yewgamer",
    options={"build_exe": build_exe_options},
    executables=executables
)
