#-------------------------------------------------------------------------------
# Name:        lxtools
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     02.08.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import subprocess
import tarfile
import zipfile
import platform
import hashlib
import urllib.request as UrlRequest
import signal
import shutil
import json
import sys
import os

if sys.platform == 'win32':
    import ctypes
    import ctypes.wintypes

# Baboonstack modules
import config


class Arguments:

    def __init__(self):
        self.__args = sys.argv.copy()
        self.__options = []

        # Remove the first Argument
        self.__args.pop(0)

        # Remove options
        optlist = []
        for opt in self.__args.copy():
            if opt[0] == '-':
                optlist.append(opt.lower())
                self.__args.remove(opt)

        for opt in optlist:
            if opt.count('-', 0, 2) == 1:
                fieldname = 'short'
            else:
                fieldname = 'long'

            for optname in config.lxOptions:
                if config.lxOptions[optname].get(fieldname, '').lower() == opt:
                    self.__options.append(optname)
                    break

    # Returns item count
    def count(self):
        return len(self.__args)

    # Get the FIRST element and remove it from list
    def get(self, defaultvalue='', count=1):
        if self.count() != 0:
            if count == 1 or self.count() == 1:
                # Returns single
                return self.__args.pop(0)
            else:
                # Returns multi
                if not count > 0:
                    return self.__args
                else:
                    result = []
                    while self.count() != 0 and count > 0:
                        result.append(self.__args.pop(0))
                        count -= 1

                    return result
        else:
            return defaultvalue

    # Returns TRUE or FALSE if NAME in list, if TRUE then removes element
    def find(self, name):
        if name in self.__args:
            self.__args.pop(self.__args.index(name))
            return True
        else:
            return False

    def getoptions(self):
        return self.__options

    def isoption(self, name):
        return name in self.__options


# Returns if x86 or x64
def getOsArchitecture():
    if platform.machine().endswith('64'):
        return 'x64'
    else:
        return 'x86'


# Returns if User an Admin
def getIfAdmin():
    if sys.platform == 'win32':
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        return os.geteuid() == 0

    return False


# Removes a Directory from System with all files
def rmDirectory(directory):
    nodes = os.listdir(directory)

    for item in nodes:
        itemname = os.path.join(directory, item)

        if os.path.isfile(itemname) or os.path.islink(itemname):
            try:
                os.remove(itemname)
            except IOError as e:
                print("Remove File error. I/O error({0}): {1}".format(e.errno, e.strerror))
        elif os.path.isdir(itemname):
            rmDirectory(itemname)

    try:
        os.rmdir(directory)
    except IOError as e:
        print("Remove Directory error. I/O error({0}): {1}".format(e.errno, e.strerror))


def removeFilesFromList(basedir, filelist, saferemove=True):
    dirlist = []

    # Remove every file from directory and marks directories
    for filename in filelist:
        fullpath = os.path.join(basedir, filename)
        if os.path.exists(fullpath):
            if os.path.isdir(fullpath):
                # Add dir to list, will be removed later
                dirlist.append(fullpath)
            else:
                # Remove file
                try:
                    os.remove(fullpath)
                except BaseException as e:
                    print(e)

    # Remove directory if empty
    for directory in dirlist:
        if len(os.listdir(directory)) == 0:
            os.rmdir(directory)

    # Remove base directory if exists and empty
    if os.path.exists(basedir):
        if len(os.listdir(basedir)) == 0:
            os.rmdir(basedir)
        else:
            # Remove directory with all files if not safe remove
            if not saferemove:
                print('Remove ewewwewe')
                rmDirectory(basedir)

# Returns the SHA1 Checksum of specified File
def getSHAChecksum(filename):
    sha = hashlib.sha1()
    tmpfile = open(filename, 'rb')
    while True:
        shadata = tmpfile.read(8192)

        # End of File
        if not shadata:
            break

        sha.update(shadata)

    # Close File
    tmpfile.close()

    # Returns Digest
    return sha.hexdigest()


# Creates a symbolic link of Directory
def setDirectoryLink(lpSymlinkName, lpTargetName):
    if os.path.exists(lpSymlinkName):
        return False

    # Windows
    if sys.platform == 'win32':
        CreateSymbolicLink = ctypes.windll.kernel32.CreateSymbolicLinkW
        CreateSymbolicLink.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        CreateSymbolicLink.restype = ctypes.c_bool

        return CreateSymbolicLink(lpSymlinkName, lpTargetName, 1)

    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        try:
            os.symlink(lpTargetName, lpSymlinkName)
            return True
        except BaseException as e:
            print('ERROR: ', e)
            return False

    raise Exception('ERROR: No API for setDirectoryLink.')


# Returns if lpFilename a Directory AND Reparse Point (Symbolic Link)
# FILE_ATTRIBUTE_DIRECTORY or FILE_ATTRIBUTE_REPARSE_POINT
def getIfSymbolicLink(lpFilename):
    if sys.platform == 'win32':
        return (ctypes.windll.kernel32.GetFileAttributesW(lpFilename) & 1040) == 1040

    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        return os.path.islink(lpFilename)

    raise Exception('ERROR: No API for getIfSymbolicLink.')


# Displays a Progress bar
def showProgress(amtDone):
    sys.stdout.write("\rProgress: [{0:50s}] {1:.1f}% ".format('#' * int(amtDone * 50), amtDone * 100))
    sys.stdout.flush()


# Callback for urlretrieve (Downloadprogress)
def reporthook(blocknum, blocksize, filesize):
    if filesize <= blocksize:
        return showProgress(1)

    if (blocknum > 0):
        percent = blocknum / (filesize / blocksize)
    else:
        percent = 0

    showProgress(percent)


# Download a Remote File to a temporary File and returns the filename
# Displays a Progress Bar during Download
def getRemoteFile(url, tempfile=''):
    showProgress(0)
    try:
        local_filename, headers = UrlRequest.urlretrieve(url, tempfile, reporthook=reporthook)
        showProgress(1)
        print('Done!')
    except KeyboardInterrupt:
        print('Abort!')
        return -1
    except IOError as e:
        print('Error!')
        print('IO Error! Abort!\n')
        print(e)
        return -1
    except:
        print('Error!')
        print('Unknow Error occured! Abort!')
        return -1

    return local_filename


# Clear temporary internet files
def cleanUpTemporaryFiles():
    UrlRequest.urlcleanup()


# Downloads a Remote File to a temporary File and returns the data
def getRemoteData(url):
    # Download from URL
    try:
        local_filename, headers = UrlRequest.urlretrieve(url)
    except IOError as e:
        print('IO Error! Abort!\n')
        print(e)
        return -1
    except:
        print('Unknow Error occured! Abort!')
        return -1

    # Open and Read local temporary File
    html = open(local_filename)
    data = html.read()
    html.close()

    # Delete temporary Internet File
    UrlRequest.urlcleanup()
    return data


# Returns the HOMEPATH of Baboonstack
def getBaboonStackDirectory():
    if sys.platform == 'win32':
        if 'LXPATH' in os.environ:
            return os.environ['LXPATH']

    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        if os.path.exists(config.lxConfig['basedir']):
            return config.lxConfig['basedir']

    return os.path.dirname(os.getcwd())


# Returns if NODE.JS Module (NVM/SERVICE) enabled
# Checks only if %LXPATH%\node exits
def getIfNodeModuleEnabled():
    nodePath = os.path.join(getBaboonStackDirectory(), 'node')
    return os.path.exists(nodePath)


# Returns if Mongo installed, Checks path only
def getIfMongoModuleEnabled():
    mongoPath = os.path.join(getBaboonStackDirectory(), 'mongo')
    return os.path.exists(mongoPath)


# Returns if Redis installed, Checks path only
def getIfRedisModuleEnabled():
    redisPath = os.path.join(getBaboonStackDirectory(), 'redisio')
    return os.path.exists(redisPath)


# Ready a single char from input
# Allowed Char in key, Upper Case Char for default (Return)
def readkey(prompt, keys='Yn'):
    keymap = []
    defaultkey = None

    # Build keymap
    for key in keys:
        if key.isupper() and not defaultkey:
            defaultkey = key.lower()

        keymap.append(key)

    # Output message
    msg = str('{0} ({1})').format(prompt, '/'.join(keymap))
    keys = keys.lower()

    while True:
        inp = input(msg).lower()

        # if RETURN pressed, then use default
        if len(inp) == 0:
            if defaultkey:
                return defaultkey
        else:
            if inp[0] in keys:
                return inp[0]


# Execute a shell command and return True/False
def run(command, cwd=None, showoutput=True):

    if showoutput is True:
        stdout = subprocess.STDOUT
    else:
        stdout = subprocess.DEVNULL

    result = subprocess.call(command, shell=True, cwd=cwd, stdout=stdout)
    # result = os.system(command)

    if result != 0:
        print('\nError while execute "' + command + '"...')
        print('Exitcode ' + str(result) + '\n')

    return result == 0


# Loads a json file
def loadjson(filename, reporterror=True):
    try:
        file = open(filename, mode='r')
        data = file.read()
        file.close()
    except BaseException as e:
        if reporterror:
            print('>> ERROR: Unable to open file...')
            print('>>', e)
        return {}

    try:
        return json.loads(data)
    except BaseException as e:
        if reporterror:
            print('>> JSON ERROR: Unable to parse package catalog...')
            print('>>', e)
        return {}


# Saves a json file
def savejson(filename, data, reporterror=True):
    try:
        file = open(filename, mode='w')
        file.write(json.dumps(data, sort_keys=True, indent=4))
        file.close()
    except BaseException as e:
        if reporterror:
            print('>> ERROR: Unable to write file...')
            print('>>', e)
        return False

    return True


# returns Platformname
def getPlatformName():
    platforms = ['win32', 'darwin', 'linux']

    for osname in platforms:
        if sys.platform.startswith(osname):
            return osname

    return 'unknow'


# returns if binary exists
def getIfBinaryExists(binary):
    # WIN32: Detect binary in environment variable ´path´
    if sys.platform == 'win32':
        if 'PATH' in os.environ:
            for path in str(os.environ['PATH']).split(';'):
                fullname = os.path.join(path, binary)

                if os.path.isfile(fullname):
                    return True

        return False

    # UNIX: Detect binary with ´whereis´
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        try:
            process = subprocess.Popen(['whereis', binary], stdout=subprocess.PIPE)
            result = process.communicate()
        except FileNotFoundError as e:
            return False
        else:
            for line in result:
                if line is None or not line:
                    continue

                filename = str(line, 'utf-8').strip()
                return os.path.isfile(filename)

        return False

    raise Exception('ERROR: getIfBinaryExists failed.')


# Change owner:group under Unix operation system
def chown(path, uid, gid):
    if getPlatformName() == 'win32' or not os.path.isdir(path):
        return False

    # Get dir Stat
    pathstat = os.stat(path)

    # Change owner:group if needed
    if not pathstat.st_uid == uid or not pathstat.st_gid == gid:
        try:
            os.lchown(path, uid, gid)
        except BaseException as e:
            print(e)
            return False

    result = True
    # For every file/dir
    for itemname in os.listdir(path):
        fullitemname = os.path.join(path, itemname)

        # If file or directory
        if os.path.isdir(fullitemname):
            chown(fullitemname, uid, gid)
        elif os.path.isfile(fullitemname):
            filestat = os.stat(fullitemname)

            # Change owner:group if needed
            if not filestat.st_uid == uid or not filestat.st_gid == gid:
                try:
                    os.chown(fullitemname, uid, gid)
                except BaseException as e:
                    print(e)
                    result = False
        else:
            print('Unknow', itemname)

    return result

# Extract archive file (source) to directory (target)
# Zip and Tar Archives supported
def doExtract(source, target):
    # .zip - 2 Bytes - 50 4B - \x50\x4b
    # .tgz - 2 Bytes - 1F 8B - \x1f\x8b
    archivefile = open(source, 'rb')
    ident = archivefile.read(2)
    archivefile.close()

    # ZIP File
    if ident == b'\x50\x4b' and zipfile.is_zipfile(source):
        zip = zipfile.ZipFile(source, 'r')
        zip.extractall(target)
        zip.close()

        return

    # Tar File
    if ident == b'\x1f\x8b':
        tar = tarfile.open(source)
        tar.extractall(target)
        tar.close()

        return True

    # print(ident)

    return False


# Moves all elements IN a directory to another one and returns filelist
def moveDirectory(src, tar):
    filelist = []

    if not os.path.isdir(src):
        return filelist

    if not os.path.isdir(tar):
        os.makedirs(tar)

    for name in os.listdir(src):
        if os.path.isdir(os.path.join(src, name)):
            subdir = moveDirectory(os.path.join(src, name), os.path.join(tar, name))

            # Add all files
            for dirname in subdir:
                filelist.append(os.path.join(name, dirname))

            # Add foldername
            filelist.append(name)
            continue

        if os.path.isfile(os.path.join(src, name)) and not os.path.isfile(os.path.join(tar, name)):
            filelist.append(name)
            shutil.move(
                os.path.join(src, name),
                os.path.join(tar, name)
            )

    return filelist


def loadFileFromUserSettings(filename, showerrors=True, returntype=None):
    if not os.path.exists(config.lxUserSettingPath):
        return None

    data = returntype
    try:
        filehandle = open(os.path.join(config.lxUserSettingPath, filename), 'r', encoding='utf8')

        if isinstance(returntype, list):
            tmpdata = filehandle.read()

            if tmpdata:
                data = tmpdata.split(',')
        else:
            data = filehandle.read()

        filehandle.close()
    except IOError:
        if showerrors:
            print('Error while read from ' + filename)

    return data


def saveFileToUserSettings(filename, data, showerrors=True):
    if not os.path.exists(config.lxUserSettingPath):
        os.mkdir(config.lxUserSettingPath)

    try:
        filehandle = open(os.path.join(config.lxUserSettingPath, filename), 'w', encoding='utf8')
        if isinstance(data, list):
            filehandle.write(','.join(data))
        else:
            filehandle.write(data)

        filehandle.close()
    except IOError:
        if showerrors:
            print('Error while write to ' + filename)


def getActiveProcessFromPidList(pidlist):
    pidActiveList = []

    if sys.platform == 'win32':
        EnumProcesses = ctypes.windll.psapi.EnumProcesses
        EnumProcesses.restype = ctypes.wintypes.BOOL

        OpenProcess = ctypes.windll.kernel32.OpenProcess
        OpenProcess.restype = ctypes.wintypes.HANDLE
        CloseHandle = ctypes.windll.kernel32.CloseHandle

        PROCESS_TERMINATE = 0x0001
        PROCESS_QUERY_INFORMATION = 0x0400

        processList = (ctypes.wintypes.DWORD * 4096)()
        processListSize = ctypes.sizeof(processList)
        sizeReturned = ctypes.wintypes.DWORD()

        if EnumProcesses(ctypes.byref(processList), processListSize, ctypes.byref(sizeReturned)):
            for index in range(int(sizeReturned.value / ctypes.sizeof(ctypes.wintypes.DWORD))):
                hProcess = OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, processList[index])

                if hProcess:
                    if str(processList[index]) in pidlist:
                        pidActiveList.append(str(processList[index]))

                    CloseHandle(hProcess)
        else:
            return None
    else:
        import errno

        for pid in pidlist:
            try:
                os.kill(int(pid), 0)
            except OSError as e:
                if e.errno == errno.EPERM:
                    pidActiveList.append(pid)
            else:
                pidActiveList.append(pid)

    return pidActiveList


def killProcess(pid):
    if sys.platform == 'win32':
        OpenProcess = ctypes.windll.kernel32.OpenProcess
        OpenProcess.restype = ctypes.wintypes.HANDLE

        CloseHandle = ctypes.windll.kernel32.CloseHandle

        TerminateProcess = ctypes.windll.kernel32.TerminateProcess
        TerminateProcess.restype = ctypes.wintypes.BOOL

        PROCESS_TERMINATE = 0x0001
        PROCESS_QUERY_INFORMATION = 0x0400

        hProcess = OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, pid)

        if hProcess:
            res = TerminateProcess(hProcess, -1)
            CloseHandle(hProcess)

            return res
    else:
        import errno

        try:
            os.kill(int(pid), signal.CTRL_C_EVENT)
        except OSError as e:
            return e.errno == errno.EPERM
        else:
            return True

    return False
