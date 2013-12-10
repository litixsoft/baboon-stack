from cx_Freeze import setup, Executable

setup( name = "bbs",
       version = "1.3.0",
       description = "Baboonstack Manager",
       options = {"build_exe": {}},
       executables = [Executable("bbs.py")]
)