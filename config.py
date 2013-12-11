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
lxPackage = 'baboonstack.package.conf'
lxPrevPackage = 'baboonstack.previous.package.conf'

lxInfo = {
    'linux': {
        'osname': 'linux',
        'version': lxVersion,
        'basedir': '/opt/litixsoft/baboonstack',
        'update': 'baboonstack-.*-linux-{0}.tar.gz',
        'package': '{0}-v{1}-linux-{2}.tar.gz',
        'scriptfile': 'lxScript.sh',
        'node': {
            'package': {
                'x32': 'node-v{0}-linux-x86.tar.gz',
                'x64': 'node-v{0}-linux-x64.tar.gz'
            },
            'links': {
                'node': {
                    'source': 'bin',
                    'target': '/usr/bin'
                },
                'npm': {
                    'source': 'bin',
                    'target': '/usr/bin'
                },
                'node_modules': {
                    'source': 'lib',
                    'target': '/usr/lib'
                }
            }
        },
        'messages': {
            'ADMINNAME': 'root',
            'REQUIREADMIN': 'This operation required root rights!'
        }

    },
    'darwin': {
        'osname': 'darwin',
        'version': lxVersion,
        'basedir': '/usr/share/litixsoft/baboonstack',
        'update': 'baboonstack-.*-darwin-{0}.tar.gz',
        'package': '{0}-v{1}-darwin-{2}.tar.gz',
        'scriptfile': 'lxScript.sh',
        'node': {
            'package': {
                'x32': 'node-v{0}-darwin-x86.tar.gz',
                'x64': 'node-v{0}-darwin-x64.tar.gz'
            },
            'links': {
                'node': {
                    'source': 'bin',
                    'target': '/usr/bin'
                },
                'npm': {
                    'source': 'bin',
                    'target': '/usr/bin'
                },
                'node_modules/npm': {
                    'source': 'lib',
                    'target': '/usr/lib',
                    'options': ['create_base_dir', 'remove_if_exists']
                }
            }
        },
        'messages': {
            'ADMINNAME': 'super user',
            'REQUIREADMIN': 'This operation required super user rights!'
        }
    },
    'win32': {
        'osname': 'windows',
        'version': lxVersion,
        'update': 'baboonstack-.*-windows-{0}.exe',
        'package': '{0}-v{1}-windows-{2}.zip',
        'scriptfile': 'lxScript.cmd',
        'node': {
            'package': {
                'x32': 'node-v{0}-x86.msi',
                'x64': 'x64/node-v{0}-x64.msi'
            },
            'links': {
            }
        },
        'messages': {
            'ADMINNAME': 'administrator',
            'REQUIREADMIN': 'This operation required administrator rights!'
        }
    }
}

lxOptions = {
    'removeall': {
        'short': '-r',
        'long': '--remove-all'
    },
    'alwaysyes': {
        'short': '-yes',
        'long': '--always-yes'
    },
    'ask': {
        'short': '-ask',
        'long': '--ask'
    },
    'noheader': {
        'short': '-nh',
        'long': '--noheader'
    }
}

# Returns Program Information for the current Operation System
# Returns empty object, if no Information available
def getConfig():
    if sys.platform in lxInfo:
        return lxInfo[sys.platform]
    else:
        return {}

# Programconfiguration
lxConfig = getConfig()

# Helper
def getConfigKey(key, defaultvalue=None, data=lxConfig):
    keypath = key.split('.')
    keydata = data

    for keyname in keypath:
        if keyname in keydata:
            if isinstance(keydata[keyname], dict):
                keydata = keydata[keyname]
            else:
                return keydata[keyname]
        else:
            if not defaultvalue:
                raise Exception('No Key "' + keyname + '" in "' + key + '"...')
            else:
                return defaultvalue

    return keydata

# Returns system specified messages
def getMessage(key):
    if 'messages' in lxConfig and str(key).upper() in lxConfig['messages']:
        return lxConfig['messages'][str(key).upper()]
    else:
        return ''