#BABOONSTACK

a Suite with NodeJS, MongoDB, RedisIO and a system-wide Node Version Manager for Linux, MacOS and Windows based 32-bit and 64-bit Operation Systems.

**Feel free to build your own Baboon Stack or just simply use our installer.**

For Linux and MacOS, run this command on your Terminal.

	curl http://packages.litixsoft.de/installer.sh | sudo sh

Windows Users follow this link to download the installation file. 

http://http://www.litixsoft.de/products-baboonstack

#### Baboonstack Directory Structure

* BABOONSTACK
    * LXM
    	* NODE - Windows only. The target of the link of the current node version.
    	* 	[Place lxManager here]
    * REDISIO
        * BIN	- Binaryfolder
        * LOG	- Logfolder
        * DB	- Databasefolder
        * lxScript.sh/lxScript.cmd
    * MONGO
        * BIN	- Binaryfolder
        * LOG   - Logfolder
        * DB    - Databasefolder
        * lxScript.sh/lxScript.cmd
    * NODE
        * x.xx.xx - NodeJS Installation

## lxManager

A powerful tool with a integrated **Node Version Manager** and **Node Service Manager**.

### File and Directory Overview

* lxm.sh - lxManager for Unix systems
* installer.sh - Online/Offline installer for Unix systems
    *	LINUX - Contains scripts for Linux system
    *	MACOS - Contains scripts for MacOS system
    *	WIN   - Contains lxManager for Windows system
    	*	TOOLS - Contains tools for Windows

## Build Linux/MacOS Client

Requirements:
* Shell

#### Build Instructions

Not required.

Just copy lxm.sh to your **baboonstack/lxm** folder.

## Build Windows Client

Requirements:
* Python 3.3_x86 Runtime (see http://www.python.org/)
* cxFreeze for Python 3.3 (see http://cx-freeze.sourceforge.net/)
* Microsoft Visual C++ 2010 x86 Redistributable Package Service Pack 1

#### Build Instructions

Be sure that the dependencies have been installed correctly. Then start the build scripts.

	win\build.cmd

Copy all content from **win\build** to your **baboonstack\lxm** folder include the files from **win\tools**