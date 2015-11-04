#!/usr/bin/env python



__author__       = "Vivek <vivek.balasubramanian@rutgers.edu>"
__copyright__    = "Copyright 2014, http://radical.rutgers.edu"
__license__      = "MIT"
__example_name__ = "Multiple Simulations Instances, Single Analysis Instance Example (MSSA)"


import sys
import os
import json

from radical.ensemblemd import Kernel
from radical.ensemblemd import SimulationAnalysisLoop
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SingleClusterEnvironment

# ------------------------------------------------------------------------------
#
class MSSA(SimulationAnalysisLoop):
    """MSMA exemplifies how the MSMA (Multiple-Simulations / Multiple-Analsysis)
       scheme can be implemented with the SimulationAnalysisLoop pattern.
    """
    def __init__(self, iterations, simulation_instances, analysis_instances):
        SimulationAnalysisLoop.__init__(self, iterations, simulation_instances, analysis_instances)


    def simulation_step(self, iteration, instance):
        """In the simulation step we
        """
        k = Kernel(name="misc.mkfile")
        k.arguments = ["--size=1000", "--filename=asciifile.dat"]
	k.download_output_data = ['asciifile.dat > asciifile-{0}.dat'.format(instance)]
        return [k]

    def analysis_step(self, iteration, instance):
        """In the analysis step we use the ``$PREV_SIMULATION`` data reference
           to refer to the previous simulation. The same
           instance is picked implicitly, i.e., if this is instance 5, the
           previous simulation with instance 5 is referenced.
        """
        upload_input_data = []
        for i in range(1, self.simlation_instances+1):
            upload_input_data.append("asciifile-{0}.dat".format(i))

        k = Kernel(name="misc.ccount")
        k.arguments            = ["--inputfile=asciifile-*.dat", "--outputfile=cfreqs.dat"]
        k.upload_input_data      = upload_input_data
        k.download_output_data = "cfreqs.dat > cfreqs-{iteration}.dat".format(iteration=iteration)
        return [k]


# ------------------------------------------------------------------------------
#
if __name__ == "__main__":


    try:

        # number of cores and runtime.
        cluster = SingleClusterEnvironment(
                        resource='xsede.comet',
                        cores=192,
                        walltime=20,
                        username='vivek91',

                        project='unc100',
#                        access_schema = config[resource]['schema'],
                        queue = 'compute',

                        database_url='mongodb://ec2-54-221-194-147.compute-1.amazonaws.com:24242',
                        database_name='myexps',
        )

        # Allocate the resources.
        cluster.allocate()

        # We set both the the simulation and the analysis step 'instances' to 16.
        # If they
        mssa = MSSA(iterations=1, simulation_instances=192, analysis_instances=1)

        cluster.run(mssa)

        cluster.deallocate()

    except EnsemblemdError, er:

        print "Ensemble MD Toolkit Error: {0}".format(str(er))
        raise # Just raise the execption again to get the backtrace
