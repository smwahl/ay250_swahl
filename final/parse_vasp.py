# parse_vasp.py
''' Library defines the vasp_run object, an object to store data about DFT
simulations using VASP.'''

import numpy as np
import os
import re
import shutil
from warnings import warn

def isRepFloat(a):
    try:
        float(a)
        return True
    except:
        return False

def isRepInt(a):
    try:
        int(a)
        return True
    except:
        return False

class vasp_run(object):
    '''object to store data about a single DFT simulation.'''
    def __init__(self,directory=None,pot_dir=None,pot_dict=None):
        self.params = {}
        self.cell = np.zeros([3,3])
        self.pos = np.zeros([0,3])
        self.spec = []
        self.nspec = []
        self.label = None # label in POSCAR file

        if directory is None:
            rundir = os.getcwd()
        else:
            rundir = os.path.abspath(directory)
        self.wd = rundir

        flist = ['POSCAR','INCAR','POTCAR','KPOINTS','CONTCAR','REFCAR','run.scr']
        flistFull = [ os.path.join(rundir, a) for a in flist ]
        self.files = dict(zip(flist,flistFull))
        self.name = os.path.basename(os.path.normpath(rundir))

        # location of pseudopotential files for POTCAR
        if pot_dir == None:
            self.pot_dir = './potentials'
        else:
            self.pot_dir = pot_dir

        if pot_dict == None:
            self.pot_dict = {'Mg':'POTCAR_PBE_Mg_pv', \
                            'Fe':'POTCAR_PBE_Fe_pv',\
                            'O':'POTCAR_PBE_O',\
                            'Si':'POTCAR_PBE_Si'}
        else:
            self.pot_dict

    def makePotcar(self,spec=None):         
        '''
        Generate a POTCAR file, by concatenating files. Update self.spec to be consistant.
        '''
        if not spec is None:
            self.spec = spec
        
#         print self.pot_dict
#         for s in self.spec:
#             print os.path.join(self.pot_dir,self.pot_dict[s] )
        pot_files = [ os.path.join(self.pot_dir,self.pot_dict[s] ) for s in self.spec ]
                               
        with open(os.path.join(self.wd,'POTCAR'), 'w') as outfile:
            for fname in pot_files:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)

    def copyToLoc(self,path,name=None,contcarToPoscar=True,refcarToPoscar=False):
        ''' Copy VASP inputfiles to a new path and return a new vasp_run object pointing to the new location.
        Provides options for which position file to copy to the POSCAR.'''

        if refcarToPoscar == True:
           contcarToPoscar=False

        # copy files to the new directory
        for f in ['INCAR','POTCAR','KPOINTS','REFCAR','run.scr']:
            try:
                shutil.copyfile(self.files[f],os.path.join(path,f))
            except:
                warn('"{}" file missing. will not be copied'.format(f))

        # copy a position file to poscar
        if contcarToPoscar:
            try:
                shutil.copyfile(self.files['CONTCAR'],os.path.join(path,'POSCAR'))
            except:
                warn('"{}" file missing. will not be copied to POSCAR.'.format('CONTCAR'))
        elif refcarToPoscar:
            try:
                shutil.copyfile(self.files['REFCAR'],os.path.join(path,'POSCAR'))
            except:
                warn('"{}" file missing. will not be copied to POSCAR.'.format('REFCAR'))
        else:
            try:
                shutil.copyfile(self.files['POSCAR'],os.path.join(path,'POSCAR'))
            except:
                warn('"{}" file missing. will not be copied to POSCAR.'.format('POSCAR'))

        # Generate new vasp_run object
        new_run = vasp_run(path)
        try:
            new_run.readPotcar()
        except:
            warn('POTCAR not read properly')
        try:
            new_run.readPoscar()
        except:
            warn('POSCAR not read properly')
        try:
            new_run.readIncar()
        except:
            warn('INCAR not read properly')

        return new_run

    

        

    def readIncar(self,filename=None):
        ''' Read in parameters from an VASP INCAR file and store the results in a dictionary'''
        if filename is None:
            fname = self.files['INCAR']
        else:
            fname = filename

        try:
            f = open(fname,'r')
        except:
            raise NameError( ''.join(['file:',str(fname),'not found.']) )
            return 0
        for line in f:
            sline = line.split()

            # check that line is valid and uncommented
            if len(sline) > 2 and not '#' in sline[0] and sline[1] == '=':
#                 print sline
                param = sline[0]
                val = []

                # check for possible string of floats or ints
                if isRepInt(sline[2]):
                    val += [ int(sline[2]) ]
                    idx = 3
                    while  idx < len(sline) and isRepInt(sline[idx]):
                        val += [ int(sline[idx]) ]
                        idx += 1

                elif isRepFloat(sline[2]):
                    val += [ float(sline[2]) ]
                    idx = 3
                    while idx < len(sline) and isRepFloat(sline[idx]):
                        val += [ float(sline[idx]) ]
                        idx += 1
                # check for boolean values
                elif '.TRUE.' in sline[2] :
                    val += [ True ]
                elif '.FALSE.' in sline[2]:
                    val += [ False]
                # if all else fails save entire string that follows
                else:
                    val = [ ' '.join(sline[2:]) ]

                if len(val) == 1:
                    self.params.update({param:val[0]})
                elif len(val) >1:
                    self.params.update({param:val})

        return 1

    def writePosFile(self,fname,cell,nspec,pos,
            label='Generated by parse_vasp.writePosFile',vel=None ):
        '''Write a position file (POSCAR,CONTCAR,etc...).'''

        f = open(fname,'w')

        # format string for float or exponential notation
        fformat = '     {:01.12f}  {:01.12f}  {:01.12f}\n'
        Eformat = '     {:1.12E}  {:1.12E}  {:1.12E}\n'

        # write label
        f.write(''.join([label,'\n']) )

        # write scale factor as 1.0
        f.write('   {:01.12f}\n'.format(1.0) )

        # write cell parameters
        for i in range(3):
            f.write(fformat.format(cell[i,0],cell[i,1],cell[i,2] ) )

        # write nspec
        for n in nspec:
            f.write(' {:3d}'.format(n) )

        f.write('\n')
        f.write('Direct\n') # only implementing Direct option at the moment
        
        # write positions
        try:
            for i in range(sum(nspec)):
                f.write(fformat.format(pos[i,0],pos[i,1],pos[i,2] ) )
        except:
            raise ValueError('Velocities must be an ndarray with # of vectors matching nspec')

        # write velocities if relevant
        try:
            if not vel is None:
                f.write('\n')
                for i in range(sum(nspec)):
                    f.write(eformat.format(pos[i,0],pos[i,1],pos[i,2] ) )
        except:
            raise ValueError('Velocities must be an ndarray with # of vectors matching nspec')

        return 1



    def readPoscar(self,filename=None):        
        ''' Read values from a POSCAR file into the corresponding vasp_run object
variables.'''
        if filename is None:
            fname = self.files['POSCAR']
        else:
            fname = filename

        vals = self.readPosFile(fname)
        self.label = vals['label']
        self.cell = vals['cell']
        self.nspec = vals['nspec']
        self.pos = vals['pos']


    def readPosFile(self,fname):
        ''' Read in information from a position file (POSCAR,CONTCAR,REFCAR) and
return the label, cell parameters, number of species, positions and velocities if theyexist. Returns dict indexed by 'label','cell','nspec','pos' and 'vel'.'''

        # try to open file
        try:
            f = open(fname,'r')
        except:
            raise NameError( ''.join(['file:',str(fname),'not found.']) )
            return 0
        try:
            label = f.readline()
        except:
            raise NameError( ''.join(['file:',str(fname),'not found.']) )
        # read cell parameters
        try:
            scale = float(f.readline())
            icell = np.zeros([3,3])
            for i in range(3):
                xlist = [ float(x) for x in f.readline().split() ]
                icell[i,:] = np.array(xlist)
            cell = scale*icell
        except:
            raise ValueError(''.join(['Problem reading in cell parameters from ',str(fname)]) )
        # read number of atoms (per spec)
        try:
            nspec = [ int(x) for x in f.readline().split() ]
            
        except:
            raise ValueError( ''.join(['Problem reading in number of atoms from ',str(fname)]) )

        if  not 'Direct'  in f.readline():
            raise ValueError( join(['"Cartesian" variable for input not yet implemented',str(fname)]) )

        # read in positions of atoms
        try:
            xpos = np.zeros([sum(nspec),3])
            for i in range(sum(nspec)):
                xpos[i,:] =  np.array( [ float(x) for x in f.readline().split() ])
            pos = xpos
        except:
            raise ValueError(''.join(['Format on positions in ',str(fname),' is incorrect.']) )

        # form output
        output = {'label':label,'cell':cell,'nspec':nspec,'pos':pos}

        # try reading in velocities should they exist
        try:
            f.readline()
            xvel = np.zeros([sum(nspec),3])
            for i in range(sum(nspec)):
                xvel[i,:] =  np.array( [ float(x) for x in f.readline().split() ])
            vel = xvel
            output.update({'vel':vel})
        except:
            pass

        return output


    def readPotcar(self,filename=None):
        ''' Read in atom times from POTCAR'''
        if filename is None:
            fname = self.files['POTCAR']
        else:
            fname = filename

        try:
            f = open(fname,'r')
        except:
            raise NameError(''.join(['file: ',str(fname),' not found.']))
            return 0
        matches = []
        for line in f:
            if "RH" in line:
                matches.append(line)
        self.spec = [ re.sub(r'\W', '',l.split()[1]) for l in matches ]
        return 1

 
class md_run (vasp_run):

    '''object to store data about a single DFT molecular-dynamics simulation.'''
    def __init__(self):
        self.refpos = None


# Test runs functions from the commandline
if __name__ == '__main__':

    myRun = vasp_run('test_run')
    myRun.readIncar()
    myRun.readPoscar()
    myRun.readPotcar()

    print myRun.params  
    print myRun.cell        
    print myRun.pos         
    print myRun.spec        
    print myRun.nspec       
    print myRun.files       
    print myRun.name        
    print myRun.label       
    myRun.writePosFile('POSCARtest',myRun.cell,myRun.nspec,myRun.pos)


