Only a small fraction of AFM-SMFS force curves contains interesting signals. We developed two simple but nonetheless useful filters that act on the whole data set, discarding curves likely devoid of interesting signals, thus greatly decreasing the time needed for data analysis.

## Flatfilt ##
Syntax:
flatfilt [min\_deviation](min_npks.md)

min\_npks = minmum number of points over the deviation
(default=4)

min\_deviation = minimum signal/noise ratio
(default=9)

If called without arguments, it uses default values, that should work most of the times.

**flatﬁlt**, simply recognizes curves that possess some kind of signiﬁcant feature
above the thermal noise. The ﬁlter cycles all the curves in the playlist. For any given curve:
  * A median window ﬁlter (window size = 7) is applied on the retracting curve
  * A difference vector, containing the Y difference between contiguous points, is calculated.
  * The number of points in the diﬀerence vector exceeding a user-deﬁned threshold is counted
  * If there are enough points exceeding the user-deﬁned threshold, then the curve is kept in the playlist, otherwise it is discarded.

This type of ﬁlter is of course very raw, and requires relatively conservative settings to safely avoid false negatives (that is, to avoid discarding interesting curves). Using it on the protein unfolding experiments described in (1) it has been found to reduce the data set to analyze by hand by 60-80%.


## Convfilt ##
Filters out flat (featureless) curves of the current playlist, creating a playlist containing only the curves with potential features.
> 
---

> Syntax:
> convfilt [min\_deviation](min_npks.md)

> min\_npks = minmum number of peaks
> (to set the default, see convfilt.conf file; SETCONV command)

> min\_deviation = minimum signal/noise ratio **in the convolution**
> (to set the default, see convfilt.conf file; SETCONV command)

> If called without arguments, it uses default values.


The second ﬁlter, **convﬁlt**, relies on automatic recognition of force peaks. Recognition
of peaks is based on a simple convolution algorithm that is an extreme but working simpli-
ﬁcation of the approach of Kasas et.al. (2). Again, the ﬁlter function cycles all curves in the playlist. For any given retracting curve:

  * The contact point is found and only data before the contact point is used
  * The data before the contact point is convoluted with an L-shaped vector that encodes the approximate L-shape that forced unfolding peaks show after the maximum.
  * The noise level of the convolution is calculated, eliminating the highest values (which are presumibly the spikes) until the noise seems to converge. The average value and absolute deviation of the noise is calculated.
  * Data points exceeding the user-deﬁned threshold of absolute deviation are counted. Usually this data will show up as “clusters” around a single force peak: each cluster is then reduced to a single data point. If there are enough points exceeding the user-deﬁned threshold, then the curve is kept in the playlist, otherwise it is discarded.

The convolution algorithm, with appropriate thresholds, usually recognizes peaks well more than 95% of the time. The ﬁlter based on it can reduce a SMFS dataset like the one in (3) to analyze by hand by about 80-90% (depending on the overall cleanliness of the data set). Thousands of curves can be automatically filtered this way in a few minutes on a standard PC, but the algorithm could still be optimized.

Parameters for peak recognition are set in the convfilt.conf file:

  * _seedouble_: (int) minimum number of points that separate two different peaks
  * _convolution_ : (list) the convolution vector
  * _positive_ : (0/1) decides if cutting the most positive or negative data points from the vector. Keep it at 0 unless you are a Hooke developer
  * _stable_ : (float) decides when the noise level of the convolution is converging. The logic is: we cut the most negative (or positive) data points until the absolute deviation becomes stable (it doesn't vary more than 0.005) or we have cut more than maxcut\*len(data) points.
  * _maxcut_ : (float from 0 to 1) the maximum fraction of points to cut to evaluate noise, even if it doesn't converge as wanted by _stable_ (to avoid 'eating' all the noise)
  * _minpeaks_ : (int) the minimum number of peaks we want to consider a curve "good"
  * _mindeviation_ : (float) the minimum number of absolute deviations from the noise we want from a convolution to consider the point a peak
  * _blindwindow_ : (float) the number of nm after the contact point where we do not look for peaks

## Fcfilt ##

Is a filtering command, similar to the previous ones, that works on force clamp curves. Its logic is very similar to 'flatfilt' for velocity clamp curves.

**Syntax: fcfilt maxretraction(nm) mindeviation(pN)**

WARNING - Only works if you set an appropriate fc\_interesting config variable (see below)!
WARNING - arguments are NOT optional at the moment!

For **Fcfilt** to work, the internal configuration variable **fc\_interesting** must have a non-zero value. Fcfilt will take into account only the portion of the curve specified via **fc\_interesting**, which can be modified with the **set** command.

Mandatory arguments are:
(1) the maximum plausible piezo retraction in NANOMETERS measured from the start of the pulling phase (i.e. usually the length of the protein) and
(2) the minimum force deviation threshold, in PICONEWTONS. If the constant-force signal deviates from the imposed force value more than this, an event is detected and the curve is non-empty.

As an example, suggested values for a typical (i27)8 experiment are respectively 200nm and 10-15 pN

For reference, the actual algorithm which decides whether a curve has some features in the interesting phase works as follows:

  * first, clip the interesting phase portion of the curve.
  * then, discard the first 20 milliseconds (this is due to a quirk of our hardware: the first few milliseconds after the pulling is started are somewhat noisy and could interfere with the filtering process).
  * now look at the zpiezo plot and note down when (if) retratcs more than **maxretraction** nm away from the first point.
  * clip off any data after this point, with an excess of 100 points (again, an hardware quirk)
  * if the remainder is less than 100 points, ditch the curve.
  * now look at the deflection plot and check if there are points more than **threshold** pN over the 'flat zone'.
  * if you find such points, bingo! you found a non-empty curve.

# Bibliography #
(1) M.Sandal et al. "Conformational equilibria in monomeric alpha synuclein at the single molecule level", PLOS Biology 6:e6 , (2008)

(2) S.Kasas et al. "Fuzzy logic algorithm to extract specific interaction forces from atomic force microscopy data" Rev. Sci. Instrum. 71:2082 (2000)

(3) M.Brucale et al. "Pathogenic mutations shift the equilibria of alpha-synuclein single molecules towards structured conformers." Chembiochem. 2009 Jan 5;10(1):176-83.