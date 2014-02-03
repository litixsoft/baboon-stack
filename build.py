import os
import sys
import stat
import subprocess
from cx_Freeze import Executable, Freezer, setup
import lxtools
from cx_Freeze import main

srcdir = '.'
distdir = os.path.join(srcdir, 'build')
iconfile = os.path.join(srcdir, 'ressources', 'baboonstack.ico')

scriptFiles = [
    os.path.join(srcdir, 'bbs.py')
]

# Remove build directory
if os.path.exists(distdir):
    lxtools.rmDirectory(distdir)

#main()

executables = {}
for scriptFile in scriptFiles:

    if sys.platform.startswith('win'):
        ex = Executable(
            scriptFile,
            icon=iconfile,
            appendScriptToExe=True,
        )
    else:
        # Unix Build
        ex = Executable(
            scriptFile,
        )

    executables[ex] = True

f = Freezer(
    executables,
    #includes=includes,
    excludes=[], #excludes,
    targetDir=distdir,
    #initScript="/Users/george/git/OpenMeta-analyst-/src/open_meta_mac.py",
    copyDependentFiles=True,
    #appendScriptToExe=True,
    #optimizeFlag=1,
    compress=False,
    #silent=True,
)

f.Freeze()

# Change the absolute paths in all library files to relative paths
# This should be a cx_freeze task, but cx_freeze doesn't do it
if sys.platform == 'darwin':
    print("Patch librarys for MacOS...")
    shippedfiles = os.listdir(distdir)

    for file in shippedfiles:
        #Do the processing for any found file or dir, the tools will just
        #fail for files for which it does not apply
        filepath = os.path.join(distdir, file)

        #Ensure write permissions
        mode = os.stat(filepath).st_mode
        if not (mode & stat.S_IWUSR):
            os.chmod(filepath, mode | stat.S_IWUSR)

        #Let the library itself know its place
        subprocess.call(('install_name_tool', '-id', '@executable_path/' + file, filepath))

        #Find the references
        otool = subprocess.Popen(('otool', '-L', filepath), stdout=subprocess.PIPE)
        libs = otool.stdout.readlines()
        for lib in libs:
            #For each referenced library, chech if it is in the set of
            #files that we ship. If so, change the reference to a path
            #relative to the executable path
            lib = lib.decode()
            filename, _, _ = lib.strip().partition(' ')
            prefix, name = os.path.split(filename)

            if name in shippedfiles:
                newfilename = '@executable_path/' + name
                print('%s => %s' % (name, newfilename))
                subprocess.call(('install_name_tool', '-change', filename, newfilename, filepath))

print("Done")