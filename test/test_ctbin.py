#! /usr/bin/env python
# ==========================================================================
# This scripts performs unit tests for the ctbin module.
#
# Copyright (C) 2014-2016 Juergen Knoedlseder
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ==========================================================================
import gammalib
import ctools


# =========================== #
# Test class for ctbin module #
# =========================== #
class Test(gammalib.GPythonTestSuite):
    """
    Test class for ctbin module.
    """

    # Constructor
    def __init__(self):
        """
        Constructor.
        """
        # Call base class constructor
        gammalib.GPythonTestSuite.__init__(self)

        # Set members
        self._events_name = "data/crab_events.fits"

        # Return
        return

    # Set test functions
    def set(self):
        """
        Set all test functions.
        """
        # Set test name
        self.name("ctbin")

        # Append tests
        self.append(self._test_ctbin, "Test ctbin")

        # Return
        return

    # Test ctbin
    def _test_ctbin(self):
        """
        Test ctbin.
        """
        # Set-up ctbin
        bin = ctools.ctbin()
        bin["inobs"]    = self._events_name
        bin["outcube"]  = "cntmap.fits"
        bin["ebinalg"]  = "LOG"
        bin["emin"]     = 0.1
        bin["emax"]     = 100.0
        bin["enumbins"] = 20
        bin["nxpix"]    = 200
        bin["nypix"]    = 200
        bin["binsz"]    = 0.02
        bin["coordsys"] = "CEL"
        bin["proj"]     = "CAR"
        bin["xref"]     = 83.63
        bin["yref"]     = 22.01

        # Run ctbin tool
        bin.run()

        # Check content of observation and cube
        self._test_observation(bin, 5542)
        self._test_cube(bin.cube(), 5542)

        # Test copy constructor
        cpy_bin = bin.copy()

        # Check content of observation and cube
        self._test_observation(cpy_bin, 5542)
        self._test_cube(cpy_bin.cube(), 5542)

        # Run copy of ctbin tool again
        cpy_bin.run()

        # Check content of observation and cube. We expect now an empty
        # event cube as on input the observation is binned, and any binned
        # observation will be skipped, hence the counts cube should be
        # empty.
        self._test_observation(cpy_bin, 0)
        self._test_cube(cpy_bin.cube(), 0)

        # Clear and run copy of ctbin again
        #cpy_bin.clear()
        #cpy_bin.run()
#RuntimeError: *** ERROR in GXmlAttribute::value(std::string): Invalid XML attribute value: *** ERROR in GPythonTestSuite::test: <type 'exceptions.RuntimeError'>
#*** ERROR in GApplicationPars::operator[](std::string&): Invalid argument. Parameter "debug" has not been found in parameter file.
#Please specify a valid parameter name.

        # Save counts cube
        bin.save()

        # Load counts cube and check content.
        evt = gammalib.GCTAEventCube("cntmap.fits")
        self._test_cube(evt, 5542)

        # Prepare observation container for stacked analysis
        cta = gammalib.GCTAObservation(self._events_name)
        obs = gammalib.GObservations()
        cta.id("0001")
        obs.append(cta)
        cta.id("0002")
        obs.append(cta)
        cta.id("0003")
        obs.append(cta)

        # Set-up ctbin using an observation container
        bin = ctools.ctbin(obs)
        bin["outcube"]  = "cntmap.fits"
        bin["ebinalg"]  = "LOG"
        bin["emin"]     = 0.1
        bin["emax"]     = 100.0
        bin["enumbins"] = 20
        bin["nxpix"]    = 200
        bin["nypix"]    = 200
        bin["binsz"]    = 0.02
        bin["coordsys"] = "CEL"
        bin["proj"]     = "CAR"
        bin["xref"]     = 83.63
        bin["yref"]     = 22.01

        # Run ctbin tool
        bin.run()

        # Check content of observation and cube (need multiplier=3 since
        # three identical observations have been appended)
        self._test_observation(bin, 5542, multiplier=3)
        self._test_cube(bin.cube(), 5542, multiplier=3)

        # Set-up ctbin with invalid event file
        bin = ctools.ctbin()
        bin["inobs"]    = "event_file_that_does_not_exist.fits"
        bin["outcube"]  = "cntmap.fits"
        bin["ebinalg"]  = "LOG"
        bin["emin"]     = 0.1
        bin["emax"]     = 100.0
        bin["enumbins"] = 20
        bin["nxpix"]    = 200
        bin["nypix"]    = 200
        bin["binsz"]    = 0.02
        bin["coordsys"] = "CEL"
        bin["proj"]     = "CAR"
        bin["xref"]     = 83.63
        bin["yref"]     = 22.01

        # Run ctbin tool
        self.test_try("Run ctbin with invalid event file")
        try:
            bin.run()
            self.test_try_failure()
        except:
            self.test_try_success()

        # Return
        return

    # Check observation
    def _test_observation(self, ctbin, nevents, multiplier=1):
        """
        Test content of an observation.
        
        Args:
            ctbin:   ctbin instance
            nevents: Expected number of events

        Kwargs:
            multiplier: Observation multiplier
        """
        # Test observation container
        obs = gammalib.GCTAObservation(ctbin.obs()[0])
        pnt = obs.pointing()
        self.test_value(ctbin.obs().size(), 1,
                        "There is one observation")
        self.test_assert(obs.instrument() == "CTA",
                        "Observation is CTA observation")
        self.test_value(obs.ontime(), 1800.0*multiplier, 1.0e-6,
                        "Ontime is 1800 sec")
        self.test_value(obs.livetime(), 1710.0*multiplier, 1.0e-6,
                        "Livetime is 1710 sec")
        self.test_value(pnt.dir().ra_deg(), 83.63, 1.0e-6,
                        "Pointing Right Ascension is 83.63 deg")
        self.test_value(pnt.dir().dec_deg(), 22.01, 1.0e-6,
                        "Pointing Declination is 22.01 deg")

        # Test event cube
        self._test_cube(obs.events(), nevents, multiplier=multiplier)

        # Return
        return

    # Check event cube
    def _test_cube(self, cube, nevents, multiplier=1):
        """
        Test content of event cube."
        
        Args:
            cube:    Event cube
            nevents: Expected number of events.

        Kwargs:
            multiplier: Event number multiplier
        """
        # Test event cube
        self.test_value(cube.size(), 800000, "800000 event bins")
        self.test_value(cube.number(), nevents*multiplier,
                        str(nevents*multiplier)+" events")

        # Return
        return
