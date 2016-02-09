IN PROGRESS

Hooke works with a combined command line and graphic interface. Think of programs like RASMOL. The command line allows the user to issue commands about the set of curves he wants to analyze. The graphic interface, for now, shows the curves plot and allows basic interactions with it -depending also from variables and commands issued.

# Starting Hooke #
Open a terminal, go to the directory Hooke is installed and type python
hooke.py (You may need to give the full path for Python on Windows sys-
tems). If everything is OK, Hooke displays a nice splashscreen and starts.

Once Hooke is launched from the terminal window, you see a text like the following:

```
Starting Hooke.
Imported plugin fit
Imported plugin procplots
Imported plugin flatfilts
Imported plugin generalclamp
Imported plugin generalvclamp
Imported plugin massanalysis
Imported plugin macro
Imported driver picoforce
Imported driver hemingclamp
Imported driver csvdriver
Imported driver tutorialdriver

Warning: Invalid work directory.
This is Hooke, version 0.8.0 Seinei
(c) Massimo Sandal, 2006. Released under the GNU General Public License Version 2
Hooke is Free software.
----
hooke:
```

Hooke tells you that plugins and drivers have been loaded, and now you’re ready to go. You’re now at the Hooke command line. In the meantime, a splashscreen and a window with a dummy force curve should appear . At the command line, digit **help** or **?** to obtain a list of available commands.

```
hooke: ?
Documented commands (type help <topic>):
========================================
addtolist debug        exit     genlist  ls   notelog previous  set
cd         derivplot export     getlist  n    p       printlist size
contact    dir        flatfilt jump      next plateau pwd       subtplot
current    distance    force    loadlist note plot    savelist  wlc
Undocumented commands:
======================
help

hooke:
```


# Begin your analysis #

## Create a playlist ##
To start analyzing your curves, you ﬁrst have to build a _playlist_. The playlist is just an index of the force curve ﬁles you want to analyze. Imagine it as a music playlist (that’s why it is called a playlist), but made of data ﬁles instead of MP3 ﬁles.

Suppose you have 100 PicoForce curve ﬁles in your curves directory, starting from mycurve.000 and ending in mycurve.100 and you want to analyze them all.

You then can cd to the directory
```
hooke: cd c:\curves
```

Type **pwd** to check the directory is correct
```
      hooke: pwd
      c:\curves
      hooke:
```

You can list the ﬁles in the directory using ls or dir (they’re synonyms)
```
      hooke: ls
      [’mycurve.000’, ’mycurve.001’, ...
      ]
```

Now you are ready to generate the playlist. The command to use is **genlist**
```
hooke: genlist mycurve.*
```
You can also generate a playlist containing all what you ﬁnd in the directory by typing:
```
hooke: genlist c:\curves
```

If you want to select what curves to see, based on the ﬁlename, you can use [wildcards](http://en.wikipedia.org/wiki/Wildcard_character#Computing).

For example:
```
hooke: genlist mycurve.05*
```

will take only curves from mycurve.050 to mycurve.059.

Note that by using genlist you just generate the playlist in the local session.
To save your playlist to a ﬁle, thus avoiding to regenerate it, type:
```
hooke: savelist mylist
```

The list will be saved, in this example, in the ﬁle _mylist.hkp_. Hooke will add the extension .hkp to the playlist if you forget to. The .hkp ﬁle is an XML ﬁle you can read and edit with any text editor (i.e. Wordpad), if needed. If you want to load it, simply issue **loadlist mylist.hkp** or **loadlist mylist**, Hooke will add '.hkp' if necessary. This will load the saved playlist, similar to saving the playlist.

Generating the playlist, you should see the plot of the ﬁrst curve appearing. If, generating the playlist, you are including by chance a non-force curve file that Hooke cannot open, it should be (more or less) silently ignored. If Hooke gives an error, or does not plot anything, try to navigate forward, and see if the next curve is plotted. It is possible you spotted a corrupted file.

## Navigate the playlist ##
Now you can navigate through your playlist using the commands **next** and **previous** or, more easily, their aliases **n** and **p**. You don’t need to type **n** every time to run along a list of curves. If you press Return to an empty prompt, Hooke will repeat the last command you issued explicitly.

You can also navigate through the command history by using the up and down arrows.

When arriving at the last curve of your playlist, pressing **n** will wrap around to the first curve. Analogously, issuing **p** at the ﬁrst curve will jump to the last.

You can also **jump** to a given curve:

```
hooke: jump c:\curves\mycurve.123
```

but be careful to tell Hooke the full path to that curve, otherwise it will not ﬁnd it.


# Taking notes #
You can take notes about the curves you are looking at. Just type **note** followed by the text you want to append to that curve. Hooke will save the text in your current playlist and in an external log ﬁle. The output will look like this:

```
Notes taken at Sun Sep 17 20:42:07 2006
/home/cyclopia/work/tris/20060620a.041 |             This is a note
/home/cyclopia/work/tris/20060620a.207 |             This is another note
/home/cyclopia/work/tris/20060620a.286 |             This is a third one
```

The first time you type **note** in a session, Hooke will ask you for a filename of the log.

Usually curves you annotated are useful later. You can copy the curves you annotated to a different directory by using the **copylog** command.

```
hooke: copylog c:\nicecurves
```

will copy all curves you have annotated to the c:\nicecurves directory. Make sure that the directory already exists before doing that.

# Exporting curves #
You can export Hooke curves as images and as text columns. To export as images, issue the **export** command followed by the ﬁlename. Supported formats are PNG (raster) and EPS (Encapsulated Postscript, vectorial). The export format is determined by the filename extension, so **export foo.png** and **export foo.eps** will save a PNG and EPS file respectively.

To export as text, use the **txt** command, followed by the ﬁlename. The output
is a text ﬁle containing columns (first two are X and Y of extension , second
two are X and Y of retraction).

# Interacting with the plot #
## Measuring distances and forces ##
You can easily zoom in the plot by dragging a rectangle on it with the left mouse button. To zoom out, click the right mouse button. Sometimes by zoom ing in and out too much, you can lose the picture (this is probably a small bug in Matplotlib). Just type plot at the command line and the curve will be refreshed.

You can measure distances and forces directly in the plot. Just issue the command **distance**. You will be asked to click two points: do it. When you click a point, a blue dot should appear. When you click the second point, the distance (in nanometers) will apper on the command line. **force** works in the same way. You can use **delta** if you prefer, which gives meaningful values for every kind of graph (not only force curves). If you want to know the coordinates of a single point, use **point**.

Hooke automatically adjusts the position of the clicked point at the nearest point in the graph, so you will be always measuring distances and forces between points in the graph.

The commands **force** and **distance** are present in the generalvclamp.py plugin.

## Worm like chain and freely jointed chain fitting ##
You can measure by hand the parameters relative to a force peak using a worm-like chain fitting with the **fit** command. The command by default automatically finds the contact point, asks for two points delimiting the portion to fit, and performs a two-variable fit, with contour length and persistence length as output, with relative errors. If desired, one can use the _noauto_ option to manually click the contact point, and/or the _pl=`[`number`]`_ options to impose a specific persistence or kuhn length (in nanometers). You can choose which model to use with `set fit_function wlc` or `set fit_function fjc`.Please see the help of the **fit** command from the Hooke command line for details.

## Iterative multiple curve fitting and measuring ##
You can cycle through all your current playlist obtaining WLC fit, FJC fit, rupture force and slope (~loading rate) information from each curve using **multifit** command. The collected data can be saved in a text file for further analysis in your favourite spreadsheet or statistical program. If you want to check first if your parameters are suitable you can execute `multifit justone` to do the measurements only over current curve. See the help of **multifit** for more options.

## Fast curve reviewing and saving ##
When automatic routines are not good enough to filter your data, use **review** command to cycle through your playlist presenting ten curves in the same graph. You can then enter the numbers of the interesting curves and automatically save a copy of them into another directory.

# Variables #
You can set environment variables to inﬂuence the behaviour of Hooke. The command to use is **set**.

You can alter permanently the behaviour of Hooke by setting these variables in the ﬁle _hooke.conf_. This is a very simple XML ﬁle, just change the values
of the variables with an ASCII text editor (not Word or a word processor - on
Windows, Wordpad should work). Be careful in the correct XML syntax (which you should grasp very easily looking at the default configuration file) otherwise Hooke will crash nastily on the next startup.

See VariableList for help on individual variables.