import sys
from cx_Freeze import setup, Executable

#if sys.platform == 'win32':

setup( name = "bbc",
       version = "1.3.0",
       description = "Baboonstack Manager",
       options = {"build_exe": {}},
       executables = [Executable("bbc.py")])