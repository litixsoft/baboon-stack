#-------------------------------------------------------------------------------
# Name:        package
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     04.12.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import json
import sys
import os

import version
import lxtools


class BaboonStackPackage:

    # Create a list with local installed components
    def __getlocalcomponents(self):
        self.__locallist = {}
        rootdir = lxtools.getBaboonStackDirectory()

        for packagename in self.getpackagelist():
            pkgdata = self.__packagedata['packages'][packagename]
            if not isinstance(pkgdata, dict):
                continue

            if os.path.exists(os.path.join(rootdir, pkgdata.get('dirname', 'none'))):
                self.__locallist[packagename] = pkgdata

    def __init__(self):
        self.__packagename = os.path.join(lxtools.getBaboonStackDirectory(), version.lxPackage)
        self.__packagedata = {}
        self.__locallist = {}

        self.loadpackage(self.__packagename)
        pass

    def loadpackage(self, filename):
        try:
            cfgfile = open(filename, mode='r')
            data = cfgfile.read()
            cfgfile.close()
        except BaseException as e:
            print('>> ERROR: Unable to read configuration file...')
            print('>>', e)
            return False

        try:
            self.__packagedata = json.loads(data)
        except BaseException as e:
            print('>> JSON ERROR: Unable to parse configuration file...')
            print('>>', e)
            print('>> Abort...')
            return False

        # Build locally installed components list
        self.__getlocalcomponents()
        return True

    def showpackage(self):
        print(self.__packagedata)

    def getpackageversion(self):
        return self.__packagedata.get('version', '<unknow>')

    def getpackagelist(self):
        pkglist = []
        if 'packages' in self.__packagedata:
            for packagename in self.__packagedata['packages']:
                pkglist.append(packagename)

        return pkglist

    def getpackagesinfo(self):
        pkglist = []
        for packagename in self.getpackagelist():
            pkginfo = {
                'name': packagename,
                'version': self.__packagedata['packages'][packagename].get('version', '')
            }

            # If package locally installed
            if packagename in self.__locallist:
                pkginfo['installed'] = 'Installed'

            # Add package info to list
            pkglist.append(pkginfo)

        # Return list
        return pkglist


# Load default
package = BaboonStackPackage()


# Main
def main():
    print('BaboonStack Version'.ljust(20, '.'), ':', package.getpackageversion())
    print('Packages:')
    for pkg in package.getpackagesinfo():
        print(str(' ' + pkg.get('name')).ljust(20, '.'), ':', pkg.get('installed', 'Not installed'))

    print('')
    return True