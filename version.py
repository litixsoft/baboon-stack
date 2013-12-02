#-------------------------------------------------------------------------------
# Name:        version
# Purpose:
#
# Author:      Thomas Scheibe
#
# Created:     05.08.2013
# Copyright:   (c) Thomas Scheibe 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys

lxVersion = '1.3.0'
lxServer = 'http://packages.litixsoft.de'
lxPacket = 'baboonstack-v{0}-windows-{1}.exe'

lxInfo = {
    'linux': {
        'osname': 'linux',
        'version': lxVersion,
        'basedir': '/opt/litixsoft/baboonstack',
        'package': 'baboonstack-.*-linux-{0}.tar.gz',
        'node': {
            'package': {
                'x32': 'node-v{0}-linux-x86.tar.gz',
                'x64': 'node-v{0}-linux-x64.tar.gz'
            },
            'target': {
                'bin': '/usr/bin',
                'lib': '/usr/lib'
            }
        }
    },
    'darwin': {
        'osname': 'darwin',
        'version': lxVersion,
        'basedir': '/usr/share/litixsoft/baboonstack',
        'package': 'baboonstack-.*-darwin-{0}.tar.gz',
        'node': {
            'package': {
                'x32': 'node-v{0}-darwin-x86.tar.gz',
                'x64': 'node-v{0}-darwin-x64.tar.gz'
            },
            'target': {
                'bin': '/usr/bin',
                'lib': '/usr/lib'
            }
        }
    },
    'win32': {
        'osname': 'windows',
        'version': lxVersion,
        'package': 'baboonstack-.*-windows-{0}.exe',
        'node': {
            'package': {
                'x32': 'node-v{0}-x86.msi',
                'x64': 'x64/node-v{0}-x64.msi'
            },
            'target': {
            }
        }
    }
}

# Returns Program Information for the current Operation System
# Returns empty object, if no Information available
def getConfig():
    if sys.platform in lxInfo:
        return lxInfo[sys.platform]
    else:
        return {}

def getConfigKey(key):
    keypath = key.split('.')
    keydata = lxConfig

    for keyname in keypath:
        if keyname in keydata:
            if isinstance(keydata[keyname], dict):
                keydata = keydata[keyname]
            else:
                return keydata[keyname]
        else:
            break

    return ''

# Programconfiguration
lxConfig = getConfig()
