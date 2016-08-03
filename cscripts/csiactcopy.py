#!/usr/bin/env python
# ==========================================================================
# Copies IACT data from remote machine
#
# Copyright (C) 2016 Michael Mayer
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
import os
import sys
import json
import shutil
import gammalib
import ctools

# ================ #
# csiactdata class #
# ================ #
class csiactcopy(ctools.cscript):
    """
    Copies IACT data from remote machine
    
    This script copies IACT data from one location to another. It can
    take a list of observation IDs to allow the download specific
    observations. Index files get merged and updated accordingly.
    """

    # Constructor
    def __init__(self, *argv):
        """
        Constructor.
        """
        # Set name
        self._name          = 'csiactcopy'
        self._version       = '1.1.0'
        self._datapath      = os.getenv('VHEFITS','')
        self._remote_master = gammalib.GFilename()
        self._remote_base   = ''
        self._prodname      = ''
        self._outpath       = ''
        self._runlist       = gammalib.GFilename()
        self._runs          = []

        # Initialise application by calling the appropriate class
        # constructor.
        self._init_cscript(argv)

        # Return
        return


    # Private methods
    def _get_parameters(self):
        """
        Get parameters from parfile and setup the observation
        """
        
        # Get Parameters
        self._remote_master = self['remote_master'].filename()
        if not self._remote_master.exists():
            raise RuntimeError('*** ERROR: FITS data not available. No '
                               'master index file found in "'+
                               self._remote_master+'". Make sure remote '
                               'file system is properly mounted.')
        
        # Get parameters
        self._prodname = self['prodname'].string()
        self._outpath  = gammalib.expand_env(self['outpath'].string())
        self._runlist  = self['runlist'].filename()            

        #  Write input parameters into logger
        self._log_parameters(gammalib.TERSE)
        
        # Return
        return

    def _copy(self, source, clobber):     
        """
        Copy file to outpath
        
        Parameters
        ----------
        source : string
            Path of file to be copied

        Returns
        -------
        filesize : float
            Size of the file that was copied
        """
        
        # Get file destination
        destination = os.path.join(self._outpath,
                                   os.path.relpath(source, self._remote_base))
            
        # Initialise return value
        filesize = 0.0
        
        # Logging
        if self._logVerbose():
            self._log('\n')
            self._log.header3('Copy file')
            self._log_value('Source', source)
            self._log_value('Destination', destination)
            self._log_value('Already exists', str(os.path.isfile(destination)))
            self._log_value('Overwrite', clobber)
            self._log.parformat('Copying')
        
        # Flag if file destination is already available
        is_file = os.path.isfile(destination)
                
        # check if file could be skipped because clobber=no
        if is_file and clobber == False:
            if self._logVerbose():
                self._log('Skip (clobber=no)')
                self._log('\n')
        
        # check if file could be skipped because it is the same file
        elif is_file and os.path.samefile(destination, source):
            if self._logVerbose():
                self._log('Skip (same file)')
                self._log('\n')
            
        else:  
            # Create directory if not existent
            dest_dir = os.path.dirname(destination)
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)
            
            # Copy file (if source not identical to destination)
            shutil.copy2(source, destination)
            
            # Get filesize
            filesize = os.stat(destination).st_size
            
            # Logging
            if self._logVerbose():
                self._log('Done!')
                self._log('\n')
                   
        # Return 
        return filesize

    def _merge(self, localfits, remotefits, hduname, clobber):
        """
        Merge remote and local fits files
        If the local fits file is not present, a new one is created.
        
        Parameters
        ----------
        localfits : string
            Path of local index FITS file         
        remotefits : string
            Path of remote index FITS file         
        hduname : string
            Name of HDU extension to be merged       
        clobber : bool
            Flag if remote content should overwrite local content        
        """    
        
        # Logging
        if self._logTerse():
            self._log_value('Local file', localfits)
            self._log_value('Remote file', remotefits)
            self._log_value('HDU name', hduname)
            if clobber:
                preference = 'Remote'
            else:
                preference = 'Local'
            self._log_value('Conflict preference', preference)
    
        # Check if local fits file is available
        if os.path.isfile(localfits):    
            local = gammalib.GFits(str(localfits))
            local_hdu = local[hduname]
        else:
            # Otherwise load remote fits file and delete rows
            local = gammalib.GFits(str(remotefits))
            local_hdu = local[hduname]
            local_hdu.remove_rows(0,local_hdu.nrows())
        
        # find local obs_id 
        local_obs = []
        lobs_col  = local_hdu['OBS_ID']
        for obs_id in lobs_col:
            local_obs.append(obs_id)      
             
        # Initialise list of runlists
        # This is kluge: to circumvent a too long file name, we split the 
        # runlists into chunks of 50 observations maximum
        runlists = []
        runs_per_chunk = 50
        for i in range(len(self._runs) / runs_per_chunk + 1):
            chunk = self._runs[i * runs_per_chunk : (i + 1) * runs_per_chunk]
            runlists.append(chunk)

        # Loop over runlist chunks
        for i, runlist in enumerate(runlists):
        
            # Create selection expression for opening remote fits file
            selection = ''
            if len(runlist):
                selection += '['+hduname+']['
                for run in runlist:
                    selection += 'OBS_ID=='+str(run)
                    selection += '||'
                selection = selection[:-2]
                selection += ']'
        
            # Create file name
            remotefile = remotefits + selection
            
            # Open remote fits file
            remote = gammalib.GFits(str(remotefile))
            
            # If first iteration, create clone of FITS column for later use
            if i == 0:
                remote_hdu = remote[hduname].clone()
            else:
                
                # get temporary hdu to be added to current HDU
                tmp_hdu = remote[hduname]
                
                # Get old size of remote HDU
                size = remote_hdu.nrows()
                
                # Extend remote HDU
                remote_hdu.append_rows(tmp_hdu.nrows())
                
                # Loop over rows and columns to copy over values exteding remote HDU
                for col in tmp_hdu:
                    for row in range(col.length()):
                        remote_hdu[col.name()][size + row] = col[row]

        # Get remote obs_id
        remote_obs = []
        robs_col   = remote_hdu['OBS_ID']
        for obs_id in robs_col:
            remote_obs.append(obs_id)
        
        # Log entries of index files   
        if self._logTerse():
            self._log_value('Remote entries', len(remote_obs))
            self._log_value('Local entries', len(local_obs))

        # initialise counter for logging
        removed_rows = 0
        
        # If clobber=yes, we use the remote content to overwrite
        # corresponding local content
        if clobber:
            
            # Loop over remote obs_ids
            for remote_obs_id in remote_obs:
                
                # Check if remote obs_id is present locally
                if remote_obs_id in local_obs:
                    
                    # Remove local obs_id entries
                    table_has_obsid = True
                    
                    # Loop over obs ids and overwrite with remote content
                    while table_has_obsid:
                        
                        # First remove old rows
                        for i in range(local_hdu.nrows()):
                            if remote_obs_id == local_hdu['OBS_ID'][i]:
                                local_hdu.remove_rows(i,1)
                                removed_rows += 1
                                break
                        
                        # Replace with remote content
                        table_has_obsid = False
                        for i in range(local_hdu.nrows()):
                            if remote_obs_id == local_hdu['OBS_ID'][i]:
                                table_has_obsid = True
                                break
                            
        # If clobber=false, we keep the local content unchanged and just
        # expand by remote content        
        else:
            # Loop over remote obs_ids
            for local_obs_id in local_obs:
                
                # Check if local obs_id is present remotely
                if local_obs_id in remote_obs:
                    
                    # Remove remote obs_id entries
                    table_has_obsid = True
                    while table_has_obsid:
                        for i in range(remote_hdu.nrows()):
                            if local_obs_id == remote_hdu['OBS_ID'][i]:
                                remote_hdu.remove_rows(i,1)
                                removed_rows += 1
                                break
                        table_has_obsid = False
                        for i in range(remote_hdu.nrows()):
                            if local_obs_id == remote_hdu['OBS_ID'][i]:
                                table_has_obsid = True
                                break
    
        # Store number of local rows
        old_local_rows = local_hdu.nrows()
        
        # Add remote HDUs
        local_hdu.insert_rows(old_local_rows, remote_hdu.nrows())
        
        # Log actions
        if self._logTerse():
            if clobber:
                what = 'Removed local rows'
            else:
                what = 'Skipped remote rows'
            self._log_value(what, removed_rows)

        # Loop over columns 
        for i in range(local_hdu.ncols()):
            
            # Get local and remote columns
            local_col = local_hdu[i]
            remote_col = remote_hdu[i]    
            
            # Loop over entries and merge
            for j in range(remote_col.length()):
                local_col[j+old_local_rows] = remote_col[j]
        
        # Save local fits file
        local.saveto(str(localfits), True)
               
        # Return
        return


    # Public methods
    def run(self):
        """
        Run the script
        """
        # Switch screen logging on in debug mode
        if self._logDebug():
            self._log.cout(True)

        # Get parameters
        self._get_parameters()

        # Make destination directory if not available
        if not os.path.isdir(self._outpath):            
            os.makedirs(self._outpath)   
        
        # Log output
        if self._logTerse():
            self._log('\n')
            self._log.header2('Runlist information')
        
        # Initialise runlist array   
        self._runs = []
        
        # Check if runlist file is available
        if self._runlist.exists():
            runfile = open(self._runlist.url())
            
            # Read runlist
            for line in runfile.readlines():
                if len(line) == 0:
                    continue
                if line[0] == '#':
                    continue
                if len(line.split()) > 0:
                    self._runs.append(int(line.split()[0]))
            
            # Close runlist file
            runfile.close()   
            
            # Logging
            if self._logTerse():
                self._log_value('Number of observations', len(self._runs))
        
        # Copy all data if runlist file is 'NONE'
        elif self._runlist == 'NONE':
            if self._logTerse():
                self._log('Copy all available data')
                self._log('\n')
        
        # Raise exception if file not valid
        else:
            raise RuntimeError('*** ERROR: Runlist file "'+
                               self._runlist+'" not available.')
        
        # Check for availability of remote master file
        if not self._remote_master.exists():
            raise RuntimeError('*** ERROR: Remote master file "'+
                               self._remote_master+'" does not exist.')
        
        # Retrieve json data from remote master
        json_data = open(self._remote_master.url()).read()
        data      = json.loads(json_data) 
        if not 'datasets' in data:
            raise RuntimeError('*** ERROR: Key "datasets" not available '
                               'in remote master index file "'+
                               self._remote_master+'".')
        
        # Get array of configurations
        configs = data['datasets']
        
        # Get remote paths
        self._remote_base = self._remote_master.path()
                
        # Initialise flag if prod has been found
        has_prod = False
        
        # Initialise file names to be copied
        files = set()
        
        # Logging
        if self._logTerse():
            self._log('\n')
            self._log.header2('Loop over remote configs')
        
        # Loop over configs
        for config in configs: 
            
            # Logging          
            if self._logVerbose():
                self._log.header2(str(config['name']))
            
            # Check if prodname was found
            if config['name'] == self._prodname:
                
                # Inidicate that prodname has been found
                has_prod = True           
                
                # Build path of index files
                remote_hdu = os.path.join(self._remote_base, config['hduindx'])
                remote_obs = os.path.join(self._remote_base, config['obsindx'])
                
                # Log information
                if self._logTerse():
                    self._log.header3('Remote config "'+self._prodname+'"')
                    self._log_value('HDU index', remote_hdu)
                    self._log_value('Observation index', remote_obs)
                
                # Open remote HDU index file
                fits = gammalib.GFits(str(remote_hdu))
                table = fits['HDU_INDEX']
                
                # Initialise flag if SIZE column is present
                has_size = table.contains('SIZE')
                
                # Initialise file size
                if has_size:
                    cp_size = 0
                
                # Initialise remote observation IDs
                remote_ids = set()
                for row in range(table.nrows()):
                    remote_ids.add(table['OBS_ID'][row])
                
                # Log runs that are not available remotely
                for run in self._runs:
                    
                    # Check for run not in remote data store
                    if not run in remote_ids:  
                        if self._logNormal():
                            self._log('Skip observation '+str(run)+': ')
                            self._log('ID not available remotely')
                            self._log('\n')
                
                # Loop over remote HDU index file
                for row in range(table.nrows()):
                    
                    # Get observation ID
                    obs_id    = table['OBS_ID'][row]
                    file_dir  = table['FILE_DIR'][row]
                    file_name = table['FILE_NAME'][row]
                    
                    # Skip if filename is empty
                    if file_name == '':
                        continue
                    
                    # Check if we need to consider an input runlist
                    if len(self._runs):
                        
                        # Check if obs id is in runlist
                        if obs_id in self._runs:                                    
                            
                            # Get filename
                            fname = os.path.join(os.path.dirname(remote_hdu),
                                                 file_dir, file_name)
                            
                            # Add file
                            oldlen = len(files)
                            files.add(fname)
                            newlen = len(files)
                            
                            # Add file size
                            if has_size and newlen > oldlen:
                                cp_size += table['SIZE'][row]
                        
                    # Otherwise add every file
                    else:
                        # Get filename
                        fname = os.path.join(os.path.dirname(remote_hdu),
                                             file_dir, file_name)
                        
                        # Add file
                        oldlen = len(files)
                        files.add(fname)
                        newlen = len(files)
                        
                        # Add file size
                        if has_size and newlen > oldlen:
                            cp_size += table['SIZE'][row]
                            
                # Log file information
                if self._logTerse():
                    self._log('\n')
                    self._log.header2('File information')
                    self._log_value('Number of files', len(files))
                    if has_size:
                        size = float(cp_size) * 1.0e-6
                        self._log_value('Size', '%.2f MB' % size)
                if self._logVerbose():
                    self._log('\n')
                    self._log.header3('File names')
                    for filename in files:
                        self._log(str(filename)+'\n')

                # Close HDU index file
                fits.close()
                
            # If prodname is not found just log that we skip the config
            else:
                if self._logExplicit():
                    self._log('\n')
                    self._log.header3('Skipping config "'+
                                      str(config['name'])+'"')
                    self._log('\n')
        
        # Raise Exception if prodname was not found
        if not has_prod: 
            msg = '*** ERROR: FITS production "'+self._prodname+'" not '
            msg += 'available. Available productions are:\n'
            for config in configs:
                msg += ' - '+config['name']+'\n'
            raise RuntimeError(msg)

        # Logging
        if self._logNormal():
            self._log('\n')
            self._log.header1('Copying files')
        
        # Intialise counter
        k = 0
    
        # Initialise values for logging
        last_fraction      =  0.0
        fraction_increment = 20.0
        
        # Use 10% step increase
        if self._logNormal():
            fraction_increment = 10.0
            
        # Use 5% step increase
        if self._logTerse():
            fraction_increment = 5.0
        
        # Use 2% step increase
        if self._logExplicit():
            fraction_increment = 2.0
        
        # Initialise logging properties
        n_copied   = 0
        total_size = 0.0
        
        # Loop over files and copy
        for filename in files:
            
            # Log progress
            fraction = float(k) / float(len(files)) * 100.0
            while fraction > last_fraction:
                
                # Print status of copying procedure
                if self._logNormal() and not self._logVerbose():
                    self._log_value('Status', '%d %%' % int(last_fraction))
                last_fraction += fraction_increment
            
            # Copy file
            filesize = self._copy(filename, self._clobber())

            # If the filesize is positive then increment the number of copied
            # files and add the size to the total copied filesize
            if filesize > 0.0:
                total_size += filesize
                n_copied   += 1
            
            # Increment file counter
            k += 1
        
        # Logging
        if self._logNormal() and not self._logVerbose():
            self._log.parformat('Status')
            self._log('Finished')
            self._log('\n')
        
        # Logging about index files
        if self._logTerse():
            self._log('\n')
            self._log.header1('Updating index files')
        
        # Build local hdu index file name
        local_hdu = os.path.join(self._outpath,
                                 os.path.relpath(remote_hdu,
                                                 self._remote_base))
        # Build local obs index file name
        local_obs = os.path.join(self._outpath,
                                 os.path.relpath(remote_obs,
                                                 self._remote_base))
        
        # If we have a runlist then merge index file
        if len(self._runs):
            
            # Logging            
            if self._logTerse():
                self._log('\n')
                self._log.header3('HDU index')
                
            # Merge remote index files with local files
            self._merge(local_hdu, remote_hdu, 'HDU_INDEX', self._clobber())
            
            # Logging
            if self._logTerse():
                self._log('\n')
                self._log.header3('OBS index')
                
            # Merge remote index files with local files
            self._merge(local_obs, remote_obs, 'OBS_INDEX', self._clobber())
            
        else: 
            # If all files were copied, just copy index files too
            self._copy(remote_hdu, self._clobber())
            self._copy(remote_obs, self._clobber())
        
        # Logging
        if self._logTerse():
            self._log('\n')
            self._log.header3('Master index file')
        
        # Adding prodname to local master
        localmaster = os.path.join(self._outpath, 'master.json')
        
        # If no local master is found, copy master over first
        if not os.path.isfile(localmaster):
            self._copy(self._remote_master.url(), self._clobber())
            
        # Load local master
        json_data = open(localmaster).read()
        data      = json.loads(json_data) 
        configs   = data['datasets']
        
        # Initialise flag indicating if we already have prodname in master
        # file
        has_config = False
        
        # Initialise new configs array
        newconfigs = []
        
        # Loop over configs in master index file
        for config in configs:
            
            # Get hdu and obs index files
            hdu = os.path.join(self._outpath, config['hduindx'])
            obs = os.path.join(self._outpath, config['obsindx'])
            
            # Check if index files are available
            if not (gammalib.GFilename(str(hdu)).is_fits() and
                    gammalib.GFilename(str(obs)).is_fits()):
                if self._logTerse():
                    self._log('Removing "'+str(config['name'])+'" ')
                    self._log('(not available)')
                    self._log('\n')
            else:
                # Append config if valid
                newconfigs.append(config)
                if self._logTerse():
                    self._log('Keeping "'+str(config['name'])+'"')
                    self._log('\n')
            
            # Signals that downloaded config is available
            if config['name'] == self._prodname:
                has_config = True
        
        # Create new entry if config was not available    
        if not has_config:
            newdict            = dict.fromkeys(['name','hduindx','obsindx'])
            newdict['name']    = self._prodname
            newdict['hduindx'] = os.path.relpath(local_hdu, self._outpath)
            newdict['obsindx'] = os.path.relpath(local_obs, self._outpath)
            newconfigs.append(newdict)
            if self._logTerse():
                self._log('Adding "'+str(newdict['name'])+'"')
                self._log('\n')
        
        # Write new json master file. Make sure that we have write permission
        # before writing the file. This is needed as the original master file
        # may be read-only, and the shutil.copy2 function copies over the
        # access permissions.
        os.chmod(localmaster, 420)
        f = open(localmaster, 'w')
        data['datasets'] = newconfigs
        json.dump(data, f, indent=2)
        f.close()

        # Log summary
        if self._logNormal():
            self._log('\n')
            self._log.header1('Summary')
            self._log_value('Data files found', len(files))
            self._log_value('Data files copied', n_copied)
            self._log_value('Size', '%.2f MB' % (float(total_size)*1.0e-6))
            self._log_value('Local configs', len(newconfigs))
            if self._logTerse():
                self._log('\n')
                self._log.header3('Content of master index')
                for config in newconfigs:
                    self._log(str(config['name']))
                    self._log('\n')

        # Return
        return       

    def execute(self):
        """
        Execute the script
        """
        # Open logfile
        self.logFileOpen()

        # Run the script
        self.run()

        # Return
        return
    
        
# ======================== #
# Main routine entry point #
# ======================== #
if __name__ == '__main__':

    # Create instance of application
    app = csiactcopy(sys.argv)

    # Execute application
    app.execute()
