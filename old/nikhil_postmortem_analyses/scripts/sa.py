#!/usr/bin/env python

"""
This example shows how to use the Ensemble MD Toolkit ``SimulationAnalysis``
pattern to execute 32 iterations of a simulation analysis loop. In the
``pre_loop`` step, a reference random ASCII file is uploaded. Each
``simulation_step`` generates 16 new random ASCII files.  Each ``analysis_step``
checks calculates the Levenshtein distance between  the newly generated files
and the reference file.

.. figure:: ../images/simulation_analysis_pattern.*
   :width: 300pt
   :align: center
   :alt: Simulation-Analysis Pattern

   Fig.: `The Simulation-Analysis Pattern.`

Run Locally
^^^^^^^^^^^

.. warning:: In order to run this example, you need access to a MongoDB server and
             set the ``RADICAL_PILOT_DBURL`` in your environment accordingly.
             The format is ``mongodb://hostname:port``. Read more about it
             MongoDB in chapter :ref:`envpreparation`.

**Step 1:** View and download the example sources :ref:`below <example_source_simulation_analysis_loop>`.

**Step 2:** Run this example with ``RADICAL_ENMD_VERBOSE`` set to ``info`` if you want to
see log messages about simulation progress::

    RADICAL_ENMD_VERBOSE=info python simulation_analysis_loop.py

Once the script has finished running, you should see the SHA1 checksums
generated by the individual ensembles  (``checksumXX.sha1``) in the in the same
directory you launched the script in.

Run Remotely
^^^^^^^^^^^^

By default, simulation and analysis steps run on one core your local machine::

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

.. _example_source_simulation_analysis_loop:

Example Source
^^^^^^^^^^^^^^
"""

__author__       = "Ole Weider <ole.weidner@rutgers.edu>"
__copyright__    = "Copyright 2014, http://radical.rutgers.edu"
__license__      = "MIT"
__example_name__ = "Simulation-Analysis Example (generic)"

import math
import pandas
import pickle
import pprint
import datetime
import random
import os
import smtplib
import numpy as np

from radical.ensemblemd import Kernel
from radical.ensemblemd import SimulationAnalysisLoop
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SimulationAnalysisLoop
from radical.ensemblemd import SingleClusterEnvironment


# ------------------------------------------------------------------------------
#
class RandomSA(SimulationAnalysisLoop):
    """RandomSA implements the simulation-analysis loop described above. It
       inherits from radical.ensemblemd.SimulationAnalysisLoop, the abstract
       base class for all Simulation-Analysis applications.
    """
    def __init__(self, maxiterations, simulation_instances=1, analysis_instances=1):
        SimulationAnalysisLoop.__init__(self, maxiterations, simulation_instances, analysis_instances)

    def pre_loop(self):
        """pre_loop is executed before the main simulation-analysis loop is
           started. In this example we create an initial 1 kB random ASCII file
           that we use as the reference for all analysis steps.
        """
        pass
    def simulation_step(self, iteration, instance):
        """The simulation step generates a 1 kB file containing random ASCII
           characters that is compared against the 'reference' file in the
           subsequent analysis step.
        """
        k = Kernel(name="misc.mkfile")
        k.arguments = ["--size=10000000", "--filename=asciifile.dat"]
        return k

    def analysis_step(self, iteration, instance):

        link_input_data = []
        for i in range(1,self.simulation_instances+1):
            link_input_data.append("$PREV_SIMULATION_INSTANCE_{instance}/asciifile.dat > asciifile-{instance}.dat".format(instance=i))

        k = Kernel(name="misc.ccount")
        k.arguments = ["--inputfile=asciifile.dat", "--outputfile=cfreqs.dat"]
        k.link_input_data = link_input_data
        k.download_output_data = "cfreqs.dat"
        k.cores = 1
        return k
	
    def post_loop(self):
        # post_loop is executed after the main simulation-analysis loop has
        # finished. In this example we don't do anything here.
        pass

def find_profile(files):
    for item in files:
        if item.find('execution_profile') != -1:
            return item

def cleanup():
    os.system('rm *.dat')
        

# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

    try:
        # Create a new static execution context with one resource and a fixed
        # number of cores and runtime.

            # scale = [1,16,32,64,128]
            # num_of_iterations = 4
            scale = [1,16]
            num_of_iterations = 2
            pairings = []

            for core in scale:
                for i in range(0,num_of_iterations):
                    pairings.append((core,i))

            random.shuffle(pairings)

            pp = pprint.PrettyPrinter()
            pp.pprint(pairings)

            for item in pairings:
                core_count = item[0]
                iteration = item[1]
                # core_count = 1
                # iteration = 24
                instance_count = core_count
                cluster = SingleClusterEnvironment(
                    resource="xsede.stampede",
                    cores=core_count,
                    walltime=30,
                    username="tg826231",
                    project="TG-MCB090174",
                    database_url=os.environ.get('RADICAL_PILOT_DBURL'),
                    database_name = 'enmddb',
                    queue = "development"
                )

                cluster.allocate()
                randomsa = RandomSA(maxiterations=1, simulation_instances=instance_count, analysis_instances=instance_count)
                cluster.run(randomsa)
                cluster.deallocate()

                new_core = "enmd_core_overhead_{0}_{1}.csv".format(core_count,iteration)
                new_pattern = "enmd_pat_overhead_{0}_{1}.csv".format(core_count,iteration)
                new_profile = "profile_{0}_{1}.csv".format(core_count,iteration)

                original_core = "enmd_core_overhead.csv"
                original_pattern = "enmd_pat_overhead.csv"
                original_profile = find_profile(os.listdir('.'))

                os.system("mv {0} {1}".format(original_core,new_core))
                os.system("mv {0} {1}".format(original_pattern,new_pattern))
                os.system("mv {0} {1}".format(original_profile,new_profile))

                # cleanup()


    except EnsemblemdError, er:

        print "Ensemble MD Toolkit Error: {0}".format(str(er))
        raise # Just raise the execption again to get the backtrace
