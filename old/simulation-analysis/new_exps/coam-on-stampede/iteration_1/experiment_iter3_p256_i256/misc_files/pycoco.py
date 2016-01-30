#!/usr/bin/env python 
from extasy import pcz
from extasy import script
from extasy import coco

import logging as log
import glob
import sys
import os.path as op
import numpy as np
import argparse
import __builtin__

def coco_ui(args):
    '''
    The command line implementation of the CoCo procedure. Should be invoked
    as:
    pyCoCo -i mdfiles -t topfile -o pdbname [-d ndims -n npoints -g gridsize -l logfile -s selection --mpi]    
    where:
        mdfiles  is a list of one or more trajectory files
        topfile  is a compatible topology file
        pdbname  is the basename for the pdb files generated by CoCo. There will
                 be npoints of these; if pdbname='out' then they will be called
                 'out0.pdb', 'out1.pdb'... etc up to 'out(npoints-1).pdb'.
        ndims    specifies the number of dimensions (PCs) in the CoCo mapping
                 (default=3).
        npoints  specifies the number of fronteir points to return structures
                 from (default=1)
        gridsize specifies the number of grid points per dimension in the CoCo
                 histogram (default=10)
        logfile is an optional file with detailed analysis data.
        selection is an optional MD-Analysis style selection string. Only 
				 selected atoms will be used in the CoCo procedure, however
                 ALL atoms will be included in the output files (all unselected
                 ones having coordinates drawn from the first frame analyzed).
                 Such structures are, obviously, only useful as targets for
                 restrained MD or EM procedures.
    '''
    if args.verbosity:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    dict = {}
    dict['topfile'] = args.topfile
    dict['mdfiles'] = glob.glob('*.ncdf')
    dict['outnamebase'] = args.output
    dict['logfile'] = args.logfile
    dict['ndims'] = args.dims
    dict['npoints'] = args.frontpoints
    dict['gridsize'] = args.grid
    dict['selection'] = args.selection
    
    __builtin__.parallelbuiltin = False
        
    if args.mpi:
		 __builtin__.parallelbuiltin = True
		 
    from extasy import cofasu
    from extasy import optimizer    
    from extasy import mpiRelated
    
    rank = mpiRelated.rank
    size = mpiRelated.size

    if dict['logfile'] is not None and rank == 0:
        logfile = open(dict['logfile'],'w')
        logfile.write("*** pyCoCo ***\n\n")

    if rank == 0:
        log.info('creating cofasu...')
    f = []
    i = 0
    print dict['selection']
    for trj in dict['mdfiles']:
        f.append(cofasu.Fasu(dict['topfile'],trj, filter=dict['selection'], owner = i % size))
        i += 1
    
    cf = cofasu.Cofasu(f)

    if dict['selection'] is not None:
    # create a cofasu corresponding to the full system, and also an index
    # file for the subset.
        cref = cofasu.Cofasu(cofasu.Fasu(dict['topfile'], trj, slice=":1"))
        xref = cref.coords(0)
        selndx = []
        for a in f[0].sel.atoms:
            selndx.append(a.number)
    else:
        cref = cf
        xref = np.zeros((3,cf.natoms))
        selndx = np.array((i for i in range(cf.natoms)))
    if dict['logfile'] is not None and rank == 0:
        logfile.write("Trajectory files to be analysed:\n")
        for f in cf.fasulist:
            logfile.write("{}: {} frames\n".format(f.trajectory,f.numframes()))

        logfile.write('\n')
    if rank == 0:
        log.info('cofasu contains {} atoms and {} frames'.format(cf.natoms,cf.numframes()))
    # Some sanity checking for situations where few input structures have
    # been given. If there is just one, just return copies of it. If there
    # are < 5, ensure ndims is reasonable, and that the total number of 
    # grid points (at which new structures might be generated) is OK too.
    # Adust both ndims and gridsize if required, giving warning messages.
    if cf.numframes() == 1:
        if dict['logfile'] is not None and rank == 0:
            logfile.write("WARNING: Only one input structure given, CoCo\n")
            logfile.write("procedure not possible, new structures will be\n")
            logfile.write("copies of the input structure.\n")

        if rank == 0:
            log.info('Warning: only one input structure!')
        for rep in range(dict['npoints']):
            dict['rep'] = rep
            if rank == 0:
                opt = cf.coords(0)
                cf.writepdb('{outnamebase}{rep}.pdb'.format(**dict),opt)
    else:
        if cf.numframes() <= dict['ndims']: 
            dict['ndims'] = cf.numframes() - 1
            if rank == 0:
                log.info("Warning - resetting ndims to {ndims}".format(**dict))
                if dict['logfile'] is not None:
                    logfile.write('Warning - ndims must be smaller than the\n')
                    logfile.write("number of input structures, resetting it to {ndims}\n\n".format(**dict))

        ntot = dict['ndims'] * dict['gridsize']
        if ntot < dict['npoints']:
            dict['gridsize'] = (dict['npoints']/dict['ndims']) + 1
            if rank == 0:
                log.info("Warning - resetting gridsize to {gridsize}".format(**dict))
                if dict['logfile'] is not None:
                    logfile.write('Warning - gridsize too small for number of\n')
                    logfile.write("output structures, resetting it to {gridsize}\n\n".format(**dict))
          
        # Create the optimizer

        if rank == 0:
            log.info('creating optimizer...')
        o = optimizer.Optimizer(cf, tol=0.01)
    
        if rank == 0:
            log.info('running pcazip...')
        p = pcz.Pcz(cf)
        if rank == 0:
            p.write('tmp.pcz')
            log.info('Total variance: {:.2f}'.format(p.evals().sum()))
            
        if dict['logfile'] is not None and rank == 0:
            logfile.write("Total variance in trajectory data: {:.2f}\n\n".format(p.evals().sum()))
            logfile.write("Conformational sampling map will be generated in\n")
            logfile.write("{ndims} dimensions at a resolution of {gridsize} points\n".format(**dict))
            logfile.write("in each dimension.\n\n")
            logfile.write("{npoints} complementary structures will be generated.\n\n".format(**dict))
        dim = dict['ndims']
        projsSel = np.zeros((p.nframes,dim))
        for i in range(dim):
            projsSel[:,i] = p.proj(i)
    
        # Build the COCO map from the selected projection data.
        coco_instance = coco.Coco(projsSel, resolution=dict['gridsize'])
        # Find the COCO points.
        nreps = int(args.frontpoints)
        if rank == 0:
            log.info('generating new points...')
        cp = coco_instance.cpoints(nreps)
    
        optlist = []
        for rep in range(nreps):
            dict['rep'] = rep
            # Convert the point to a crude structure.
            e = p.expand(cp[rep,:])
            crude = p.unmap(e)
            # Optimise the crude structure.
#            opt = o.optimize(crude, dtol=0.005)
            opt = crude
            optlist.append(opt)
            # merge the optimised subset into the full coordinates array:
            xout = xref
            xout[selndx] = opt

            if rank == 0:
                cref.writepdb('{outnamebase}{rep}.pdb'.format(**dict),xout)

        if dict['logfile'] is not None and rank == 0:
            logfile.write("RMSD matrix for new structures:\n")
            for i in range(nreps):
                for j in range(nreps):
                    logfile.write("{:6.2f}".format(cofasu.rmsd(optlist[i],optlist[j])))
                logfile.write("\n")

    if dict['logfile'] is not None and rank == 0:
        logfile.close()
            
################################################################################
#                                                                              #
#                                    ENTRY POINT                               #
#                                                                              #
################################################################################

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('-g','--grid', type=int, default=10, help="Number of points along each dimension of the CoCo histogram")
    parser.add_argument('-d','--dims', type=int, default=3, help='The number of projections to consider from the input pcz file in CoCo; this will also correspond to the number of dimensions of the histogram.')
    parser.add_argument('-n','--frontpoints', type=int, default=1, help="The number of new frontier points to select through CoCo.")
    parser.add_argument('-i','--mdfile', type=str, nargs='*', help='The MD files to process.')
    parser.add_argument('-o','--output', type=str, help='Basename of the pdb files that will be produced.')
    parser.add_argument('-t','--topfile', type=str, help='Topology file.')
    parser.add_argument('-v','--verbosity', nargs='?', help="Increase output verbosity.")
    parser.add_argument('-l','--logfile', type=str, default=None, help='Optional log file.')
    parser.add_argument('-s','--selection', type=str, default='name *', help='Optional atom selection string.')
    parser.add_argument('--mpi', action='store_true', help='Unless the user sets this flag, the program runs in serial.')

    args=parser.parse_args()
    coco_ui(args)
