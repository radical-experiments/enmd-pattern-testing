#!/usr/bin/env python



__author__       = "Ole Weider <ole.weidner@rutgers.edu>"
__copyright__    = "Copyright 2014, http://radical.rutgers.edu"
__license__      = "MIT"
__example_name__ = "Pipeline Example (generic)"

import sys
import os
import json

from radical.ensemblemd import Kernel
from radical.ensemblemd import Pipeline
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SingleClusterEnvironment


# ------------------------------------------------------------------------------
#
class CharCount(Pipeline):
    """The CharCount class implements a three-step pipeline. It inherits from
        radical.ensemblemd.Pipeline, the abstract base class for all pipelines.
    """

    def __init__(self, steps,instances):
        Pipeline.__init__(self, steps,instances)

    def step_1(self, instance):
        """The first step of the pipeline creates a 1 MB ASCI file.
        """
        k = Kernel(name="misc.mkfile")
        k.arguments = ["--size=1000000", "--filename=asciifile-{0}.dat".format(instance)]
	k.download_output_data = ['asciifile-{0}.dat'.format(instance)]
        return k

    def step_2(self, instance):
        """The second step of the pipeline does a character frequency analysis
           on the file generated the first step. The result is transferred back
           to the host running this script.

           ..note:: The placeholder ``$STEP_1`` used in ``link_input_data`` is
                    a reference to the working directory of step 1. ``$STEP_``
                    can be used analogous to refernce other steps.
        """
        k = Kernel(name="misc.ccount")
        k.arguments            = ["--inputfile=asciifile-{0}.dat".format(instance), "--outputfile=cfreqs-{0}.dat".format(instance)]
        k.upload_input_data      = "asciifile-{0}.dat".format(instance)
        k.download_output_data = "cfreqs-{0}.dat".format(instance)
        return k

# ------------------------------------------------------------------------------
#
if __name__ == "__main__":


    try:

        # Create a new static execution context with one resource and a fixed
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

        # Set the 'instances' of the pipeline to 16. This means that 16 instances
        # of each pipeline step are executed.
        #
        # Execution of the 16 pipeline instances can happen concurrently or
        # sequentially, depending on the resources (cores) available in the
        # SingleClusterEnvironment.
        ccount = CharCount(steps=2,instances=192)

        cluster.run(ccount)

        # Print the checksums
        #print "\nResulting checksums:"
        #import glob
        #for result in glob.glob("cfreqs-*.sha1"):
        #    print "  * {0}".format(open(result, "r").readline().strip())

        cluster.deallocate()

        #df = ccount.execution_profile_dict
        #df.to_pickle('exp.pkl')

    except EnsemblemdError, er:

        print "Ensemble MD Toolkit Error: {0}".format(str(er))
        raise # Just raise the execption again to get the backtrace
