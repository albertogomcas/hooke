We will add new Q&As whenever new problems arise...

  * **Q: Hooke displays only a grey window with a tiny square pattern at the top left corner (on Windows)**
  * A: This is probably a small bug in the Windows version of the wx libraries. Simply resize the plot window and the default curve should appear.


  * **Q: At startup, Hooke crashes with a long error message that ends with _AttributeError: HookeCliPlugged instance has no attribute 'find\_contact\_point'_**
  * A: Most probably there is some problem with your SciPy version. Using SciPy 0.5.x instead of SciPy 0.6 leads to this crash (which is due to the fact that SciPy 0.5 does not contain the ODR libraries that we use for curve fitting). Check your libraries version.

  * **Q: At startup, Hooke displays a long list of lines like _GnomePrintCupsPlugin-Message: The ppd file for the CUPS printer foo could not be loaded._ (on Linux/Unix)**
  * A: This is not a problem of Hooke but of the interplay between your Gnome install and the wx library. It is just a warning that can safely be ignored.

  * **Q: At startup, Hooke crashes with errors like "import numpy.ma as ma ImportError: No module named ma"**
  * A: Check if your NumPy and your matplotlib libraries are of mutually compatible versions.