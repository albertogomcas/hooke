# Hooke(GUI) #

Hooke(GUI) is a GUI-only version of Hooke. The fact that all commands can be chosen from the GUI and do not need to be typed into the command line, provides a different user experience. This might be beneficial for some users.

## Installation ##
Download the latest SVN version and check the "illysam" branch is there ; to install that please follow the installation guidelines [here](HowToInstall.md). You don't need to install wxMPL to run Hooke(GUI). However, you need to install [ConfigObj](http://www.voidspace.org.uk/python/configobj.html) and [wxPropertyGrid](http://wxpropgrid.sourceforge.net/cgi-bin/index). Follow the installation instructions on the respective websites.
Unfortunately, there seem to be some issues with wxPropertyGrid on Linux, Mac OS X and other nix systems.

Hooke(GUI) has been developed and tested with this combination of libraries on Windows (XP, Vista, 7):

  * [Python](http://www.python.org): 2.6.4
  * [wxPython](http://www.wxpython.org): 2.8.10.1
  * [wxPropertyGrid](http://wxpropgrid.sourceforge.net/cgi-bin/index): 1.4.10
  * [matplotlib](http://matplotlib.sourceforge.net/): 0.99.1
  * [SciPy](http://www.scipy.org/): 0.7.1
  * [NumPy](http://www.numpy.org/): 1.4.0
  * [ConfigObj](http://www.voidspace.org.uk/python/configobj.html): 4.6.0

The program will probably work fine with other combinations as well. If you can make it work, please post your combination [here](ListKnownWorkingLibraries.md) indicating that you are using Hooke(GUI).

This version is not yet complete but provides the basic functionality required to do simple force curve filtering and autopeak analysis. Please create a new [issue](Issues.md) if you urgently need a feature that is not implemented.


## Interface ##
Starting Hooke(GUI) for the first time, you will see the central plot area with the current plot surrounded by the following windows (the F key toggles the visibility of the panel):

  1. Folders (F5)
  1. Playlists (F6)
  1. Commands (or Settings and commands) (F7)
  1. Properties (F8)
  1. Assistant (F9)
  1. Results (F10)
  1. Output (F11)
  1. Note (F12)

![http://nanoscience-dev.concordia.ca/custom/images/hooke/hooke%20gui%20screenshot.jpg](http://nanoscience-dev.concordia.ca/custom/images/hooke/hooke%20gui%20screenshot.jpg)

Initially, the window will be rather small in order to work with small screen resolutions. Adjust the size and position to your liking.

Above the windows you see the navigation toolbar to switch from one curve to another (next/previous).

### Plot area ###
The plot area can be customised by setting 'preferences' in the core plug-in.
  * hide\_curve\_extension: hides the curve extension in the title of the plot (and from the playlist in the playlists panel)
  * legend: show or hide the legend
  * use\_zero: display '0' instead of _e.g._ '0.00' on the axes
  * decimals (x\_decimals, y\_decimals): set the decimal places for the x and y axes
  * prefixes(x\_prefix, y\_prefix): set the prefix for the x and y axes

These are global settings. Individual plots can be customised with the same options (except hide\_curve\_extension) by setting 'preferences' in the plot plug-in.

### 1. Folders ###
Here you can navigate your file system and double click on a saved playlist to open it. You can change the initial folder by modifying 'workdir' in the 'preferences' (core plug-in).

### 2. Playlists ###
You can manage several playlists in this window. As the GUI is rather flexible, it is possible to display the curves from different playlists side by side to compare them (relatively handy when comparing different fit parameters). You can double-click a file in the playlist to display it in the plot area. Deleting entire playlists or single files can be accomplished by right-clicking and selecting 'Delete'.

### 3. Commands (or Settings and commands) ###
All available commands (_i.e._ do\_COMMAND) are listed under their corresponding plug-in. In order to see a plug-in and its commands, you have to edit _hooke.ini_ in the _config_ folder (plugins/PLUGINNAME = True). Selecting a plug-in or command will display the associated help in the Assistant window (see below). You can edit the properties of the selected command in the Properties window (see below) and click 'Execute' to run the selected command. If you do not need to modify any properties, you can also double-click a command to run it.

### 4. Properties ###
The properties for the command selected in the Commands window (see above) are displayed here. Edit the properties to your satisfaction (some need to be confirmed by hitting enter, this seems to be a problem in wxPropertyGrid) and click the 'Execute' button to run the selected command. Floating point values are limited to a certain number of decimals (limitation of wxPropertyGrid?) so be careful when using floating point values.

### 5. Assistant ###
Selecting a plug-in or command in the Commands window will display the associated help here. The help for the plug-in should give a general description of the plug-in. The help for a command should describe the properties available for this command and suggest reasonable default values if possible. Feel free to point out missing help content.

### 6. Results ###
The results from the 'autopeak' or 'multidistance' command are displayed here. Initially, all results are checked (i.e visible). If you want to hide a result, simply uncheck it. Hidden curves will not be exported either. You can only display one type of fit result (WLC, FJC, etc.) at a time and you can switch between result types (results plug-in - show\_results).

### 7. Output ###
The Output window serves as a log where pertinent information is displayed. If something does not work the way you expect it, have a look here to see if there is more information available.

### 8. Note ###
A note can be added to every curve: enter your note and click 'Update note'. With the copylog command (core plug-in) you can copy all the files with a note to a different folder.


## General remarks ##
Ignore the text on the Welcome tab. This tab is more like a proof of principle and will contain a short how-to in the future (once the howto is written).

Hooke(GUI) will remember the size and position of the main window.

You can arrange the panels any which way you like and save this arrangement as a perspective.

![http://nanoscience-dev.concordia.ca/custom/images/hooke/hooke%20gui%20screenshot%20perspective.jpg](http://nanoscience-dev.concordia.ca/custom/images/hooke/hooke%20gui%20screenshot%20perspective.jpg)

Hooke(GUI) will always start with the last used perspective and you can switch from one perspective to another by selecting a perspective from the perspectives menu. After deleting a perspective, the radio indicator in the perspectives menu disappears (known bug in wxPython). This is only a visual problem and does not affect anything else.

In order to pan the plot, zoom in and out and export the plot of your force curves, use the plot toolbar under the plot. A more detailed description is available on the [matplotlib website](http://matplotlib.sourceforge.net/users/navigation_toolbar.html).

## Some plug-ins and commands ##
  * replot (plot): replots the current force curve from scratch eliminating any secondary plots
  * fjc/fjcPEG/wlc (fit): do not use any of these commands directly, they are not implemented properly yet. However, the properties you set for these commands are used for the autopeak command
  * plotmanipulators (core): select the plotmanipulators you want to use and arrange them in the proper order
  * test (test): use this for testing purposes. You find do\_test in hooke.py
  * clear\_results (results): deletes all fitting results from the curve
  * show\_results (results): select which fitting results should be displayed on the plot
  * overlay (export): exports all retraction curves in a playlist on the same scale. This is achieved by determining the maximum x window and adding x(max) and x(min) to all curves that are shorter than the maximum x window. Make sure to filter your playlist before running this command!

## Basic analysis and autopeak ##
Please follow the steps for basic analysis described [here](BasicAnalysis.md). Instead of typing in the command at the command-line, select it in the Commands window, set your properties in the Properties window and click on 'Execute'.

The [autopeak](Brief_Autopeak_HowTo.md) tutorial is also applicable. In Hooke(GUI) you need to setup the type of fit you want to use: in the Properties of the autopeak command (autopeak plug-in) select wlc, fjc or fjcPEG from the dropdown list for the fit\_function.

If you run different fits (_e.g._ WLC and FJC) you can switch the display of the results with the show\_results command (results plug-in).

## Brief Plug-in/Properties tutorial ##
Have a look at the files in the _plugins_ folder. The python files contain the plotmanipulators (_i.e._ plotmanip\_NAME), commands (_i.e._ do\_COMMAND) and auxilliary methods. The ini files contain the information for the Properties window. You can already use a fair number of datatypes (_e.g._ integer, float, boolean, list, color, etc.) and more can be added. Be careful when using floats as there is a limit to the number of decimals (see above). The plotmanipulators and commands should read the properties directly from the ini file instead of having them passed to them as arguments. For the time being, accessor methods are located in hooke.py (_e.g._ GetBoolFromConfig()).
A more detailed description will be made available.