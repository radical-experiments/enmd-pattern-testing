#!/usr/bin/env python

"""

This example shows how to use the Ensemble MD Toolkit ``SimulationAnalysis``
pattern to execute 4 iterations of a simulation analysis loop with multiple
simulation instances and a single analysis instance. We skip the ``pre_loop``
step in this example. Each ``simulation_step`` generates 16 new random ASCII
files. One ASCII file in each of its instances. In the ``analysis_step``, the
ASCII files from each of the simulation instances are analyzed and character
count is performed on each of the files using one analysis instance. The output
is downloaded to the user machine.

.. code-block:: none

    [S]    [S]    [S]    [S]    [S]    [S]    [S]
     |      |      |      |      |      |      |
     \-----------------------------------------/
                          |
                         [A]
                          |
     /-----------------------------------------\
     |      |      |      |      |      |      |
    [S]    [S]    [S]    [S]    [S]    [S]    [S]
     |      |      |      |      |      |      |
     \-----------------------------------------/
                          |
                         [A]
                          :

Run Locally
^^^^^^^^^^^

.. warning:: In order to run this example, you need access to a MongoDB server and
             set the ``RADICAL_PILOT_DBURL`` in your environment accordingly.
             The format is ``mongodb://hostname:port``. Read more about it
             MongoDB in chapter :ref:`envpreparation`.

**Step 1:** View and download the example sources :ref:`below <multiple_simulations_single_analysis>`.

**Step 2:** Run this example with ``RADICAL_ENMD_VERBOSE`` set to ``info`` if you want to
see log messages about simulation progress::

    RADICAL_ENMD_VERBOSE=info python multiple_simulations_single_analysis.py

Once the script has finished running, you should see the character frequency files
generated by the individual ensembles  (``cfreqs-1.dat``) in the in the same
directory you launched the script in. You should see as many such files as were the
number of iterations. Each analysis stage generates the character frequency file
for all the files generated in the simulation stage every iteration.

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
simulations instances can run in parallel::

    SingleClusterEnvironment(
        resource="stampede.tacc.utexas.edu",
        cores=16,
        walltime=30,
        username=None,  # add your username here
        project=None # add your allocation or project id here if required
    )


.. _multiple_simulations_single_analysis:

Example Source
^^^^^^^^^^^^^^
"""

__author__       = "Vivek <vivek.balasubramanian@rutgers.edu>"
__copyright__    = "Copyright 2014, http://radical.rutgers.edu"
__license__      = "MIT"
__example_name__ = "Multiple Simulations Instances, Single Analysis Instance Example (MSSA)"

from radical.ensemblemd import Kernel
from radical.ensemblemd import SimulationAnalysisLoop
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SingleClusterEnvironment
import datetime

# ------------------------------------------------------------------------------
#
class MSSA(SimulationAnalysisLoop):
    """MSMA exemplifies how the MSMA (Multiple-Simulations / Multiple-Analsysis)
       scheme can be implemented with the SimulationAnalysisLoop pattern.
    """
    def __init__(self, iterations, simulation_instances, analysis_instances):
        SimulationAnalysisLoop.__init__(self, iterations, simulation_instances, analysis_instances)


    def pre_loop(self):
	k = Kernel(name="misc.nop")
	return k

    def simulation_step(self, iteration, instance):
        """In the simulation step we
        """
        k1 = Kernel(name="misc.nop")
        
	k2 = Kernel(name="misc.nop")

        return [k1,k2]

    def analysis_step(self, iteration, instance):

        k1 = Kernel(name="misc.nop")

	k2 = Kernel(name="misc.nop")
        return [k1,k2]


# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

    try:

	# Create a new static execution context with one resource and a fixed
        # number of cores and runtime.

        f1=open('record.data','a')
        f1.write('Start= {0}\n'.format(datetime.datetime.now()))
        cluster = SingleClusterEnvironment(
            resource="xsede.stampede",
            cores=512,
            walltime=10,
	    queue="normal",
            username='vivek91',
            project='TG-MCB090174',
            database_url='mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'
#           database_name='myexps'
        )

        # Allocate the resources.
        f1.write('Allocating= {0}\n'.format(datetime.datetime.now()))
        cluster.allocate()
        f1.write('Allocated= {0}\n'.format(datetime.datetime.now()))

        # We set both the the simulation and the analysis step 'instances' to 16.
        # If they
        mssa = MSSA(iterations=1, simulation_instances=512, analysis_instances=1)

        f1.write('Executing= {0}\n'.format(datetime.datetime.now()))
        cluster.run(mssa)

        f1.write('Deallocating= {0}\n'.format(datetime.datetime.now()))
        cluster.deallocate()
        f1.write('Done= {0}\n'.format(datetime.datetime.now()))

	#print mssa.execution_profile_dict

    except EnsemblemdError, er:

        print "Ensemble MD Toolkit Error: {0}".format(str(er))
        raise # Just raise the execption again to get the backtrace
