#! /usr/bin/env python
# ==========================================================================
# This scripts performs unit tests for the ctcubemask tool.
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
from testing import test


# ============================== #
# Test class for ctcubemask tool #
# ============================== #
class Test(test):
    """
    Test class for ctcubemask tool
    """
    # Constructor
    def __init__(self):
        """
        Constructor
        """
        # Call base class constructor
        test.__init__(self)

        # Set members
        self._exclusion = self._datadir + '/exclusion.reg'

        # Return
        return

    # Set test functions
    def set(self):
        """
        Set all test functions
        """
        # Set test name
        self.name('ctcubemask')

        # Append tests
        self.append(self._test_cmd, 'Test ctcubemask on command line')
        self.append(self._test_python, 'Test ctcubemask from Python')

        # Return
        return

    # Test ctcubemask on command line
    def _test_cmd(self):
        """
        Test ctcubemask on the command line
        """
        # Set tool name
        ctcubemask = self._tool('ctcubemask')

        # Setup ctcubemask command
        cmd = ctcubemask+' inobs="'+self._cntcube+'"'+ \
                         ' regfile="'+self._exclusion+'"'+ \
                         ' outcube="ctcubemask_cmd1.fits"'+ \
                         ' ra=83.63 dec=22.01 rad=2.0'+ \
                         ' emin=0.1 emax=100.0'+ \
                         ' logfile="ctcubemask_cmd1.log" chatter=1'

        # Check if execution of wrong command fails
        self.test_assert(self._execute('command_that_does_not_exist') != 0,
             'Self test of test script')

        # Check if execution was successful
        self.test_assert(self._execute(cmd) == 0,
             'Check successful execution from command line')

        # Check result file
        self._check_result_file('ctcubemask_cmd1.fits')

        # Setup ctcubemask command
        cmd = ctcubemask+' inobs="counts_cube_that_does_not_exist.fits"'+ \
                         ' regfile="'+self._exclusion+'"'+ \
                         ' outcube="ctcubemask_cmd2.fits"'+ \
                         ' ra=83.63 dec=22.01 rad=2.0'+ \
                         ' emin=0.1 emax=100.0'+ \
                         ' logfile="ctcubemask_cmd2.log" chatter=2'

        # Check if execution failed
        self.test_assert(self._execute(cmd) != 0,
             'Check invalid input file when executed from command line')

        # Return
        return

    # Test ctcubemask from Python
    def _test_python(self):
        """
        Test ctcubemask from Python
        """
        # Set-up ctcubemask
        mask = ctools.ctcubemask()
        mask['inobs']   = self._cntcube
        mask['regfile'] = self._exclusion
        mask['ra']      = 83.63
        mask['dec']     = 22.01
        mask['rad']     = 2.0
        mask['emin']    = 0.1
        mask['emax']    = 100.0
        mask['outcube'] = 'ctcubemask_py1.fits'
        mask['logfile'] = 'ctcubemask_py1.log'
        mask['chatter'] = 2

        # Run ctcubemask tool
        mask.logFileOpen()   # Make sure we get a log file
        mask.run()
        mask.save()

        # Check result file
        self._check_result_file('ctcubemask_py1.fits')

        # Set-up ctcubemask without exclusion regions
        mask = ctools.ctcubemask()
        mask['inobs']   = self._cntcube
        mask['regfile'] = 'NONE'
        mask['ra']      = 83.63
        mask['dec']     = 22.01
        mask['rad']     = 3.0
        mask['emin']    = 0.1
        mask['emax']    = 100.0
        mask['outcube'] = 'ctcubemask_py2.fits'
        mask['logfile'] = 'ctcubemask_py2.log'
        mask['chatter'] = 3
        mask['publish'] = True

        # Execute ctcubemask tool
        mask.logFileOpen()   # Make sure we get a log file
        mask.execute()

        # Check result file
        self._check_result_file('ctcubemask_py2.fits', events=5542)

        # Copy ctcubemask tool and execute copy
        cpy_mask = mask
        cpy_mask['outcube'] = 'ctcubemask_py3.fits'
        cpy_mask['logfile'] = 'ctcubemask_py3.log'
        cpy_mask['chatter']  = 4
        cpy_mask.execute()

        # Check result file
        self._check_result_file('ctcubemask_py3.fits', events=5542)

        # Clear ctcubemask tool
        mask.clear()

        # TODO: Do some test after clearing

        # Return
        return

    # Check result file
    def _check_result_file(self, filename, events=4921):
        """
        Check result file
        """
        # Load counts cube
        cube = gammalib.GCTAEventCube(filename)

        # Check counts cube
        self.test_value(cube.size(), 800000, 'Check for number of cube bins')
        self.test_value(cube.number(), events, 'Check for number of events')

        # Return
        return
