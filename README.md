#BABOONSTACK

a Suite with NodeJS, MongoDB, RedisIO and a system-wide Node Version Manager for Linux, MacOS and Windows based 32-bit and 64-bit Operation Systems.

**Feel free to build your own Baboon Stack or just simply use our installer.**

For Linux and MacOS, run this command in your Terminal.

	curl http://packages.litixsoft.de/installer.sh | sh

Windows Users follow this link to download the installation file.

http://www.litixsoft.de/products-baboonstack

#### Baboonstack Directory Structure

    └───BABOONSTACK
        ├── BBS
        │   ├── NODE - Windows only. The target of the link of the current node version.
        │   └── [Place lxBaboon Manager here]
        ├── REDISIO
        │   ├── BIN - Binaryfolder
        │   ├── LOG - Logfolder
        │   ├── DB  - Databasefolder
        │   └── lxScript.sh/lxScript.cmd
        ├── MONGO
        │   ├── BIN - Binaryfolder
        │   ├── LOG - Logfolder
        │   ├── DB  - Databasefolder
        │   └── lxScript.sh/lxScript.cmd
        └── NODE
            └── x.xx.xx - NodeJS Version x.xx.xx Installation

## Baboon Manager

A powerful tool with a integrated **Node Version Manager** and **Node Service Manager**.

## Build Client

**Requirements:**
* Python 3.3 Runtime (see http://www.python.org/)
* cxFreeze for Python 3.3 (see http://cx-freeze.sourceforge.net/)
* Windows: Microsoft Visual C++ 2010 x86 Redistributable Package Service Pack 1

*Note*

On Linux x64 system you need the 64bit Runtime of Python 3.3. Or just install **ia32libs**.

#### Build Instructions

Be sure that the dependencies have been installed correctly. Then start the build scripts.

On Windows systems

    make.cmd

On Unix systems

	make.sh

Copy all content from **build/** to your **/baboonstack/bbs** folder. Include the files from **packages/[version]/[os]/**