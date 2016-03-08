#!/usr/bin/env python

"""
This example shows how to use the Ensemble MD Toolkit ``Pipeline`` pattern
to execute 16 concurrent pipeline of sequential tasks. In the first step of
each pipeline ``step_1``, a 10 MB input file is generated and filled with
ASCII charaters. In the second step ``step_2``, a character frequency analysis
if performed on this file. In the last step ``step_3``, an SHA1 checksum is
calculated for the analysis result. The results of the frequency analysis and
the SHA1 checksums are copied back to the machine on which this script runs.

.. figure:: ../images/pipeline_pattern.*
   :width: 300pt
   :align: center
   :alt: Pipeline Pattern

   Fig.: `The Pipeline Pattern.`

Run Locally
^^^^^^^^^^^

.. warning:: In order to run this example, you need access to a MongoDB server and
             set the ``RADICAL_PILOT_DBURL`` in your environment accordingly.
             The format is ``mongodb://hostname:port``. Read more about it
             MongoDB in chapter :ref:`envpreparation`.

**Step 1:** View and download the example sources :ref:`below <example_source_pipeline>`.

**Step 2:** Run this example with ``RADICAL_ENMD_VERBOSE`` set to ``info`` if you want to
see log messages about simulation progress::

    RADICAL_ENMD_VERBOSE=info python pipeline.py

Once the script has finished running, you should see the raw data of the
character analysis step (``cfreqs-XX.dat``) and the corresponding SHA1 checksums
(``cfreqs-XX.dat.sha1``) in the same directory you launched the script in.

Run Remotely
^^^^^^^^^^^^

By default, the pipeline steps run on one core your local machine::

    SingleClusterEnvironment(
        resource="localhost",
        cores=1,
        walltime=30,
        username=None,
        project=None
    )

You can change the script to use a remote HPC cluster and increase the number
of cores to see how this affects the runtime of the script as the individual
pipeline instances can run in parallel::

    SingleClusterEnvironment(
        resource="stampede.tacc.utexas.edu",
        cores=16,
        walltime=30,
        username=None,  # add your username here
        project=None # add your allocation or project id here if required
    )

.. _example_source_pipeline:

Example Source
^^^^^^^^^^^^^^
"""

__author__       = "Ole Weider <ole.weidner@rutgers.edu>"
__copyright__    = "Copyright 2014, http://radical.rutgers.edu"
__license__      = "MIT"
__example_name__ = "Pipeline Example (generic)"


from radical.ensemblemd import Kernel
from radical.ensemblemd import Pipeline
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SingleClusterEnvironment
from random import shuffle

import pickle
import datetime
import pprint
import random
import sys
import os
import numpy as np


# ------------------------------------------------------------------------------
#
class CharCount(Pipeline):
    def __init__(self, instances, steps):
        Pipeline.__init__(self, instances, steps)

    def stage_1(self, instance):
        """The first step of the pipeline creates a 1 MB ASCI file.
        """
        k = Kernel(name="misc.mkfile")
        k.arguments = ["--size=10000000", "--filename=asciifile-{0}.dat".format(instance)]
        return k

    def stage_2(self, instance):
        """The second step of the pipeline does a character frequency analysis
           on the file generated the first step. The result is transferred back
           to the host running this script.

           ..note:: The placeholder ``$STEP_1`` used in ``link_input_data`` is
                    a reference to the working directory of step 1. ``$STEP_``
                    can be used analogous to refernce other steps.
        """
        k = Kernel(name="misc.ccount")
        k.arguments            = ["--inputfile=asciifile-{0}.dat".format(instance), "--outputfile=cfreqs-{0}.dat".format(instance)]
        k.link_input_data      = "$STEP_1/asciifile-{0}.dat".format(instance)
        k.download_output_data = "cfreqs-{0}.dat".format(instance)
        k.cores = 1
        return k


def find_profile(files):
    for item in files:
        index = item.find('execution_profile')
        if index != -1:
            return item

def cleanup():
    os.system('rm *.dat')
# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

    try:
        # Create a new static execution context with one resource and a fixed
        # number of cores and runtime.

        pp = pprint.PrettyPrinter()
    	#scale = [1,16,32,64,128]
        
        scale = [1,16,32,64,128]
        num_of_iterations = 4 
    	pairings = []

        for core in scale:
            for i in range(0,num_of_iterations):
                pairings.append((core,i))

        done = [(1,0),(128,2),(128,3),(32,0),(32,1),(32,2)]
        for item in done:
            pairings.remove(item)
    	pp.pprint(pairings)

    	shuffle(pairings)

    	for item in pairings:
            core_count = item[0]
            iteration = item[1] 
        
            cluster = SingleClusterEnvironment(
                resource="xsede.stampede",
                # resource="xsede.comet",
                # resource = "localhost",
                cores=core_count,
                walltime=30,
                username="tg826231",
                # username="nrs76",
                project="TG-MCB090174",
                database_url=os.environ.get('RADICAL_PILOT_DBURL'),
                database_name = 'enmddb',
                queue = "development"
            )

            # Allocate the resources. 
            cluster.allocate()
            ccount = CharCount(instances=core_count,steps=2)
            cluster.run(ccount)
            cluster.deallocate()

            new_core_string = "enmd_core_overhead_{0}_{1}.csv".format(core_count,iteration)
            new_core_string = "enmd_pat_overhead_{0}_{1}.csv".format(core_count,iteration)
            new_profile = "profile_{0}_{1}.csv".format(core_count,iteration)

            original_core = "enmd_core_overhead.csv"
            original_pattern = "enmd_pat_overhead.csv"
            original_profile = find_profile(os.listdir('.'))


            os.system("mv {0} {1}".format(original_core,new_core_string))
            os.system("mv {0} {1}".format(original_pattern,new_core_string))
            os.system("mv {0} {1}".format(original_profile, new_profile))


            cleanup()

            


    except EnsemblemdError, er:

        print "Ensemble MD Toolkit Error: {0}".format(str(er))
        raise # Just raise the execption again to get the backtrace
