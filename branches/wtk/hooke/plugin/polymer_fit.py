# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2010 Alberto Gomez-Casado
#                         Fabrizio Benedetti
#                         Massimo Sandal <devicerandom@gmail.com>
#                         W. Trevor King <wking@drexel.edu>
#
# This file is part of Hooke.
#
# Hooke is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Hooke is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General
# Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Hooke.  If not, see
# <http://www.gnu.org/licenses/>.

"""The ``polymer_fit`` module proviews :class:`PolymerFitPlugin` and
serveral associated :class:`hooke.command.Command`\s for Fitting
velocity-clamp data to various polymer models (WLC, FJC, etc.).
"""

import copy
import Queue
import StringIO
import sys

import numpy
from scipy.optimize import newton

from ..command import Command, Argument, Failure
from ..config import Setting
from ..curve import Data
from ..plugin import Plugin
from ..util.fit import PoorFit, ModelFitter
from ..util.callback import is_iterable
from .curve import CurveArgument
from .vclamp import scale


kB = 1.3806503e-23  # Joules/Kelvin


def coth(z):
    """Hyperbolic cotangent.

    Examples
    --------
    >>> coth(1.19967874)  # doctest: +ELLIPSIS
    1.199678...

    Notes
    -----
    From `MathWorld`_

    .. math::
      \coth(z) \equiv \frac{\exp(z) + \exp(-z)}{\exp(z) - \exp(-z)}
         = \frac{1}{\tanh(z)}

    .. _MathWorld:
      http://mathworld.wolfram.com/HyperbolicCotangent.html
    """
    return 1.0/numpy.tanh(z)

def arccoth(z):
    """Inverse hyperbolic cotangent.

    Examples
    --------
    >>> arccoth(1.19967874)  # doctest: +ELLIPSIS
    1.199678...
    >>> arccoth(coth(numpy.pi))  # doctest: +ELLIPSIS
    3.1415...

    Notes
    -----
    Inverting from the :func:`definition <coth>`.

    .. math::
      z \equiv \atanh\left( \frac{1}{\coth(z)} \right)
    """
    return numpy.arctanh(1.0/z)

def Langevin(z):
    """Langevin function.

    Examples
    --------
    >>> Langevin(numpy.pi)  # doctest: +ELLIPSIS
    0.685...

    Notes
    -----
    From `Wikipedia`_ or Hatfield [#]_

    .. math::
      L(z) \equiv \coth(z) - \frac{1}{z}

    .. _Wikipedia:
      http://en.wikipedia.org/wiki/Brillouin_and_Langevin_functions#Langevin_Function

    .. [#]: J.W. Hatfield and S.R. Quake
      "Dynamic Properties of an Extended Polymer in Solution."
      Phys. Rev. Lett. 1999.
      doi: `10.1103/PhysRevLett.82.3548 <http://dx.doi.org/10.1103/PhysRevLett.82.3548>`
    """
    return coth(z) - 1.0/z

def inverse_Langevin(z, extreme=1.0 - 1e-8):
    """Inverse Langevin function.

    Parameters
    ----------
    z : float or array_like
        object whose inverse Langevin will be returned
    extreme : float
        value (close to one) for which we assume the inverse is +/-
        infinity.  This avoids problems with Newton-Raphson
        convergence in regions with low slope.

    Examples
    --------
    >>> inverse_Langevin(Langevin(numpy.pi))  # doctest: +ELLIPSIS
    3.14159...
    >>> inverse_Langevin(Langevin(numpy.array([1,2,3])))  # doctest: +ELLIPSIS
    array([ 1.,  2.,  3.])

    Notes
    -----
    We approximate the inverse Langevin via Newton's method
    (:func:`scipy.optimize.newton`).  For the starting point, we take
    the first three terms from the Taylor series (from `Wikipedia`_).

    .. math::
      L^{-1}(z) = 3z + \frac{9}{5}z^3 + \frac{297}{175}z^5 + \dots

    .. _Wikipedia:
      http://en.wikipedia.org/wiki/Brillouin_and_Langevin_functions#Langevin_Function
    """
    if is_iterable(z):
        ret = numpy.ndarray(shape=z.shape, dtype=z.dtype)
        for i,z_i in enumerate(z):
            ret[i] = inverse_Langevin(z_i)
        return ret
    if z > extreme:
        return numpy.inf
    elif z < -extreme:
        return -numpy.inf
    # Catch stdout since sometimes the newton function prints exit
    # messages to stdout, e.g. "Tolerance of %s reached".
    stdout = sys.stdout
    tmp_stdout = StringIO.StringIO()
    sys.stdout = tmp_stdout
    ret = newton(func=lambda x: Langevin(x)-z,
                  x0=3*z + 9./5.*z**3 + 297./175.*z**5,)
    sys.stdout = stdout
    output = tmp_stdout.getvalue()
    return ret

def FJC_fn(x_data, T, L, a):
    """The freely jointed chain model.

    Parameters
    ----------
    x_data : array_like
        x values for which the WLC tension should be calculated.
    T : float
        temperature in Kelvin.
    L : float
        contour length in meters.
    a : float
        Kuhn length in meters.

    Returns
    -------
    f_data : array
        `F(x_data)`.

    Examples
    --------
    >>> FJC_fn(numpy.array([1e-9, 5e-9, 10e-9], dtype=numpy.float),
    ...        T=300, L=15e-9, a=2.5e-10) # doctest: +ELLIPSIS
    array([  3.322...-12,   1.78...e-11,   4.889...e-11])

    Notes
    -----
    The freely jointed chain model is

    .. math::
      F(x) = \frac{k_B T}{a} L^{-1}\left( \frac{x}{L} \right)

    where :math:`L^{-1}` is the :func:`inverse_Langevin`, :math:`a` is
    the Kuhn length, and :math:`L` is the contour length [#]_.  For
    the inverse formulation (:math:`x(F)`), see Ray and Akhremitchev [#]_.


    .. [#]: J.W. Hatfield and S.R. Quake
      "Dynamic Properties of an Extended Polymer in Solution."
      Phys. Rev. Lett. 1999.
      doi: `10.1103/PhysRevLett.82.3548 <http://dx.doi.org/10.1103/PhysRevLett.82.3548>`

    .. [#] C. Ray and B.B. Akhremitchev.
      `"Fitting Force Curves by the Extended Freely Jointed Chain Model" <http://www.chem.duke.edu/~boris/research/force_spectroscopy/fit_efjc.pdf>`
    """
    return kB*T / a * inverse_Langevin(x_data/L)

class FJC (ModelFitter):
    """Fit the data to a freely jointed chain.

    Examples
    --------
    Generate some example data

    >>> T = 300  # Kelvin
    >>> L = 35e-9  # meters
    >>> a = 2.5e-10  # meters
    >>> x_data = numpy.linspace(10e-9, 30e-9, num=20)
    >>> d_data = FJC_fn(x_data, T=T, L=L, a=a)

    Fit the example data with a two-parameter fit (`L` and `a`).

    >>> info = {
    ...     'temperature (K)': T,
    ...     'x data (m)': x_data,
    ...     }
    >>> model = FJC(d_data, info=info, rescale=True)
    >>> outqueue = Queue.Queue()
    >>> Lp,a = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> model.L(Lp)  # doctest: +ELLIPSIS
    3.500...e-08
    >>> a  # doctest: +ELLIPSIS
    2.499...e-10

    Fit the example data with a one-parameter fit (`L`).  We introduce
    some error in our fixed Kuhn length for fun.

    >>> info['Kuhn length (m)'] = 2*a
    >>> model = FJC(d_data, info=info, rescale=True)
    >>> Lp = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> model.L(Lp)  # doctest: +ELLIPSIS
    3.199...e-08
    """
    def Lp(self, L):
        """To avoid invalid values of `L`, we reparametrize with `Lp`.

        Parameters
        ----------
        L : float
            contour length in meters

        Returns
        -------
        Lp : float
            rescaled version of `L`.

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = FJC(data=x_data, info={'x data (m)':x_data})
        >>> model.Lp(20e-9)  # doctest: +ELLIPSIS
        -inf
        >>> model.Lp(19e-9)  # doctest: +ELLIPSIS
        nan
        >>> model.Lp(21e-9)  # doctest: +ELLIPSIS
        -2.99...
        >>> model.Lp(100e-9)  # doctest: +ELLIPSIS
        1.386...

        Notes
        -----
        The rescaling is designed to limit `L` to values strictly
        greater than the maximum `x` data value, so we use

        .. math::
            L = [\exp(L_p))+1] * x_\text{max}

        which has the inverse

        .. math::
            L_p = \ln(L/x_\text{max}-1)

        This will obviously effect the interpretation of the fit's covariance matrix.
        """
        x_max = self.info['x data (m)'].max()
        return numpy.log(L/x_max - 1)

    def L(self, Lp):
        """Inverse of :meth:`Lp`.

        Parameters
        ----------
        Lp : float
            rescaled version of `L`

        Returns
        -------
        L : float
            contour length in meters

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = FJC(data=x_data, info={'x data (m)':x_data})
        >>> model.L(model.Lp(21e-9))  # doctest: +ELLIPSIS
        2.100...e-08
        >>> model.L(model.Lp(100e-9))  # doctest: +ELLIPSIS
        9.999...e-08
        """
        x_max = self.info['x data (m)'].max()
        return (numpy.exp(Lp)+1)*x_max

    def model(self, params):
        """Extract the relavant arguments and use :func:`FJC_fn`.

        Parameters
        ----------
        params : list of floats
            `[Lp, a]`, where the presence of `a` is optional.
        """
        # setup convenient aliases
        T = self.info['temperature (K)']
        x_data = self.info['x data (m)']
        L = self.L(params[0])
        if len(params) > 1:
            a = abs(params[1])
        else:
            a = self.info['Kuhn length (m)']
        # compute model data
        self._model_data[:] = FJC_fn(x_data, T, L, a)
        return self._model_data

    def guess_initial_params(self, outqueue=None):
        """Guess initial fitting parameters.

        Returns
        -------
        Lp : float
            A guess at the reparameterized contour length in meters.
        a : float (optional)
            A guess at the Kuhn length in meters.  If `.info` has a
            setting for `'Kuhn length (m)'`, `a` is not returned.
        """
        x_max = self.info['x data (m)'].max()
        a_given = 'Kuhn length (m)' in self.info
        if a_given:
            a = self.info['Kuhn length (m)']
        else:
            a = x_max / 10.0
        L = 1.5 * x_max
        Lp = self.Lp(L)
        if a_given:
            return [Lp]
        return [Lp, a]

    def guess_scale(self, params, outqueue=None):
        """Guess parameter scales.

        Returns
        -------
        Lp_scale : float
            A guess at the reparameterized contour length scale in meters.
        a_scale : float (optional)
            A guess at the Kuhn length in meters.  If the length of
            `params` is less than 2, `a_scale` is not returned.
        """
        Lp_scale = 1.0
        if len(params) == 1:
            return [Lp_scale]
        return [Lp_scale] + [x/10.0 for x in params[1:]]


def inverse_FJC_PEG_fn(F_data, T=300, N=1, k=150., Lp=3.58e-10, Lh=2.8e-10, dG=3., a=7e-10):
    """Inverse poly(ethylene-glycol) adjusted extended FJC model.

    Examples
    --------
    >>> kwargs = {'T':300.0, 'N':1, 'k':150.0, 'Lp':3.58e-10, 'Lh':2.8e-10,
    ...           'dG':3.0, 'a':7e-10}
    >>> inverse_FJC_PEG_fn(F_data=200e-12, **kwargs)  # doctest: +ELLIPSIS
    3.487...e-10

    Notes
    -----
    The function is that proposed by F. Oesterhelt, et al. [#]_.

    .. math::
      x(F) = N_\text{S} \cdot \left[
        \left(
            \frac{L_\text{planar}}{
                  \exp\left(-\Delta G/k_B T\right) + 1}
            + \frac{L_\text{helical}}{
                  \exp\left(+\Delta G/k_B T\right) + 1}
          \right) \cdot \left(
            \coth\left(\frac{Fa}{k_B T}\right)
            - \frac{k_B T}{Fa}
          \right)
        + \frac{F}{K_\text{S}}

    where :math:`N_\text{S}` is the number of segments,
    :math:`K_\text{S}` is the segment elasticicty,
    :math:`L_\text{planar}` is the ttt contour length,
    :math:`L_\text{helical}` is the ttg contour length,
    :math:`\Delta G` is the Gibbs free energy difference
     :math:`G_\text{planar}-G_\text{helical}`,
    :math:`a` is the Kuhn length,
    and :math:`F` is the chain tension.

    .. [#]: F. Oesterhelt, M. Rief, and H.E. Gaub.
      "Single molecule force spectroscopy by AFM indicates helical
      structure of poly(ethylene-glycol) in water."
      New Journal of Physics. 1999.
      doi: `10.1088/1367-2630/1/1/006 <http://dx.doi.org/10.1088/1367-2630/1/1/006>`
      (section 4.2)
    """
    kBT = kB * T
    g = (dG - F_data*(Lp-Lh)) / kBT
    z = F_data*a/kBT
    return N * ((Lp/(numpy.exp(-g)+1) + Lh/(numpy.exp(+g)+1)) * (coth(z)-1./z)
                + F_data/k)

def FJC_PEG_fn(x_data, T, N, k, Lp, Lh, dG, a):
    """Poly(ethylene-glycol) adjusted extended FJC model.

    Parameters
    ----------
    z : float or array_like
        object whose inverse Langevin will be returned
    extreme : float
        value (close to one) for which we assume the inverse is +/-
        infinity.  This avoids problems with Newton-Raphson
        convergence in regions with low slope.

    Examples
    --------
    >>> kwargs = {'T':300.0, 'N':1, 'k':150.0, 'Lp':3.58e-10, 'Lh':2.8e-10,
    ...           'dG':3.0, 'a':7e-10}
    >>> FJC_PEG_fn(inverse_FJC_PEG_fn(1e-11, **kwargs), **kwargs)  # doctest: +ELLIPSIS
    9.999...e-12
    >>> FJC_PEG_fn(inverse_FJC_PEG_fn(3.4e-10, **kwargs), **kwargs)  # doctest: +ELLIPSIS
    3.400...e-10
    >>> FJC_PEG_fn(numpy.array([1e-10,2e-10,3e-10]), **kwargs)  # doctest: +ELLIPSIS
    array([  5.207...e-12,   1.257...e-11,   3.636...e-11])
    >>> kwargs['N'] = 123
    >>> FJC_PEG_fn(numpy.array([1e-8,2e-8,3e-8]), **kwargs)  # doctest: +ELLIPSIS
    array([  4.160...e-12,   9.302...e-12,   1.830...e-11])

    Notes
    -----
    We approximate the PEG adjusted eFJC via Newton's method
    (:func:`scipy.optimize.newton`).  For the starting point, we use
    the standard FJC function with an averaged contour length.
    """
    kwargs = {'T':T, 'N':N, 'k':k, 'Lp':Lp, 'Lh':Lh, 'dG':dG, 'a':a}
    if is_iterable(x_data):
        ret = numpy.ndarray(shape=x_data.shape, dtype=x_data.dtype)
        for i,x in enumerate(x_data):
            ret[i] = FJC_PEG_fn(x, **kwargs)
        return ret
    if x_data == 0:
        return 0
    # Approximate with the simple FJC_fn()
    guess = numpy.inf
    L = N*max(Lp, Lh)
    while guess == numpy.inf:
        guess = FJC_fn(x_data, T=T, L=L, a=a)
        L *= 2.0

    fn = lambda f: inverse_FJC_PEG_fn(guess*abs(f), **kwargs) - x_data
    ret = guess*abs(newton(func=fn, x0=1.0))
    return ret

class FJC_PEG (ModelFitter):
    """Fit the data to an poly(ethylene-glycol) adjusted extended FJC.

    Examples
    -------- 
    Generate some example data

    >>> kwargs = {'T':300.0, 'N':123, 'k':150.0, 'Lp':3.58e-10, 'Lh':2.8e-10,
    ...           'dG':3.0, 'a':7e-10}
    >>> x_data = numpy.linspace(10e-9, 30e-9, num=20)
    >>> d_data = FJC_PEG_fn(x_data, **kwargs)

    Fit the example data with a two-parameter fit (`N` and `a`).

    >>> info = {
    ...     'temperature (K)': kwargs['T'],
    ...     'x data (m)': x_data,
    ...     'section elasticity (N/m)': kwargs['k'],
    ...     'planar section length (m)': kwargs['Lp'],
    ...     'helical section length (m)': kwargs['Lh'],
    ...     'Gibbs free energy difference (Gp - Gh) (kBT)': kwargs['dG'],
    ...     }
    >>> model = FJC_PEG(d_data, info=info, rescale=True)
    >>> outqueue = Queue.Queue()
    >>> Nr,a = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> model.L(Nr)  # doctest: +ELLIPSIS
    122.999...
    >>> a  # doctest: +ELLIPSIS
    6.999...e-10

    Fit the example data with a one-parameter fit (`N`).  We introduce
    some error in our fixed Kuhn length for fun.

    >>> info['Kuhn length (m)'] = 2*kwargs['a']
    >>> model = FJC_PEG(d_data, info=info, rescale=True)
    >>> Nr = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> model.L(Nr)  # doctest: +ELLIPSIS
    96.931...
    """
    def Lr(self, L):
        """To avoid invalid values of `L`, we reparametrize with `Lr`.

        Parameters
        ----------
        L : float
            contour length in meters

        Returns
        -------
        Lr : float
            rescaled version of `L`.

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = FJC_PEG(data=x_data, info={'x data (m)':x_data})
        >>> model.Lr(20e-9)  # doctest: +ELLIPSIS
        0.0
        >>> model.Lr(19e-9)  # doctest: +ELLIPSIS
        -0.0512...
        >>> model.Lr(21e-9)  # doctest: +ELLIPSIS
        0.0487...
        >>> model.Lr(100e-9)  # doctest: +ELLIPSIS
        1.609...

        Notes
        -----
        The rescaling is designed to limit `L` to values strictly
        greater than zero, so we use

        .. math::
            L = \exp(L_p) * x_\text{max}

        which has the inverse

        .. math::
            L_p = \ln(L/x_\text{max})

        This will obviously effect the interpretation of the fit's covariance matrix.
        """
        x_max = self.info['x data (m)'].max()
        return numpy.log(L/x_max)

    def L(self, Lr):
        """Inverse of :meth:`Lr`.

        Parameters
        ----------
        Lr : float
            rescaled version of `L`

        Returns
        -------
        L : float
            contour length in meters

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = FJC_PEG(data=x_data, info={'x data (m)':x_data})
        >>> model.L(model.Lr(21e-9))  # doctest: +ELLIPSIS
        2.100...e-08
        >>> model.L(model.Lr(100e-9))  # doctest: +ELLIPSIS
        9.999...e-08
        """
        x_max = self.info['x data (m)'].max()
        return numpy.exp(Lr)*x_max

    def _kwargs(self):
        return {
            'T': self.info['temperature (K)'],
            'k': self.info['section elasticity (N/m)'],
            'Lp': self.info['planar section length (m)'],
            'Lh': self.info['helical section length (m)'],
            'dG': self.info['Gibbs free energy difference (Gp - Gh) (kBT)'],
            }

    def model(self, params):
        """Extract the relavant arguments and use :func:`FJC_PEG_fn`.

        Parameters
        ----------
        params : list of floats
            `[N, a]`, where the presence of `a` is optional.
        """
        # setup convenient aliases
        T = self.info['temperature (K)']
        x_data = self.info['x data (m)']
        N = self.L(params[0])
        if len(params) > 1:
            a = abs(params[1])
        else:
            a = self.info['Kuhn length (m)']
        kwargs = self._kwargs()
        # compute model data
        self._model_data[:] = FJC_PEG_fn(x_data, N=N, a=a, **kwargs)
        return self._model_data

    def guess_initial_params(self, outqueue=None):
        """Guess initial fitting parameters.

        Returns
        -------
        N : float
            A guess at the section count.
        a : float (optional)
            A guess at the Kuhn length in meters.  If `.info` has a
            setting for `'Kuhn length (m)'`, `a` is not returned.
        """
        x_max = self.info['x data (m)'].max()
        a_given = 'Kuhn length (m)' in self.info
        if a_given:
            a = self.info['Kuhn length (m)']
        else:
            a = x_max / 10.0
        f_max = self._data.max()
        kwargs = self._kwargs()
        kwargs['a'] = a
        x_section = inverse_FJC_PEG_fn(F_data=f_max, **kwargs)
        N = x_max / x_section;
        Nr = self.Lr(N)
        if a_given:
            return [Nr]
        return [Nr, a]

    def guess_scale(self, params, outqueue=None):
        """Guess parameter scales.

        Returns
        -------
        N_scale : float
            A guess at the section count scale in meters.
        a_scale : float (optional)
            A guess at the Kuhn length in meters.  If the length of
            `params` is less than 2, `a_scale` is not returned.
        """
        return [x/10.0 for x in params]


def WLC_fn(x_data, T, L, p):
    """The worm like chain interpolation model.

    Parameters
    ----------
    x_data : array_like
        x values for which the WLC tension should be calculated.
    T : float
        temperature in Kelvin.
    L : float
        contour length in meters.
    p : float
        persistence length in meters.

    Returns
    -------
    f_data : array
        `F(x_data)`.

    Examples
    --------
    >>> WLC_fn(numpy.array([1e-9, 5e-9, 10e-9], dtype=numpy.float),
    ...        T=300, L=15e-9, p=2.5e-10) # doctest: +ELLIPSIS
    array([  1.717...e-12,   1.070...e-11,   4.418...e-11])

    Notes
    -----
    The function is the simple polynomial worm like chain
    interpolation forumula proposed by C. Bustamante, et al. [#]_.

    .. math::
      F(x) = \frac{k_B T}{p} \left[
        \frac{1}{4}\left( \frac{1}{(1-x/L)^2} - 1 \right)
        + \frac{x}{L}
                             \right]

    .. [#] C. Bustamante, J.F. Marko, E.D. Siggia, and S.Smith.
    "Entropic elasticity of lambda-phage DNA."
    Science. 1994.
    doi: `10.1126/science.8079175 <http://dx.doi.org/10.1126/science.8079175>`
    """
    a = kB * T / p
    scaled_data = x_data / L
    return a * (0.25*((1-scaled_data)**-2 - 1) + scaled_data)

class WLC (ModelFitter):
    """Fit the data to a worm like chain.

    Examples
    --------
    Generate some example data

    >>> T = 300  # Kelvin
    >>> L = 35e-9  # meters
    >>> p = 2.5e-10  # meters
    >>> x_data = numpy.linspace(10e-9, 30e-9, num=20)
    >>> d_data = WLC_fn(x_data, T=T, L=L, p=p)

    Fit the example data with a two-parameter fit (`L` and `p`).

    >>> info = {
    ...     'temperature (K)': T,
    ...     'x data (m)': x_data,
    ...     }
    >>> model = WLC(d_data, info=info, rescale=True)
    >>> outqueue = Queue.Queue()
    >>> Lp,p = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> model.L(Lp)  # doctest: +ELLIPSIS
    3.500...e-08
    >>> p  # doctest: +ELLIPSIS
    2.500...e-10

    Fit the example data with a one-parameter fit (`L`).  We introduce
    some error in our fixed persistence length for fun.

    >>> info['persistence length (m)'] = 2*p
    >>> model = WLC(d_data, info=info, rescale=True)
    >>> Lp = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> model.L(Lp)  # doctest: +ELLIPSIS
    3.318...e-08
    """
    def Lp(self, L):
        """To avoid invalid values of `L`, we reparametrize with `Lp`.

        Parameters
        ----------
        L : float
            contour length in meters

        Returns
        -------
        Lp : float
            rescaled version of `L`.

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = WLC(data=x_data, info={'x data (m)':x_data})
        >>> model.Lp(20e-9)  # doctest: +ELLIPSIS
        -inf
        >>> model.Lp(19e-9)  # doctest: +ELLIPSIS
        nan
        >>> model.Lp(21e-9)  # doctest: +ELLIPSIS
        -2.99...
        >>> model.Lp(100e-9)  # doctest: +ELLIPSIS
        1.386...

        Notes
        -----
        The rescaling is designed to limit `L` to values strictly
        greater than the maximum `x` data value, so we use

        .. math::
            L = [\exp(L_p))+1] * x_\text{max}

        which has the inverse

        .. math::
            L_p = \ln(L/x_\text{max}-1)

        This will obviously effect the interpretation of the fit's covariance matrix.
        """
        x_max = self.info['x data (m)'].max()
        return numpy.log(L/x_max - 1)

    def L(self, Lp):
        """Inverse of :meth:`Lp`.

        Parameters
        ----------
        Lp : float
            rescaled version of `L`

        Returns
        -------
        L : float
            contour length in meters

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = WLC(data=x_data, info={'x data (m)':x_data})
        >>> model.L(model.Lp(21e-9))  # doctest: +ELLIPSIS
        2.100...e-08
        >>> model.L(model.Lp(100e-9))  # doctest: +ELLIPSIS
        9.999...e-08
        """
        x_max = self.info['x data (m)'].max()
        return (numpy.exp(Lp)+1)*x_max

    def model(self, params):
        """Extract the relavant arguments and use :func:`WLC_fn`.

        Parameters
        ----------
        params : list of floats
            `[Lp, p]`, where the presence of `p` is optional.
        """
        # setup convenient aliases
        T = self.info['temperature (K)']
        x_data = self.info['x data (m)']
        L = self.L(params[0])
        if len(params) > 1:
            p = abs(params[1])
        else:
            p = self.info['persistence length (m)']
        # compute model data
        self._model_data[:] = WLC_fn(x_data, T, L, p)
        return self._model_data

    def guess_initial_params(self, outqueue=None):
        """Guess initial fitting parameters.

        Returns
        -------
        Lp : float
            A guess at the reparameterized contour length in meters.
        p : float (optional)
            A guess at the persistence length in meters.  If `.info`
            has a setting for `'persistence length (m)'`, `p` is not
            returned.
        """
        x_max = self.info['x data (m)'].max()
        p_given = 'persistence length (m)' in self.info
        if p_given:
            p = self.info['persistence length (m)']
        else:
            p = x_max / 10.0
        L = 1.5 * x_max
        Lp = self.Lp(L)
        if p_given:
            return [Lp]
        return [Lp, p]

    def guess_scale(self, params, outqueue=None):
        """Guess parameter scales.

        Returns
        -------
        Lp_scale : float
            A guess at the reparameterized contour length scale in meters.
        p_scale : float (optional)
            A guess at the persistence length in meters.  If the
            length of `params` is less than 2, `p_scale` is not
            returned.
        """
        Lp_scale = 1.0
        if len(params) == 1:
            return [Lp_scale]
        return [Lp_scale] + [x/10.0 for x in params[1:]]


class PolymerFitPlugin (Plugin):
    """Polymer model (WLC, FJC, etc.) fitting.
    """
    def __init__(self):
        super(PolymerFitPlugin, self).__init__(name='polymer_fit')
        self._commands = [PolymerFitCommand(self),]

    def dependencies(self):
        return ['vclamp']

    def default_settings(self):
        return [
            Setting(section=self.setting_section, help=self.__doc__),
            Setting(section=self.setting_section,
                    option='polymer model',
                    value='WLC',
                    help="Select the default polymer model for 'polymer fit'.  See the documentation for descriptions of available algorithms."),
            Setting(section=self.setting_section,
                    option='FJC Kuhn length',
                    value=4e-10, type='float',
                    help='Kuhn length in meters'),
            Setting(section=self.setting_section,
                    option='FJC-PEG Kuhn length',
                    value=4e-10, type='float',
                    help='Kuhn length in meters'),
            Setting(section=self.setting_section,
                    option='FJC-PEG elasticity',
                    value=150.0, type='float',
                    help='Elasticity of a PEG segment in Newtons per meter.'),
            Setting(section=self.setting_section,
                    option='FJC-PEG delta G',
                    value=3.0, type='float',
                    help='Gibbs free energy difference between trans-trans-trans (ttt) and trans-trans-gauche (ttg) PEG states in units of kBT.'),
            Setting(section=self.setting_section,
                    option='FJC-PEG L_helical',
                    value=2.8e-10, type='float',
                    help='Contour length of PEG in the ttg state.'),
            Setting(section=self.setting_section,
                    option='FJC-PEG L_planar',
                    value=3.58e-10, type='float',
                    help='Contour length of PEG in the ttt state.'),
            Setting(section=self.setting_section,
                    option='WLC persistence length',
                    value=4e-10, type='float',
                    help='Persistence length in meters'),
            ]


class PolymerFitCommand (Command):
    """Polymer model (WLC, FJC, etc.) fitting.

    Fits an entropic elasticity function to a given chunk of the
    curve.  Fit quality compares the residual with the thermal noise
    (a good fit should be 1 or less).

    Because the models are complicated and varied, you should
    configure the command by setting configuration options instead of
    using command arguments.  TODO: argument_to_setting()
    """
    def __init__(self, plugin):
        super(PolymerFitCommand, self).__init__(
            name='polymer fit',
            arguments=[
                CurveArgument,
                Argument(name='block', aliases=['set'], type='int', default=0,
                         help="""
Data block for which the fit should be calculated.  For an
approach/retract force curve, `0` selects the approaching curve and
`1` selects the retracting curve.
""".strip()),
                Argument(name='bounds', type='point', optional=False, count=2,
                         help="""
Indicies of points bounding the selected data.
""".strip()),
                ],
            help=self.__doc__, plugin=plugin)

    def _run(self, hooke, inqueue, outqueue, params):
        scale(hooke, params['curve'], params['block'])  # TODO: is autoscaling a good idea? (explicit is better than implicit)
        data = params['curve'].data[params['block']]
        # HACK? rely on params['curve'] being bound to the local hooke
        # playlist (i.e. not a copy, as you would get by passing a
        # curve through the queue).  Ugh.  Stupid queues.  As an
        # alternative, we could pass lookup information through the
        # queue...
        model = self.plugin.config['polymer model']
        new = Data((data.shape[0], data.shape[1]+1), dtype=data.dtype)
        new.info = copy.deepcopy(data.info)
        new[:,:-1] = data
        new.info['columns'].append('%s tension (N)' % model)  # TODO: WLC fit for each peak, etc.
        z_data = data[:,data.info['columns'].index(
                'cantilever adjusted extension (m)')]
        d_data = data[:,data.info['columns'].index('deflection (N)')]
        start,stop = params['bounds']
        tension_data,ps = self.fit_polymer_model(
            params['curve'], z_data, d_data, start, stop, outqueue)
        new.info['%s polymer fit parameters' % model] = ps
        new[:,-1] = tension_data
        params['curve'].data[params['block']] = new

    def fit_polymer_model(self, curve, z_data, d_data, start, stop,
                          outqueue=None):
        """Railyard for the `fit_*_model` family.

        Uses the `polymer model` configuration setting to call the
        appropriate backend algorithm.
        """
        fn = getattr(self, 'fit_%s_model'
                     % self.plugin.config['polymer model'].replace('-','_'))
        return fn(curve, z_data, d_data, start, stop, outqueue)

    def fit_FJC_model(self, curve, z_data, d_data, start, stop,
                      outqueue=None):
        """Fit the data with :class:`FJC`.
        """
        info = {
            'temperature (K)': self.plugin.config['temperature'],
            'x data (m)': z_data[start:stop],
            }
        if True:  # TODO: optionally free persistence length
            info['Kuhn length (m)'] = (
                self.plugin.config['FJC Kuhn length'])
        model = FJC(d_data[start:stop], info=info, rescale=True)
        queue = Queue.Queue()
        params = model.fit(outqueue=queue)
        if True:  # TODO: if Kuhn length fixed
            params = [params]
            a = info['Kuhn length (m)']
        else:
            a = params[1]
        Lp = params[0]
        L = model.L(Lp)
        T = info['temperature (K)']
        fit_info = queue.get(block=False)
        mask = numpy.zeros(z_data.shape, dtype=numpy.bool)
        mask[start:stop] = True
        return [FJC_fn(z_data, T=T, L=L, a=a) * mask,
                fit_info]

    def fit_FJC_PEG_model(self, curve, z_data, d_data, start, stop,
                          outqueue=None):
        """Fit the data with :class:`FJC_PEG`.
        """
        info = {
            'temperature (K)': self.plugin.config['temperature'],
            'x data (m)': z_data[start:stop],
            # TODO: more info
            }
        if True:  # TODO: optionally free persistence length
            info['Kuhn length (m)'] = (
                self.plugin.config['FJC Kuhn length'])
        model = FJC(d_data[start:stop], info=info, rescale=True)
        queue = Queue.Queue()
        params = model.fit(outqueue=queue)
        if True:  # TODO: if Kuhn length fixed
            params = [params]
            a = info['Kuhn length (m)']
        else:
            a = params[1]
        Nr = params[0]
        N = model.L(Nr)
        T = info['temperature (K)']
        fit_info = queue.get(block=False)
        mask = numpy.zeros(z_data.shape, dtype=numpy.bool)
        mask[start:stop] = True
        return [FJC_PEG_fn(z_data, **kwargs) * mask,
                fit_info]

    def fit_WLC_model(self, curve, z_data, d_data, start, stop,
                      outqueue=None):
        """Fit the data with :class:`WLC`.
        """
        info = {
            'temperature (K)': self.plugin.config['temperature'],
            'x data (m)': z_data[start:stop],
            }
        if True:  # TODO: optionally free persistence length
            info['persistence length (m)'] = (
                self.plugin.config['WLC persistence length'])
        model = WLC(d_data[start:stop], info=info, rescale=True)
        queue = Queue.Queue()
        params = model.fit(outqueue=queue)
        if True:  # TODO: if persistence length fixed
            params = [params]
            p = info['persistence length (m)']
        else:
            p = params[1]
        Lp = params[0]
        L = model.L(Lp)
        T = info['temperature (K)']
        fit_info = queue.get(block=False)
        mask = numpy.zeros(z_data.shape, dtype=numpy.bool)
        mask[start:stop] = True
        return [WLC_fn(z_data, T=T, L=L, p=p) * mask,
                fit_info]


# TODO:
# def dist2fit(self):
#     '''Calculates the average distance from data to fit, scaled by
#     the standard deviation of the free cantilever area (thermal
#     noise).
#     '''