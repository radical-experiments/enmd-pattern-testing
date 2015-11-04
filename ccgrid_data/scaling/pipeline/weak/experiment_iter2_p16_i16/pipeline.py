#!/usr/bin/env python



__author__       = "Ole Weider <ole.weidner@rutgers.edu>"
__copyright__    = "Copyright 2014, http://radical.rutgers.edu"
__license__      = "MIT"
__example_name__ = "Pipeline Example (generic)"

import sys
import os
import argparse
import imp

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

	k1 = Kernel(name="md.amber")
        k1.arguments = ["--mininfile={0}".format(os.path.basename(Kconfig.minimization_input_file)),
                       #"--mdinfile={0}".format(os.path.basename(Kconfig.md_input_file)),
                       "--topfile={0}".format(os.path.basename(Kconfig.top_file)),
                       "--crdfile={0}".format(os.path.basename(Kconfig.initial_crd_file)),
                       "--cycle=%s"%(1)]
        k1.upload_input_data = [Kconfig.minimization_input_file,
                             	Kconfig.top_file,
                             	Kconfig.initial_crd_file]
        k1.cores=1
        k1.upload_input_data = k1.upload_input_data + ['{0} > min1.crd'.format(Kconfig.initial_crd_file)]
        #k1.copy_output_data =['md{0}.crd > $PRE_LOOP/md_{0}_{1}.crd'.format(1,instance)]

	return k1

    def step_2(self,instance):

        k2 = Kernel(name="md.amber")
        k2.arguments = [
                            "--mdinfile={0}".format(os.path.basename(Kconfig.md_input_file)),
                            "--topfile={0}".format(os.path.basename(Kconfig.top_file)),
                            "--cycle=%s"%(1)
                        ]

	k2.upload_input_data = [Kconfig.md_input_file]
        k2.link_input_data = [
                                "$STEP_1/{0}".format(os.path.basename(Kconfig.top_file)),
                                "$STEP_1/md{0}.crd > md{0}.crd".format(1),
                            ]

        k2.cores = 1

        return k2

# ------------------------------------------------------------------------------

if __name__ == "__main__":

    try:

	parser = argparse.ArgumentParser()
        parser.add_argument('--RPconfig', help='link to Radical Pilot related configurations file')
        parser.add_argument('--Kconfig', help='link to Kernel configurations file')

        args = parser.parse_args()

        if args.RPconfig is None:
            parser.error('Please enter a RP configuration file')
            sys.exit(1)
        if args.Kconfig is None:
            parser.error('Please enter a Kernel configuration file')
            sys.exit(0)

        RPconfig = imp.load_source('RPconfig', args.RPconfig)
        Kconfig = imp.load_source('Kconfig', args.Kconfig)

        # Create a new static execution context with one resource and a fixed
        # number of cores and runtime.

        cluster = SingleClusterEnvironment(
            resource=RPconfig.REMOTE_HOST,
            cores=RPconfig.PILOTSIZE,
            walltime=RPconfig.WALLTIME,
            username = RPconfig.UNAME, #username
            project = RPconfig.ALLOCATION, #project
            queue = RPconfig.QUEUE,
            database_url = RPconfig.DBURL
        )

        # Allocate the resources. 
        cluster.allocate()

        # Set the 'instances' of the pipeline to 16. This means that 16 instances
        # of each pipeline step are executed.
        #
        # Execution of the 16 pipeline instances can happen concurrently or
        # sequentially, depending on the resources (cores) available in the
        # SingleClusterEnvironment.
        ccount = CharCount(steps=2,instances=Kconfig.num_CUs)

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
