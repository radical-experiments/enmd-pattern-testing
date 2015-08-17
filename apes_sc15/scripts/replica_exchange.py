#!/usr/bin/env python

"""
This example shows how to use the Ensemble MD Toolkit ``ReplicaExchange`` pattern.
Demonstrated RE simulation involves 16 replicas and performs a total of 3 synchronous simulation cycles.
Here exchange step is performed locally, which corresponds to ``static_pattern_1`` execution plugin.
Firstly, for each replica is generated dummy ``md_input_x_y.md``
input file. Each of these files contains 500 randomly generated numbers. As MD kernel in this example
is used ``misc.ccount`` kernel which counts the number of occurrences of all characters in a given file.
As input file for this kernel is supplied previously generated ``md_input_x_y.md`` file. ``misc.ccount``
kernel produces ``md_input_x_y.out`` file, which is transferred to current working directory.
Dummy replica parameter named ``parameter`` is exchanged during the exchange step. Exchanges
of ``parameter`` do not affect next simulation cycle. Replica to perform an exchange with is
chosen randomly.

.. figure:: ../images/replica_exchange_pattern.*
   :width: 300pt
   :align: center
   :alt: Replica Exchange Pattern

   Fig.: `Replica Exchange Pattern.`

Run Locally
^^^^^^^^^^^

.. warning:: In order to run this example, you need access to a MongoDB server and
             set the ``RADICAL_PILOT_DBURL`` in your environment accordingly.
             The format is ``mongodb://hostname:port``. Read more about it
             MongoDB in chapter :ref:`envpreparation`.

**Step 1:** View and download the example sources :ref:`below <example_replica_exchange>`.

**Step 2:** Run this example with ``RADICAL_ENMD_VERBOSE`` set to ``info`` if you want to
see log messages about simulation progress::

    RADICAL_ENMD_VERBOSE=info python replica_exchange.py

Run Remotely
^^^^^^^^^^^^

By default, the exchange steps run on one core your local machine::

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

.. _example_replica_exchange:

Example Source
^^^^^^^^^^^^^^
"""

__author__       = "Antons Treikalis <antons.treikalis@rutgers.edu>"
__copyright__    = "Copyright 2014, http://radical.rutgers.edu"
__license__      = "MIT"
__example_name__ = "Synchronous Replica Exchange Example with 'local' exchange (generic)."


import os
import sys
import json
import math
import random
import pprint
import optparse
from os import path
import radical.pilot

from radical.ensemblemd import Kernel
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SingleClusterEnvironment
from radical.ensemblemd.patterns.replica_exchange import Replica
from radical.ensemblemd.patterns.replica_exchange import ReplicaExchange

#------------------------------------------------------------------------------
#

class ReplicaP(Replica):
    """Class representing replica and it's associated data.

    This class must be extended by users implementing RE pattern for
    specific MD kernel
    """
    def __init__(self, my_id, cores=1):
        """Constructor

        Arguments:
        my_id - integer representing replica's id
        cores - number of cores each replica should use
        """
        self.id = int(my_id)
        self.cores = int(cores)
        self.parameter = random.randint(300, 600)
        self.cycle = 0

        super(ReplicaP, self).__init__(my_id)

class RePattern(ReplicaExchange):
    """In this class are specified details of RE simulation:
        - initialization of replicas
        - generation of input files
        - preparation for MD and exchange steps
        - implementation of exchange routines
    """
    def __init__(self):
        """Constructor
        """
        # hardcoded name of the input file base
        self.inp_basename = "md_input"
        # number of replicas to be launched during the simulation
        self.replicas = None
        # number of cycles the simulaiton will perform
        self.nr_cycles = None

        super(RePattern, self).__init__()

    # ------------------------------------------------------------------------------
    #
    def initialize_replicas(self):
        """Initializes replicas and their attributes to default values
        """
        try:
            self.replicas+1
        except:
            print "Ensemble MD Toolkit Error: Number of replicas must be defined for pattern ReplicaExchange!"
            raise


        replicas = []
        N = self.replicas
        for k in range(N):
            r = ReplicaP(k)
            replicas.append(r)

        return replicas

    # ------------------------------------------------------------------------------
    #
    def build_input_file(self, replica):
        """Generates dummy input file

        Arguments:
        replica - object representing a given replica and it's associated parameters
        """

        file_name = self.inp_basename + "_" + str(replica.id) + "_" + str(replica.cycle) + ".md"

	'''
	k = Kernel("misc.mkfile")
	k.arguments = ["--size=1000", "--filename={0}".format(file_name)]
	return k
	'''

        fo = open(file_name, "wb")
        for i in range(1,1000000):
            fo.write(str(random.randint(i, 500) + i*2.5) + " ");
            if i % 10 == 0:
                fo.write(str("\n"));
        fo.close()

    # ------------------------------------------------------------------------------
    #
    def prepare_replica_for_md(self, replica):
        """Specifies input and output files and passes them to kernel

        Arguments:
        replica - object representing a given replica and it's associated parameters
        """
        input_name = self.inp_basename + "_" + str(replica.id) + "_" + str(replica.cycle) + ".md"
        output_name = self.inp_basename + "_" + str(replica.id) + "_" + str(replica.cycle) + ".out"

        k = Kernel(name="misc.ccount")
        k.arguments            = ["--inputfile=" + input_name, "--outputfile=" + output_name]
        k.upload_input_data      = input_name
        k.download_output_data = output_name
        k.cores = 1

        replica.cycle = replica.cycle + 1
        return k

    # ------------------------------------------------------------------------------
    #
    def prepare_replica_for_exchange(self, replica):
        """This is not used in this example, but implementation is still required

        Arguments:
        replica - object representing a given replica and it's associated parameters
        """
        pass

    #-------------------------------------------------------------------------------
    #
    def exchange(self, r_i, replicas, swap_matrix):
        """Given replica r_i returns replica r_j for r_i to perform an exchange with

        Arguments:
        replicas - a list of replica objects
        swap_matrix - matrix of dimension-less energies, where each column is a replica
        and each row is a state
        """
        return random.choice(replicas)

    #-------------------------------------------------------------------------------
    #
    def get_swap_matrix(self, replicas):
        """Creates and populates swap matrix used to determine exchange probabilities

        Arguments:
        replicas - a list of replica objects
        """
        # init matrix
        swap_matrix = [[ 0. for j in range(len(replicas))]
            for i in range(len(replicas))]

        return swap_matrix

    #-------------------------------------------------------------------------------
    #
    def perform_swap(self, replica_i, replica_j):
        """Performs an exchange of parameters

        Arguments:
        replica_i - a replica object
        replica_j - a replica object
        """
        param_i = replica_i.parameter
        replica_i.parameter = replica_j.parameter
        replica_j.parameter = param_i

# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

    try:
        # Create a new static execution context with one resource and a fixed
        # number of cores and runtime.
        
	scale = [16,32,64,128]
	for core_count in scale:
	#core_count=16
		cluster = SingleClusterEnvironment(
		    resource="xsede.stampede",
		    cores=core_count,
		    walltime=15,
		    username="tg826231",
		    project="TG-MCB090174",
		    database_url='mongodb://ec2-54-221-194-147.compute-1.amazonaws.com:24242',
		    database_name='myexps',
		    queue="development"
		)

		# Allocate the resources.
		cluster.allocate()

		# creating RE pattern object
		re_pattern = RePattern()

		# set number of replicas
		re_pattern.replicas = core_count
	 
		# set number of cycles
		re_pattern.nr_cycles = 1

		# initializing replica objects
		replicas = re_pattern.initialize_replicas()

		re_pattern.add_replicas( replicas )

		# run RE simulation
		cluster.run(re_pattern, force_plugin="replica_exchange.static_pattern_1")

		'''
		print "RE simulation finished!"
		print "Simulation performed {0} cycles for {1} replicas. In your working directory you should".format(re_pattern.nr_cycles, re_pattern.replicas)
		print "have {0} md_input_x_y.md files and {0} md_input_x_y.out files where x in {{0,1,2,...{1}}} and y in {{0,1,...{2}}}.".format( (re_pattern.nr_cycles*re_pattern.replicas), (re_pattern.replicas-1), (re_pattern.nr_cycles-1) )
		print ".md file is replica input file and .out is output file providing number of occurrences of each character."

		# execution profile printing
		print "Profiling info: "
		pp = pprint.PrettyPrinter()
		pp.pprint(re_pattern.execution_profile_dict)

		df = re_pattern.execution_profile_dataframe
		df.to_pickle('results.pkl')
		'''

		import cPickle as pickle
		with open("repex_data_" + str(core_count) + ".pkl",'w') as outfile:
			pickle.dump(re_pattern.execution_profile_dict,outfile)

    except EnsemblemdError, er:

        print "Ensemble MD Toolkit Error: {0}".format(str(er))
        raise # Just raise the execption again to get the backtrace
