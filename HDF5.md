**This method is not necessary any more, MFP3D files are now understood by Hooke**

Users of Asylum AFM obtain their data files in .ibw format, currently not understood by Hooke. This method provides an alternative to [MFP1DSupport](http://code.google.com/p/hooke/wiki/Mfp1dSupport) in case it is not working for you.

# Requirements #
  * Igor Pro 5.04 or later with MFP3D installed (tested with a fresh install of MFP3D 080501+0207 in Igor Pro 6.04)
  * HDF5 export activated in Igor Pro
  * h5py python extension (python-h5py)
  * libhdf5-serial

The python script has been tested in linux (Ubuntu 9.10 Karmic Koala), the required packages are not available in karmic repositories, but can be found in lucid (future Ubuntu 10.4).

HDF5 is a vendor independent standard, as long as Igor/MFP3D keeps calling the parameters in the same way (i.e. `SpringConstant`) any version (5.04 or later) should work.

In any given path `IP` stands for `your IgorPro directory` (tipically `C:\Program Files\WaveMetrics\Igor Pro Folder\`), substitute accordingly.


# Activating HDF5 export in Igor Pro #
You only need to do this step once.
This is a quick-install guide, more details can be found in `IP\More Extensions\File Loaders\HDF5 Help.ihf`

  1. Make a shortcut of `IP\More Extensions\File Loaders\HDF5.xop` into `IP\Igor Extensions\` folder
  1. Make a shortcut of `IP\WaveMetrics Procedures\File Input Output\HDF5 Browser.ipf` into `IP\Igor Procedures` folder
  1. Start MFP3D
  1. Click _Data->Load Waves->Packages->Install HDF5 Package_. A pop-up should tell you the package was installed.
  1. Close MFP3D and start it again
  1. Click _Data->Load Waves->New HDF5 Browser_

If everything was all right you should have a big window named HDF5Browser

# Exporting your files to HDF5 format #

We will store the data of many force curves in a single HDF5 file.

  1. Start MFP3D
  1. In the Master Panel click Review, to open the Master Force Panel
  1. In the Master Force Panel click Load Curves, find the directory where you have your curves and click That's It
  1. Wait some seconds for the curves to be loaded
  1. Uncheck everything in Axis subpanel (you dont want to make graphs of 1000+ curves!)
  1. Click the top level branch of the directory or force map you want to export. As it is usually a big number of curves a windows will ask if you are serious. Providing you did previous step you can say yes and you can load few thousand curves without making your computer nuts. Keep an eye in the "Displayed plots" count. How many curves you can export at a time will likely depend on your memory. I have tried 1000 on a computer with 1GB RAM without much pain. Wait till the PC finishes thinking (2-3 min). A blank Force Review Graph window should appear when it is done.
  1. Open a HDF5Browser (_Data->Load Waves->New HDF5 Browser_)
  1. Click Create HDF5 File, select location and name as you like
  1. Now click Save Data Folder button
  1. In the new window that opens you can select which data folder you want to save. Make sure that both Save Groups Recursive and Include Igor Attributes boxes are checked and click Save button.
  1. Wait a few seconds for the files to be saved then click Done to close this window.
  1. **(a)** Close HDF5 file, you are finished. **(b)** Alternatively, go back to the Master Force Panel, unclick the forces you selected before (frees memory). Click new ones.
  1. Go back to the HDF5Browser and repeat **steps 9-11**.
  1. You can repeat **steps 12b-13** until you save all the curves you want.
  1. Close HDF5 file.

It is also possible to reopen a file to add more data, just make sure that you are not opening it as _read only_ in the HDF5Browser.

# Converting HDF5 file to hooke readable files #

On a command line type: `python h5export.py file.h5`