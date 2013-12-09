'''
SSUTIL: Module for generating and organizing the necessary files for simulations of solid solutions in VASP.
'''

'''
Importing modules
'''
import numpy as np
import scipy as sp
import pandas as pd

from parse_vasp import *

import requests
from bs4 import BeautifulSoup

import copy
from itertools import combinations
from scipy.misc import factorial
from collections import Iterable

from warnings import warn

import datetime

'''
Helper Functions
'''

def apply_gen(p,g):
    '''
    Apply generator 'g' to a set of positions 'p'.
    '''
    
    # Check shape and value of p and g
    assert p.shape[1] == 3
    assert g.shape == (3,4)
    assert p.max() <= 1. and p.min >= 0.
    assert g.max() <= 1. and g.min >= -1.
    
    # Carry out dot product
    ptrans = np.dot(p,g[:,0:3]) + g[:,3] # could casting cause a problem for n=3?
    
    # shift all positions to between 0 and 1
    pmod = np.mod(ptrans,1.)
    return pmod 

def site_idx(sites,pos):
    '''
    For an array of possible sites, match coordinates in 'pos' and return
    the index of the corresponding site. If site does not match, return None.
    '''
    
    assert pos.shape[1] == 3
    assert sites.shape[1] == 3
    
    matches = []
    for p in pos:
        m = np.where((sites == p).all(axis=1))
        try:
            matches.append(m[0].flatten()[0])
        except:
            warn('Generated cite does not match')
        
    return matches

def get_translations(super_dim):
    '''
    If the cell is a supercell, this will find all the fractional shifts that generate equivalent 
    positions. Input is a 3 element iterable containing the multiple of the unit cell parameter in 
    each direction. Assumes periodic boundary conditions on cell.
    '''
    assert isinstance(super_dim,Iterable),\
    'Input is a 3 element iterable containing the multiple of the unit cell parameter in each direction.'
    assert len(super_dim) == 3,\
    'Input is a 3 element iterable containing the multiple of the unit cell parameter in each direction.'
    
    supshift = lambda i: np.linspace(0., 1. - 1./super_dim[i] ,super_dim[i])
    
    trans_list = []
    for x in supshift(0):
        for y in supshift(1):
            for z in supshift(2):
                trans_list.append([x,y,z])
    tran = np.array(trans_list)
    
    return tran

'''
Web Query Functions
'''

def get_generators(sg):
    '''
    Queries the bilbao crystallographic database, returning a list of arrays with the 
    generators associated with a space group. Takes an integer for the number of the 
    space group. Note these generators will be correct only if the sites are in standard 
    notation.
    '''
    # Check that sg is an integer
    if not isinstance(sg,int):
        raise ValueError("'{}' is not an integer reference to a valid spacegroup".format(sg))

    # retrieve html from page for the correct space grop
    generator_url = "http://www.cryst.ehu.es/cgi-bin/cryst/programs/nph-getgen?" \
                    + "list=Standard/Default%20Setting&what=gen&gnum=" + str(sg)
    r  = requests.get(generator_url) 
    data = r.text
    soup = BeautifulSoup(data)

#     print data
    
    # Find all of the generator arrays
    html_gens = soup.contents[1].find_all('pre')
    
    # If generators retrieved translate into numpy arrays
    if len(html_gens) > 1:
        
        gens = []
        for html_gen in html_gens:
            
            # strip html tags
            str_gen = html_gen.stripped_strings.next()
            
            lgen = []
            for x in str_gen.split('\n'):
                inner = []
                
                # if element is a fraction, it must be parsed to produce a float
                for y in x.split():
                    try:
                        inner.append(float(y))
                    except:
                        arg = y.split('/')
                        assert len(arg) == 2
                        inner.append(float(arg[0]) / float(arg[1]) )
                lgen.append(inner)
            gens.append(np.array(lgen))
        
        return gens
    else:
        # Raise error if integer doesn't reference a spacegroup
        raise ValueError("Integer '{}' is not a reference to a valid spacegroup".format(sg) )

'''
Functions for handling combinations.
'''

def subCombinations(run,sub_rule,n_sub):
    '''
    Return all possible combinations of integer indices for the positions in the cell
    defined in vasp_run 'run', given an atomic substitiution rule 'sub_rule', and a number
    of substitutions per cell 'n_sub'. Only single substitutions allowed. If an iterable
    of integers is provided, a list of arrays containing the combinations for each 
    number of substitutions.'
    '''
    assert isinstance(run,vasp_run), 'Run must be specified by a vasp_run object.'
    assert len(run.spec) > 0, 'No species defined in vasp_run "{}"'.format(myRun.name)
        
    # Check that only one rule is to be applied and save in a dict
    sub_rule_errText = 'Only single substitutions allowed.'
    if isinstance(sub_rule,dict):
        assert len(sub_rule.keys()) == 1, sub_rule_errText
        rule = sub_rule
    elif isinstance(sub_rule,list) or  isinstance(sub_rule,tuple) \
    or isinstance(sub_rule,np.ndarray):
        assert len(sub_rule) == 2, sub_rule_errText
        rule = {sub_rule[0]:sub_rule[1]}
    else:
        raise TypeError('Invalid type for substitution rule')
        
    if not rule.keys()[0] in run.spec:
        warn('Species {} not found in run {}'.format(rule.keys()[0],run.name) )
        
    # find a sublist of where a replaceable atom resides
    x=0
    idxs = np.array([])
    for i,s in enumerate(run.spec):
        if s == rule.keys()[0]:
            idxs = np.arange(x, x + run.nspec[i])
        x += run.nspec[i]
    
    # Check that n_sub is valid number for the given cell
    n_sub_errText = 'Invalid number of substitutions for cell with {} {} atoms.'.format(len(idxs),\
                                                                     rule.keys()[0])
    # accept either an integer or an iterable
    if isinstance(n_sub,int):
        nums = [n_sub]
    elif isinstance(n_sub,Iterable):
        nums = n_sub
    else:
        raise ValueEror(n_sub_errText)
    
    # store combinations for each n_sub
    results = []
    for n in nums:
        assert isinstance(n,int), n_sub_errText
        assert n >= 0 and n <= len(idxs), n_sub_errText
        
        
        # generate combinations
        combs = np.array([ x for x in combinations(idxs,n) ])
        combs.sort(axis=1)
        
#         # Verify that the number of combinations is correct 
#         if combs.shape[0] != \
#         factorial(len(idxs)) / float(factorial(n)) / float(factorial(len(idxs)-n)) :
#             warn('Number of combinations generated is different than expected.')
#         results.append(combs)

    # return most reasonable type based on the number of 
    if len(results) == 1:
        return results[0]
    elif len(results) == 0:
        return None
    else:
        return results



# Finding unique combinations:
# inputs: vasp run, combinations, spacegroup, 
# optional: shift
# can shift only be included here (positions need to be regenerated with the shift)

def findUniqueCombs(run,combs,gen,tran=None,cell_shift=None,cell_rot=None,verbose=0):
    '''
    Finds the set of unique combinations of positions for a simulation of a solid solution.
    Input is a vasp_run object 'run' run defining the system before substitutions, a MxN array
    'combs' containing all possible combindations. M is the total number of possible combinations
    where N is the number of substitutions being made. A list of arrays corresponding to the generators
    of the strucuture.
    
    Two optional inputs include a list of arrays containing translations that result in equivalent
    configurations (when the cell is a supercell), cell_shift describes the shift in structure from
    the standard definition of the spacegroup. All transformations must described as 4x3 arrays. See
    http://www.cryst.ehu.es/cgi-bin/cryst/programs/nph-doc-trmat for more information.
    
    Set verbose to 1 to print intermediate information (default = 0)
    '''

    assert isinstance(run,vasp_run)
    
    # check that shapes 
    assert combs.shape[1] < run.pos.shape[0]
    
    # shift positions if necessary
    if cell_shift is None:
        positions = run.pos
    elif isinstance(cell_shift,Iterable):
        assert len(cell_shift) == 3, 'Invalid cell_shift.'
        positions = run.pos - cell_shift
    else:
        raise TypeError, 'Invalid cell_shift.'

    # rotate positions if necessary
    if cell_rot is None:
        positions = run.pos
    elif isinstance(cell_rot,np.ndarray):
        assert cell_rot.shape == (3,3),'Invalid cell_rot.'
        irot = np.linalg.inv(cell_rot)
        positions = np.dot(run.pos,irot)
    else:
        raise TypeError, 'Invalid cell_shift.'
    
    # Check that all transformations are in a valid form
    transformErr = 'All transformations must described as 4x3 arrays. See ' \
    + 'http://www.cryst.ehu.es/cgi-bin/cryst/programs/nph-doc-trmat for more information.'
    for g in gen:
        assert isinstance(g,np.ndarray), transformErr
        assert g.shape == (3,4), transformErr
        
    if not tran is None:
        for t in tran:
            assert isinstance(t,np.ndarray), transformErr
            assert t.shape == (3,), transformErr
    
    # create a copy of the combination list, from which combinations will be deleted as they are
    # identified as nonunique
    comb_list = combs.copy()
    unique_comb = [] # store unique combinations
    mults = [] # store multiples of unique combination in complete set of combinations
        
    tol = .01 # define tolerance for comparing the position of atoms in the cell
    count = 0
    
    # Loop until all unique configurations have been identified
    while len(comb_list) > 0:
        
        # use the first comination as the unique position
        a = positions[comb_list[0]]
        count += 1
        
        if verbose == 1:
            print 'Unique Position:', count
            print a
    
        # store matching configurations
        matches = [a] # must include 0
        nmatches = 1 # store number of matches
        prev_nmatches = 0 # previous number of matches
        untested = [a]#         # outer loop, stop when no new equivalent configurations found

        while len(untested) > 0:
            new = []
            for u in untested:
                for g in gen:
                    b = apply_gen(u,g)
                    
                    repeat = False
                    for m in matches:
                        if np.sum(np.abs(m - b)) <= tol:
                            repeat = True
                    #print matches
                    
                    # add match if it is not identical to previous matches
                    if not repeat:
                        new.append(b)
                        matches.append(b)
                        
            # prepare for next iteration        
            untested = new
    
        # apply translations
        if not tran is None:
            tmatches = []
            for t in tran:
                for m in matches:
                    tmatches.append(np.mod(m+t,1.))  # need to check for non-unique combinations
        else:
            tmatches = matches
                
    
        rows=comb_list.shape[0]
        cols=comb_list.shape[1]
        #idx_to_remove = np.zeros(rows)
        
        # boolean with lenght of comb_list to test if combination has been identified
        matched = np.zeros(rows).astype(bool)
        
        # loop through and match combinations to comb_list
        #cmatches = []
        for m in tmatches:
            c = np.array(site_idx(positions,m))
            c.sort() # This must be done to order the combination array in the sa
            try:
                matched += ( cols == (0 == (comb_list - c)).sum(1) )
            except:
                pass
    
    
        # store the new unique combination and its multiplicity in the cell
        unique_comb.append(comb_list[0])

        # store the multiplicity of the new combination
        mults.append(sum(matched))
        
        # delte matching rows from comb_list
        comb_list = comb_list[np.logical_not(matched)]
        
        if verbose == 1:
            print 'Multiplicity:',sum(matched)
            print 'Number of generator loops:', num_gen_loops
            print 'unsorted configurations:', len(comb_list)
            
    return unique_comb, mults
    


def make_ss_runs(run,rule,unique_pos,multip,df_path='./ss_archive.df'):
    '''
    Make all necessary solid solution runs with initial settings identical to vasp_run 'run'. 'rule' specifies the
    atomic replacement rule. Substitution sites are read from array 'unique_pos', which index unique positions in 
    the original positions contained in 'run'. An array with the same length 'multip' contains the number of 
    multiples for each unique position. 'df' contains a pandas dataframe in which metadata about the runs
    is stored for easy referencing.
    '''
    
    ss_dir = os.path.join(run.wd,'ss_runs')
    cell = run.cell
    
    # increment ss_dir if previous directories exist
    count = 0
    while os.path.exists(ss_dir):
        count +=1
        ss_dir = os.path.join(run.wd,'ss_runs'+'_{:d}'.format(count))
    
    os.makedirs(ss_dir)
    
    new_runs = []
    for i,comb in enumerate(uni):
        ss_run = os.path.join(ss_dir,'run_'+'{:03d}'.format(i) )
        os.makedirs(ss_run)
        new_run = myRun.copyToLoc(ss_run,refcarToPoscar=True)
        new_runs.append(new_run)
        
        nspec_i = run.nspec
        spec_i = run.spec
        
        # Generate new position arrays, substituted atoms are placed immediately after the replacee atoms
        spec = []; nspec = []; pos = np.zeros([0,3])
        count = 0
        for n,s in zip(nspec_i,spec_i):
            pos_i = run.pos[np.arange(count,count+n)]
            if s in rule.keys():
                pos_same = np.delete(pos_i,comb-count,axis=0)
                pos_sub = pos_i[comb-count]
                pos = np.vstack([pos,pos_same,pos_sub])
                nspec += [n-len(comb),len(comb)]
                spec += [s,rule[s]]
            else:
                pos = np.vstack([pos,pos_i])
                nspec.append(n)
                spec.append(s)
        
        # Replace position data
        new_run.pos = pos
        new_run.spec = spec
        new_run.nspec = nspec
        
        # Write new position files
        new_run.writePosFile(os.path.join(ss_run,'POSCAR'),cell,nspec,pos)
        new_run.writePosFile(os.path.join(ss_run,'REFCAR'),cell,nspec,pos)
                
        # Write new POTCAR file
        new_run.makePotcar(spec)
        
    # Write
    writeToDataframe(new_runs,run,rule,unique_pos,multip)
    #writeToDataframe(new_runs,**args,**kwargs)
        
def writeToDataframe(ss_runs,run,rule,uniq,multip,df_path='./ss_archive.df'):
    '''
    Stores relavent data in a DataFrame and pickles it.
    '''

    # current date/time
    dt = datetime.datetime.now()
    
    # store relavent information in pandas DataFrame
    tosave = []
    for i,ss_run in enumerate(ss_runs):
        tosave.append([ss_run.name,run.name,rule.keys()[0],rule.values()[0],len(uniq[i]),len(uniq),uniq[i],multip[i]/float(sum(multip)),
         ss_run.spec,ss_run.nspec,ss_run.wd,dt])
    cols = ['ss_run_name','original_run','sub_target','substitute','num_sub','num_ss_runs','original_sites',
            'occurance_freq','spec','num_spec','path','time']
    df = pd.DataFrame(tosave,columns=cols)
    
    # if the pickled dataframe exists, load it and concatenate the new results
    if os.path.isfile(df_path):
        prev_df = pd.read_pickle(df_path)
        new_df = pd.concat([prev_df,df])
    else:
        new_df = df

    # pickle the dataframe for future use
    new_df.to_pickle(df_path)  # save it
        
