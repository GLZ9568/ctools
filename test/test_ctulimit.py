#! /usr/bin/env python
# ==========================================================================
# This scripts performs unit tests for the ctulimit tool.
#
# Copyright (C) 2015-2016 Michael Mayer
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
from testing import test


# ============================ #
# Test class for ctulimit tool #
# ============================ #
class Test(test):
    """
    Test class for ctulimit tool
    """
    # Constructor
    def __init__(self):
        """
        Constructor
        """
        # Call base class constructor
        test.__init__(self)

        # Return
        return

    # Set test functions
    def set(self):
        """
        Set all test functions
        """
        # Set test name
        self.name('ctulimit')

        # Append tests
        self.append(self._test_cmd, 'Test ctulimit on command line')
        self.append(self._test_python, 'Test ctulimit from Python')

        # Return
        return

    # Test ctulimit on command line
    def _test_cmd(self):
        """
        Test ctulimit on the command lines
        """
        # Set tool name
        ctulimit = self._tool('ctulimit')

        # Setup ctulimit command
        cmd = ctulimit+' inobs="'+self._events+'"'+ \
                       ' inmodel="'+self._model+'" srcname="Crab"'+ \
                       ' caldb="'+self._caldb+'" irf="'+self._irf+'"'+ \
                       ' logfile="ctulimit_cmd1.log" chatter=1'

        # Check if execution of wrong command fails
        self.test_assert(self._execute('command_that_does_not_exist') != 0,
             'Self test of test script')

        # Check if execution was successful
        self.test_assert(self._execute(cmd) == 0,
             'Check successful execution from command line')

        # Check result file
        self._check_result_file('ctulimit_cmd1.log')

        # Setup ctulimit command
        cmd = ctulimit+' inobs="event_file_that_does_not_exist.fits"'+ \
                       ' inmodel="'+self._model+'" srcname="Crab"'+ \
                       ' caldb="'+self._caldb+'" irf="'+self._irf+'"'+ \
                       ' logfile="ctulimit_cmd2.log" chatter=1'

        # Check if execution failed
        self.test_assert(self._execute(cmd) != 0,
             'Check invalid input file when executed from command line')

        # Return
        return

    # Test ctulimit from Python
    def _test_python(self):
        """
        Test ctulimit from Python
        """
        # Allocate ctulimit
        ulimit = ctools.ctulimit()

        # Check that empty ctulimit tool holds zero upper limits
        self.test_value(ulimit.diff_ulimit(), 0.0, 1.0e-23,
                        'Check differential upper limit')
        self.test_value(ulimit.flux_ulimit(), 0.0, 1.0e-17,
                        'Check upper limit on photon flux')
        self.test_value(ulimit.eflux_ulimit(), 0.0, 1.0e-16,
                        'Check upper limit on energy flux')

        # Check that saving does not nothing
        ulimit.logFileOpen()
        ulimit.save()

        # Check that clearing does not lead to an exception or segfault
        ulimit.clear()

        # Now set ctulimit parameters
        ulimit = ctools.ctulimit()
        ulimit['inobs']   = self._events
        ulimit['inmodel'] = self._model
        ulimit['srcname'] = 'Crab'
        ulimit['caldb']   = self._caldb
        ulimit['irf']     = self._irf
        ulimit['logfile'] = 'ctulimit_py1.log'
        ulimit['chatter'] = 2

        # Run ctulimit tool
        ulimit.logFileOpen()   # Make sure we get a log file
        ulimit.run()
        ulimit.save()

        # Check results
        self.test_value(ulimit.diff_ulimit(), 8.86803e-18, 1.0e-23,
                        'Check differential upper limit')
        self.test_value(ulimit.flux_ulimit(), 6.10509e-12, 1.0e-17,
                        'Check upper limit on photon flux')
        self.test_value(ulimit.eflux_ulimit(), 2.75669e-11, 1.0e-16,
                        'Check upper limit on energy flux')

        # Copy ctulimit tool
        cpy_ulimit = ulimit.copy()

        # Check results of copy
        self.test_value(cpy_ulimit.diff_ulimit(), 8.86803e-18, 1.0e-23,
                        'Check differential upper limit')
        self.test_value(cpy_ulimit.flux_ulimit(), 6.10509e-12, 1.0e-17,
                        'ulimit upper limit on photon flux')
        self.test_value(cpy_ulimit.eflux_ulimit(), 2.75669e-11, 1.0e-16,
                        'Check upper limit on energy flux')

        # Execute copy of ctulimit tool again, now with a higher chatter
        # level than before
        cpy_ulimit['logfile'] = 'ctulimit_py2.log'
        cpy_ulimit['chatter'] = 3
        cpy_ulimit.logFileOpen()  # Needed to get a new log file
        cpy_ulimit.execute()

        # Check results
        self.test_value(cpy_ulimit.diff_ulimit(), 8.86803e-18, 1.0e-23,
                        'Check differential upper limit')
        self.test_value(cpy_ulimit.flux_ulimit(), 6.10509e-12, 1.0e-17,
                        'ulimit upper limit on photon flux')
        self.test_value(cpy_ulimit.eflux_ulimit(), 2.75669e-11, 1.0e-16,
                        'Check upper limit on energy flux')

        # Now clear copy of ctulimit tool
        cpy_ulimit.clear()

        # Check that empty ctulimit tool holds zero upper limits
        self.test_value(cpy_ulimit.diff_ulimit(), 0.0, 1.0e-23,
                        'Check differential upper limit')
        self.test_value(cpy_ulimit.flux_ulimit(), 0.0, 1.0e-17,
                        'Check upper limit on photon flux')
        self.test_value(cpy_ulimit.eflux_ulimit(), 0.0, 1.0e-16,
                        'Check upper limit on energy flux')

        # Return
        return

    # Check result file
    def _check_result_file(self, filename):
        """
        Check result file
        """
        # Return
        return
