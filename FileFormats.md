We need full support for most force spectroscopy data files. Please help us by:
  * giving us example data files
  * giving us specifications of data files
  * testing code and reporting bugs

# Supported file formats #

  * **Veeco Picoforce (6.12)**
> > drivers: picoforce.py ; picoforcealt.py (depends on your version of Picoforce)


> Support for 6.13 and above is possibly faulty (see [bug 0010](http://code.google.com/p/hooke/issues/detail?id=10) )


  * **JPK** (experimental support; needs testing!) (old versions)
> > drivers: jpk.py

  * **MFP 1D** (indirect) (needs testing)
> > drivers: mfp1dexport.py
> > Still _indirect_ support, requires Igor export scripts provided by Rolf Schmidt et al. available in the subversion reporsitory. See Mfp1dSupport for the details.

  * **MFP 3D** (needs testing!)
> > These files are now directly supported by the mfp3d driver. Note that "flatten" manipulator usually distorts the curve, it is recommended to deactivate it `set flatten 0`
> > The old way of importing MFP3D data [HDF5](http://code.google.com/p/hooke/wiki/HDF5) is not recommended any more.

  * Simple **comma-separated values**
> > drivers: csv.py
> > Basically little more than a proof of concept, but one can build useful drivers on top of it.

# To do file formats #

  * Asylum MFP 1D
  * Anything else...