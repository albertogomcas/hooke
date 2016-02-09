IN PROGRESS

If you want to install Hooke plugins, see InstallPlugins.

# Requirements #

Hooke is known to work on Windows, Linux and MacOS X.

For other operating systems, it should work on all the platforms that support Python 2.5, Scipy, Numpy, Matplotlib and Wx (this should include most Unix systems and possibly a few other).

Hooke requires:
  * [Python](http://www.python.org) 2.5
  * [wxPython](http://www.wxpython.org) 2.8.x.x
  * [Numpy](http://numpy.scipy.org) 1.2.x (1.0.x if you are using Matplotlib 0.91.x,  probably)
  * [Scipy](http://www.scipy.org) >=0.6.x
  * [Matplotlib](http://matplotlib.sourceforge.net) =0.91.x and  [wxMPL](http://agni.phys.iit.edu/~kmcivor/wxmpl/) 1.2.9
  * OR [Matplotlib](http://matplotlib.sourceforge.net) >=0.98 and [wxMPL](http://agni.phys.iit.edu/~kmcivor/wxmpl/) >=1.3.1

All libraries are open source, free of charge and available on the Internet. A bundle with a working combination of libraries can be found in the downloads section http://code.google.com/p/hooke/downloads/list
The packages should be installed in the order in which they are mentioned above.

**Note: It IS important to check the cross-compatibility of the versions of the above.** In particular of the numpy/scipy/matplotlib combo , and remember to install them for the right version of Python. For your help, you can find here a ListKnownWorkingLibraries with combinations of libraries tested and known to work.

## Requirements on Linux ##
With all probability a suitable Python version is installed on your system. If in doubt, ﬁre up a command line prompt and digit ’python’.

The problem is a bit different for the other libraries. If you use a Linux or BSD flavour, the libraries (except wxMPL) can be probably found on the package
manager of your system. I don’t know for Solaris or other Unixen.

I personally usually install Python and wxPython from packages, and the other libs from source. Compiling and installing them from source is not hard if you are accustomed to  compile software packages on Unix, but it requires in turn a lot of dependencies. Prepare to have installed on your system at least (I am surely forgetting something) LAPACK, BLAS, PyGTK, libpng and Tk -both packages and most importantly their headers/development ﬁles (usually known as dev packages, on Debian systems). The numpy, scipy and matplotlib documentations online will help you through. If you have packages of the recent versions,  try them -they should work. WxMPL has no official packages as far as I know, but it’s the easiest to install, once you have wxpython and matplotlib installed. Just  follow the instructions in the package.

## Requirements on Windows ##

You should ﬁnd the required packages on the Internet as easy .EXE installers.
Just download them from the Internet (most are hosted on [sourceforge.net](http://sourceforge.net), but look for them in the links above) and install them in the correct order.

An alternative is to install Enthought Python, a distribution of Python for scientiﬁc computing that includes numpy, scipy and wxpython (plus another bunch of libraries and goodies). You will still need to install matplotlib and wxmpl, though. Keep in mind that wxmpl needs to be installed **from the Windows command line**.


# Installation #
Hooke still has no installer... but it does not need it essentially, since it's so simple. Once all the dependencies have been installed, just unzip the package and copy the Hooke folder in your favourite location.

It is advisable to put it in a folder where you have write access rights (es. your home folder)

A [distutils](http://www.python.org/community/sigs/current/distutils-sig/doc/) based installer is in the todo list.

## Installation notes for Windows ##
Download the required packages from their respective webs to get the latest version. Alternatively, you can get a bundle with all you need from our featured donwloads (http://code.google.com/p/hooke/downloads/list)
Install the required libraries in the following order: python, wxpython, maptplotlib, numpy, scipy and finally configobj and wxpropgrid (for Hooke GUI) or wxmpl (for the command line version).

In some systems numpy and scipy installers will complain about an invalid architecture option, in that case, you need to execute the installer from the command line `numpy-xxxx.exe /arch option` where option can be nosse, sse2, sse3. Safest (but worst performance) choice is nosse, although most computers manufactured after 2004 should support at least sse2.

Note: release notes of numpy and scipy say to use `/arch=option` however we could only make it work without the "=" sign.

## Installation notes for Linux ##
Ubuntu users can follow these instructions for installing Hooke (tested in Ubuntu 9.10 Karmic Koala)

  1. Open a console and type `sudo aptitude install python-wxgtk2.8 python-scipy python-numpy python-matplotlib`
  1. Download wxmpl from http://agni.phys.iit.edu/~kmcivor/wxmpl/
  1. Extract the tar.gz or .zip package and enter the newly created directory
  1. Type `sudo python setup.py install`

For HDF5 support (**only** Igor Pro users!)
  1. Download h5py and hdf5 support packages (when ubuntu 10.4 is available you probably can do this with apt-get/aptitude)
    * http://packages.ubuntu.com/lucid/libhdf5-serial-1.8.3 (or higher version)
    * http://packages.ubuntu.com/lucid/python-h5py
  1. Install manually the packages, open a console, move to the directory where you placed the .debs and type:
    * `sudo dpkg -i libhdf5-serial-**version**.deb`
    * `sudo dpkg -i python-h5py-**version**.deb`
## Installation notes for Mac OS X ##
to do