# BABOONSTACK
a Suite with Node.JS, MongoDB, RedisIO. Includes a system-wide Node Version Manager and MongoDB Version Manager for Linux, MacOS and Windows based 32-bit and 64-bit Operation Systems.

* Web site: http://www.litixsoft.de/products-baboonstack.html
* Unix Installer: http://www.litixsoft.de/products-baboonstack.html#installwindows
* Windows Installer: http://www.litixsoft.de/products-baboonstack.html#installunix

#Install
Download the build releases for windows, macos or linux based operation systems, or just build your own baboonstack manager client (see Build).

##System requirements

* Windows Visa/Seven/8
* Linux
* MacOs X

#Build Baboon Manager
##Requirements:
* Python 3.3.x Runtime (see http://www.python.org/)
* cxFreeze for Python 3.3.x (see http://cx-freeze.sourceforge.net/)
* Windows: Microsoft Visual C++ 2010 x86 Redistributable Package Service Pack 1

##Hints and Notes

######Python under Linux x64

On Linux x64 system you need the **ia32libs** or the 64bit Runtime of Python 3.3.x.

######How to Install Python 3.3 on Ubuntu 13.04, 12.10 and 12.04

see http://linuxg.net/how-to-install-python-3-3-on-ubuntu-13-04-12-10-and-12-04/

##Build Instructions

Be sure that the dependencies have been installed correctly. Then start the build scripts.

On Windows systems

    git clone https://github.com/litixsoft/baboon-stack.git
    make.cmd

On Unix systems

	git clone https://github.com/litixsoft/baboon-stack.git
	./make.sh

Copy all content from **build/** to your **/baboonstack/bbs** folder. Include the files from **packages/[version]/[os]/**

# Author
[Litixsoft GmbH](http://www.litixsoft.de)

#License
Copyright (C) 2014 Litixsoft GmbH <info@litixsoft.de>
Licensed under the MIT license.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE. DEALINGS IN THE SOFTWARE.