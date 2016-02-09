The AUTOPEAK command can speed up the quantitative analysis of a given curve considerably. When invoked, AUTOPEAK performs automatically a fixed sequence of measurements on the current curve and outputs the relevant parameters. When no custom parameters are utilized, the sequence of measurement steps looks like this:

**(1) Find peak positions**

**(2) Determine the baseline value**

**(3) Find contact point**

**(4) Perform WLC and linear fits on the peaks found previously**

**(5) Ask user acceptance of the performed fits**

**(6) Output fitted values for each peak (rupture force, contour length, persistence length, linear slope at rupture, errors of the fits)**

Each step is customizable with several variables and is described in detail below. The general syntax of the AUTOPEAK command is as follows:

```
autopeak [noauto] [reclick] [rebase] [usepoints] [pl=value] [t=value]
```

# How to customize the analysis #

## (0) Decide what function to use ##
In Hooke latest revisions you can choose the elasticity function to use to fit your peaks. The relevant variable is called FIT\_FUNCTION and you can set it this way

```
set fit_function wlc
```

if you want a worm-like chain model of entropic elasticity or

```
set fit_function fjc
```

if you prefer a freely jointed chain model.
If you don't know what this means, it probably means that you want WLC (the default). The documentation below assumes that we're using WLC, but it makes no difference to it if you're using WLC instead of FJC (it may or may not make a difference to your data though)

## (1) Finding Peaks ##

First of all, **autopeak** tries to recognize the peaks present in a curve, using the same convolution algorithm that can also be invoked with the **peaks** command. The convolution algorithm can be customized with the **setconv** command, and these settings will also be used by **autopeak**. It is often useful to try different convolution settings using the **peaks** command, trying to find a setting that is a bit on the generous side (i.e. it finds peaks in excess to the ‘true’ ones, see below).

The relevant settings are:

_mindeviation_ : Number of standard deviations above the convolution noise. The higher the parameter, the less peaks are found; the lower the parameter, the more peaks are found.

_seedouble_ : Minimum distance to count two peaks as separate peaks in nm. If two peaks occur at less than _seedouble_ nanometers, they are counted as a single peak.

_blindwindow_ : Zone after the contact point that we ignore, in nm (to avoid measuring non-specific adhesion).

_convolution_ : The actual convolution vector. Do not touch this unless you REALLY know what you're doing.


## (2) Determining the Baseline Value ##

**autopeak** needs a zero force reference in order to measure the rupture forces of the peaks and to estimate a contact point for the curve. There are several possible ways to do this, and you can choose a certain way by using optional arguments with the **autopeak** command, or by changing global variables with the **set** command.

If no optional argument is given to **autopeak**, the baseline will be estimated by looking at a portion of the curve that is further away from the surface than the position of the last peak found in the previous step (see Finding Peaks above). Once the peak position is found, two numbers are needed to identify the region used to estimate the baseline value: the distance between the last peak and the start of this region (stored in the AUTO\_RIGHT\_BASELINE variable, in nanometers) and the width of the region (stored in the AUTO\_LEFT\_BASELINE variable, also in nanometers). Both variables can be customized with the **set** command. The mean value of the force in the specified region is taken as the zero force baseline reference.

The completely automated method just described above is the default option. It is also possible to use a semi-automated and a fully manual method for calculating the baseline. These modes can be selected by setting the BASELINE\_CLICKS variable with the **set** command. When BASELINE\_CLICKS is 0 (default value), baseline estimation requires no manual clicks and proceeds exactly as described above. BASELINE\_CLICKS can also be set to either 1 or 2. If BASELINE\_CLICKS is set to 1, Hooke will ask the user to click on the curve once, and this point replaces the AUTO\_RIGHT\_BASELINE value (the width of the region will still be defined by AUTO\_LEFT\_BASELINE). If instead BASELINE\_CLICKS is set to 2, both boundaries of the region will need to be selected by mouse clicks.

The calculated baseline will be used for all subsequent measurements performed on the current curve. However, if the optional argument _rebase_ is added to the AUTOPEAK command, the calculation will be performed anew, according to the current relevant settings (i.e. the variables mentioned above).

Finally, peaks are automatically excluded from the measurement if their persistence length falls out of a certain range. The range is defined by the AUTO\_MIN\_P and AUTO\_MAX\_P variables, in nanometers. If in some curve, the **peaks** command finds a peak that **autopeak** does not find, check with the **wlc** command if the persistence length falls out of the range.

## (3) Finding Contact Point ##

After having determined the baseline value, **autopeak** estimates a plausible contact point by finding the intersection point of two segments: the horizontal baseline segment (y=baseline value) and a linear fit of the near-vertical hookean contact region. Again, this completely automatic estimation can be overridden by using optional arguments with the **autopeak** command. If the NOAUTO argument is used, the user will be asked to specify the contact point manually (with a single mouse click).

In either case (automated or manual contact point determination), the found contact point will be used for the subsequent measurements performed on the current curve. However, if the optional argument _reclick_ is added to the AUTOPEAK command, the user will be asked to specify the contact point anew, the latter contact point replacing the former.

## (4) Performing fits on the Peaks ##

WLC functions originating from the contact point will be fitted on each peak previously spotted by **autopeak** in this curve (during step 1 above). A region will be defined for each peak, and the WLC will be fitted only taking into account the experimental points comprised in this region. If no custom arguments are added, the region has a fixed width, and the outmost point of the region relative to the contact point (i.e. “leftmost” on the screen) is the peak itself. The width of the region is stored in the two variables AUTO\_FIT\_NM and AUTO\_FIT\_POINTS, which can be modified with the **set** command. The former specifies the width of the fit region in nanometers, the second in absolute number of points. The addition of the optional argument USEPOINTS to the **autopeak** command will toggle which of the two variables will be used (unsurprisingly, AUTO\_FIT\_POINTS will be used only when the USEPOINTS argument is used).

The WLC equations used for the fit itself have two free parameters, namely contour length and persistence length of the pulled object. If no optional arguments are given, both parameters are optimized simultaneously. Alternatively, the optional argument _pl=X_ can be used, where X is the persistence length (in nanometers) that will be used for the fit. In this latter case, the fit will use only one variable.

The optional argument _T=X_ will change the temperature parameter in the WLC equation used for the fit (unit measure is K). The variable TEMPERATURE can also be set with the **set** command to obtain the same result.

A simple linear fit will also be performed on the peaks, broadly following the same procedure outlined above. In this case, the width of the fit region is defined by the AUTO\_SLOPE\_SPAN variable, given in this case in absolute number of points.

## (5) Ask User Acceptance of the Performed Fits ##

The WLC plots will then be superimposed to the curve to allow the user a visual qualitative estimate of the individual fits. Each successive peak will be numbered progressively from 0 onwards, 0 being the peak closest to contact point. A prompt will ask the user which of the WLC fits should be discarded:

```
Peaks to ignore (0,1...n from contact point, return to take all)
N to discard measurement
```

If N is entered at the prompt, all the current measurements will be discarded and not sent to output (see below).

## (6) Output Fitted Values for each Peak ##

Finally, all the values found in the analysis will be outputted both to the screen, and a user-specified file. When you first issue the **autopeak** command during a Hooke session, it will ask for a filename. If you are giving the filename of an existing file, **autopeak** will resume it and append measurements to it. If you are giving a new filename, it will create the file and append to it until you close the current session.

This is an example file outputted by **autopeak**. The analysis was performed with fixed persistence length (_pl=0.35_).

```
Analysis started Wed Dec 03 12:15:52 2008
----------------------------------------
; Contour length (nm)  ;  Persistence length (nm) ;  Max.Force (pN)  ;  Slope (N/m) ;  Sigma contour (nm) ; Sigma persistence (nm)
C:\Documents and Settings\utente\Desktop\20081202_4s4_a53t_tris10mM\12021851.010
 ; 160.564221142 ; 0.35 ; 92.943924517 ; 0.000659914294585 ; 1.27733711603 ; 0
 ; 178.833860291 ; 0.35 ; 89.2893347657 ; 0.00245173346948 ; 0.794763991469 ; 0
 ; 194.700016668 ; 0.35 ; 114.064388156 ; 0.00693404929585 ; 0.697728046589 ; 0
 ; 217.30422854 ; 0.35 ; 90.2438505041 ; 0.00134107226685 ; 0.973225283369 ; 0
 ; 233.262875717 ; 0.35 ; 116.068927395 ; 0.00581200503053 ; 0.631216922346 ; 0
 ; 274.316183901 ; 0.35 ; 104.30958757 ; 0.00488501967784 ; 1.19537932592 ; 0
 ; 293.188681122 ; 0.35 ; 113.182010518 ; 0.000697144280399 ; 0.938287901289 ; 0
 ; 311.519448229 ; 0.35 ; 107.954090148 ; 0.00210364767408 ; 1.0687159539 ; 0
 ; 330.988522726 ; 0.35 ; 110.683694879 ; 0.00735012001617 ; 1.40534064588 ; 0
 ; 352.327864108 ; 0.35 ; 111.100552256 ; 0.00645107279789 ; 1.54929108347 ; 0
 ; 373.000688786 ; 0.35 ; 97.2267134089 ; 0.0017840342437 ; 1.9135653495 ; 0
C:\Documents and Settings\utente\Desktop\20081202_4s4_a53t_tris10mM\m20081202a.078
 ; 31.2871233813 ; 0.35 ; 126.129204238 ; 0.0165706776113 ; 0.136459650445 ; 0
 ; 50.9548186357 ; 0.35 ; 122.158845919 ; 0.0197902225442 ; 0.0957803329259 ; 0
 ; 69.7031062115 ; 0.35 ; 140.627667872 ; 0.0150915826621 ; 0.127321919971 ; 0
 ; 87.0751582659 ; 0.35 ; 115.537297076 ; 0.00670653611372 ; 0.19634809617 ; 0
C:\Documents and Settings\utente\Desktop\20081202_4s4_a53t_tris10mM\m20081202a.083
 ; 95.581325965 ; 0.35 ; 118.910051952 ; 0.00578145504649 ; 0.464774887986 ; 0
 ; 116.490799302 ; 0.35 ; 125.88473764 ; 0.00814442097178 ; 0.34508997912 ; 0
 ; 136.047127219 ; 0.35 ; 130.107681756 ; 0.00852028572519 ; 0.295966224306 ; 0
 ; 157.058547746 ; 0.35 ; 104.575755405 ; 0.0065195205728 ; 0.629766769923 ; 0
 ; 177.62392358 ; 0.35 ; 109.683389205 ; 0.00404904642569 ; 0.666914249141 ; 0
 ; 195.035675533 ; 0.35 ; 117.478460089 ; 0.00703595940494 ; 0.554322188624 ; 0
 ; 215.240322445 ; 0.35 ; 124.956106355 ; 0.00469715428104 ; 0.69708108878 ; 0

[...]

```