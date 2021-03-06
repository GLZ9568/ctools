.. _start_unbinned:

Doing an unbinned analysis
--------------------------

  .. admonition:: What you will learn

     You will learn how to **adjust a parametrised model to the events without
     binning the data**.

     Gamma-ray events are rare, hence the counts cubes generated by
     :ref:`ctbin` may be sparsly populated, having many empty pixels, in
     particular at high energies. In that case it may be worth to
     analyse the events directly with an unbinned maximum likelihood
     analysis.

     An unbinned analysis is generally preferred over a binned analysis for
     short observation times (a few tens of hours) or if you want to assure
     that the analysis results are not biased by the selected binning. Also
     the fitting of a light or phase curve is only be possible with an
     unbinned maximum likelihood analysis
     (see :ref:`light curve <1dc_howto_ligthcurve>` and
     :ref:`phase curve <1dc_howto_phasecurve>` fitting).

An alternative analysis technique consists of working directly on the event
list without binning the events in a counts cube.
You do this with the :ref:`ctlike` tool as follows:

.. code-block:: bash

   $ ctlike
   Input event list, counts cube or observation definition XML file [selected_events.fits]
   Calibration database [prod2]
   Instrument response function [South_0.5h]
   Input model definition XML file [models.xml] $CTOOLS/share/models/crab.xml
   Output model definition XML file [crab_results.xml]

You will recognise that :ref:`ctlike` runs much faster in unbinned mode
compared to binned mode.
This is understandable as the selected event list contains
only 21991 events, while the binned counts cube you used before had
200 x 200 x 20 = 800000 bins. As unbinned maximum likelihood fitting loops
over the events (while binned maximum likelihood loops over the bins),
there are much less operations to perform in unbinned than in binned mode
(there is some additional overhead in unbinned mode that comes from
integrating the models over the region of interest, yet this is negligible
compared to the operations needed when looping over all pixels). So as long
as you work with small event lists, unbinned mode is faster (this
typically holds up to few tens of hours of observing time).
Unbinned :ref:`ctlike` should also be more precise as no binning is performed,
hence there is no loss of information due to histogramming.

Below you see the corresponding output from the ``ctlike.log`` file. The fitted
parameters are essentially identical to the ones found in binned mode.
The slight difference with respect to the binned analysis may be explained
by the different event sample that were used for the analysis: while
binned likelihood works on rectangular counts cubes, unbinned likelihood works
on circular event selection regions. It is thus not possible to select exactly
the same events for both analyses.

.. code-block:: none

   2017-08-08T20:56:27: +=================================+
   2017-08-08T20:56:27: | Maximum likelihood optimisation |
   2017-08-08T20:56:27: +=================================+
   2017-08-08T20:56:27:  >Iteration   0: -logL=140091.731, Lambda=1.0e-03
   2017-08-08T20:56:28:  >Iteration   1: -logL=140089.754, Lambda=1.0e-03, delta=1.977, step=1.0e+00, max(|grad|)=5.681267 [Index:3]
   2017-08-08T20:56:28:  >Iteration   2: -logL=140089.751, Lambda=1.0e-04, delta=0.003, step=1.0e+00, max(|grad|)=0.255879 [Index:3]
   2017-08-08T20:56:28:
   2017-08-08T20:56:28: +=========================================+
   2017-08-08T20:56:28: | Maximum likelihood optimisation results |
   2017-08-08T20:56:28: +=========================================+
   2017-08-08T20:56:28: === GOptimizerLM ===
   2017-08-08T20:56:28:  Optimized function value ..: 140089.751
   2017-08-08T20:56:28:  Absolute precision ........: 0.005
   2017-08-08T20:56:28:  Acceptable value decrease .: 2
   2017-08-08T20:56:28:  Optimization status .......: converged
   2017-08-08T20:56:28:  Number of parameters ......: 10
   2017-08-08T20:56:28:  Number of free parameters .: 4
   2017-08-08T20:56:28:  Number of iterations ......: 2
   2017-08-08T20:56:28:  Lambda ....................: 1e-05
   2017-08-08T20:56:28:  Maximum log likelihood ....: -140089.751
   2017-08-08T20:56:28:  Observed events  (Nobs) ...: 21991.000
   2017-08-08T20:56:28:  Predicted events (Npred) ..: 21990.996 (Nobs - Npred = 0.00358908515045187)
   2017-08-08T20:56:28: === GModels ===
   2017-08-08T20:56:28:  Number of models ..........: 2
   2017-08-08T20:56:28:  Number of parameters ......: 10
   2017-08-08T20:56:28: === GModelSky ===
   2017-08-08T20:56:28:  Name ......................: Crab
   2017-08-08T20:56:28:  Instruments ...............: all
   2017-08-08T20:56:28:  Instrument scale factors ..: unity
   2017-08-08T20:56:28:  Observation identifiers ...: all
   2017-08-08T20:56:28:  Model type ................: PointSource
   2017-08-08T20:56:28:  Model components ..........: "PointSource" * "PowerLaw" * "Constant"
   2017-08-08T20:56:28:  Number of parameters ......: 6
   2017-08-08T20:56:28:  Number of spatial par's ...: 2
   2017-08-08T20:56:28:   RA .......................: 83.6331 [-360,360] deg (fixed,scale=1)
   2017-08-08T20:56:28:   DEC ......................: 22.0145 [-90,90] deg (fixed,scale=1)
   2017-08-08T20:56:28:  Number of spectral par's ..: 3
   2017-08-08T20:56:28:   Prefactor ................: 5.69800719463692e-16 +/- 9.95311294944208e-18 [1e-23,1e-13] ph/cm2/s/MeV (free,scale=1e-16,gradient)
   2017-08-08T20:56:28:   Index ....................: -2.46101639180337 +/- 0.0145278326558106 [-0,-5]  (free,scale=-1,gradient)
   2017-08-08T20:56:28:   PivotEnergy ..............: 300000 [10000,1000000000] MeV (fixed,scale=1000000,gradient)
   2017-08-08T20:56:28:  Number of temporal par's ..: 1
   2017-08-08T20:56:28:   Normalization ............: 1 (relative value) (fixed,scale=1,gradient)
   2017-08-08T20:56:28: === GCTAModelIrfBackground ===
   2017-08-08T20:56:28:  Name ......................: CTABackgroundModel
   2017-08-08T20:56:28:  Instruments ...............: CTA
   2017-08-08T20:56:28:  Instrument scale factors ..: unity
   2017-08-08T20:56:28:  Observation identifiers ...: all
   2017-08-08T20:56:28:  Model type ................: "PowerLaw" * "Constant"
   2017-08-08T20:56:28:  Number of parameters ......: 4
   2017-08-08T20:56:28:  Number of spectral par's ..: 3
   2017-08-08T20:56:28:   Prefactor ................: 1.00310957843794 +/- 0.0134585839142799 [0.001,1000] ph/cm2/s/MeV (free,scale=1,gradient)
   2017-08-08T20:56:28:   Index ....................: 0.00814622034405194 +/- 0.00817635016295375 [-5,5]  (free,scale=1,gradient)
   2017-08-08T20:56:28:   PivotEnergy ..............: 1000000 [10000,1000000000] MeV (fixed,scale=1000000,gradient)
   2017-08-08T20:56:28:  Number of temporal par's ..: 1
   2017-08-08T20:56:28:   Normalization ............: 1 (relative value) (fixed,scale=1,gradient)

..

  .. note::

     Many tools or scripts can also be used in unbinned mode, including
     :ref:`csresmap`, :ref:`ctbutterfly` and :ref:`csspec` that were used
     earlier. It is sufficient to replace the input counts cube by an event
     list to activate unbinned mode for these tools.
