#-------------------------------------------------------------------------------
# Name:        config
# Purpose:     Configuration for Baboonstack for different Platforms
#
# Author:      Thomas Scheibe
#
# Created:     05.08.2018
# Copyright:   (c) Litixsoft GmbH 2014
# Licence:     Licensed under the MIT license.
#-------------------------------------------------------------------------------
import sys
import os

lxVersion = '1.4.0'
lxServer = 'http://packages.litixsoft.de'
lxPackage = 'baboonstack.package.conf'
lxPreviousPackage = 'baboonstack.previous.package.conf'
lxUserSettingPath = os.path.join(os.path.expanduser('~'), '.bbs')

lxInfo = {
    'linux': {
        'osname': 'linux',
        'version': lxVersion,
        'basedir': '/opt/litixsoft/baboonstack',
        'update': 'baboonstack-.*-linux-{0}.tar.gz',
        'package': '{0}-v{1}-linux-{2}.tar.gz',
        'packagemask': '[A-Za-z0-9]*-v.*-linux-{0}.tar.gz',
        'scriptfile': 'lxscript.sh',
        'configfile': 'package.bbs.conf',
        'node': {
            'package': {
                'x86': 'node-v{0}-linux-x86.tar.gz',
                'x64': 'node-v{0}-linux-x64.tar.gz'
            },
            'links': {
                'node': {
                    'source': 'bin',
                    'target': '/usr/bin'
                },
                'npm': {
                    'source': '/usr/lib/node_modules/npm/bin/npm-cli.js',
                    'target': '/usr/bin',
                    'options': ['absolute_source', 'no_source_check']
                },
                'node_modules': {
                    'source': 'lib',
                    'target': '/usr/lib'
                }
            }
        },
        'mongo': {
            'package': {
                'x64': 'https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-{0}.tgz',
                'x86': 'https://fastdl.mongodb.org/linux/mongodb-linux-i686-{0}.tgz'
            },
            'helper': {
                'x64': 'http://packages.litixsoft.de/mongo-linux-x64.tar.gz',
                'x86': 'http://packages.litixsoft.de/mongo-linux-x86.tar.gz'
            },
            'links': {
                'mongo': {
                    'source': 'bin',
                    'target': '/usr/bin'
                },
                'mongod': {
                    'source': 'bin',
                    'target': '/usr/bin'
                }
            },
            'patches': {
                'lxscript.sh': {
                    'sha1': '98a838e7fe75f906d318771c0bd3275a23e14c2a',
                    'action': [
                        {
                            'line': 83,
                            'action': 'remove'
                        },
                        {
                            'line': 84,
                            'action': 'remove'
                        },
                        {
                            'line': 85,
                            'action': 'remove'
                        }
                    ]
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
        'packagemask': '[A-Za-z0-9]*-v.*-darwin-{0}.tar.gz',
        'scriptfile': 'lxscript.sh',
        'configfile': 'package.bbs.conf',
        'node': {
            'package': {
                'x86': 'node-v{0}-darwin-x86.tar.gz',
                'x64': 'node-v{0}-darwin-x64.tar.gz'
            },
            'links': {
                'node': {
                    'source': 'bin',
                    'target': '/usr/bin'
                },
                'npm': {
                    'source': '/usr/lib/node_modules/npm/bin/npm-cli.js',
                    'target': '/usr/bin',
                    'options': ['absolute_source', 'no_source_check']
                },
                'node_modules/npm': {
                    'source': 'lib',
                    'target': '/usr/lib',
                    'options': ['create_base_dir', 'remove_if_exists']
                }
            }
        },
        'mongo': {
            'package': {
                'x64': 'https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-{0}.tgz'
            },
            'helper': {
                'x64': 'http://packages.litixsoft.de/mongo-darwin-x64.tar.gz'
            },
            'links': {
                'mongo': {
                    'source': 'bin',
                    'target': '/usr/bin'
                },
                'mongod': {
                    'source': 'bin',
                    'target': '/usr/bin'
                }
            },
            'patches': {
                'lxscript.sh': {
                    'sha1': '0f62a076df48a928f14b268270c90992ebb16405',
                    'action': [
                        {
                            'line': 77,
                            'action': 'remove'
                        },
                        {
                            'line': 78,
                            'action': 'remove'
                        }
                    ]
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
        'packagemask': '[A-Za-z0-9]*-v.*-windows-{0}.zip',
        'scriptfile': 'lxScript.cmd',
        'configfile': 'package.bbs.conf',
        'node': {
            'package': {
                'x86': 'node-v{0}-x86.msi',
                'x64': 'x64/node-v{0}-x64.msi'
            },
            'links': {
            }
        },
        'mongo': {
            'package': {
                'x64': 'https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-2008plus-{0}.zip',
                'x86': 'https://fastdl.mongodb.org/win32/mongodb-win32-i386-{0}.zip',
            },
            'helper': {
                'x64': 'http://packages.litixsoft.de/mongo-windows-x64.zip',
                'x86': 'http://packages.litixsoft.de/mongo-windows-x86.zip'
            },
            'binary': {
                'mongod': 'bin\\mongod.exe',
                'mongo': 'bin\\mongo.exe',
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
    'force': {
        'short': '-f',
        'long': '--force'
    },
    'ask': {
        'short': '-ask',
        'long': '--ask'
    },
    'noheader': {
        'short': '-nh',
        'long': '--noheader'
    },
    'local': {
        'short': '-l',
        'long': '--local'
    },
    'safe': {
        'short': '-s',
        'long': '--safe'
    },
    'remote': {
        'short': '-r',
        'long': '--remote'
    },
    'noswitch': {
        'short': '-ns',
        'long': '--noswitch'
    },
    'all': {
        'short': '-all',
        'long': '--all'
    }
}


# Returns Program Information for the current Operation System
# Returns empty object, if no Information available
def getConfig():
    for item in lxInfo:
        if sys.platform.startswith(item):
            return lxInfo[item]

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
            # if not defaultvalue:
            #     raise Exception('No Key "' + keyname + '" in "' + key + '"...')
            # else:
            return defaultvalue

    return keydata


# Returns system specified messages
def getMessage(key):
    if 'messages' in lxConfig and str(key).upper() in lxConfig['messages']:
        return lxConfig['messages'][str(key).upper()]
    else:
        return ''