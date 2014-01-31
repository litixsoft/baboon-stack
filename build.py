import lxtools
import os
from cx_Freeze import main

# Remove build directory
if os.path.exists('build'):
    lxtools.rmDirectory('build')

main()