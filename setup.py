import os
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY'] = "C:/Users/javel/AppData/Local/Programs/Python/Python37-32/tcl/tcl8.6"
os.environ['TK_LIBRARY'] = "C:/Users/javel/AppData/Local/Programs/Python/Python37-32/tcl/tk8.6"


buildOptions = dict(
    include_files=[
        'C:/Users/javel/AppData/Local/Programs/Python/Python37-32/DLLs/tcl86t.dll',
        'C:/Users/javel/AppData/Local/Programs/Python/Python37-32/DLLs/tk86t.dll'
    ],
    packages=["tkinter", "sys", "os", "random"],
    excludes=[],
)

import sys
base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('main.py', base=base)
]

setup(name='Minesweeper',
      version='0.1',
      description='',
      options=dict(build_exe=buildOptions),
      executables=executables)
