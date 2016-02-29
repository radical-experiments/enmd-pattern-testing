#!/usr/bin/env python



__author__       = "Ole Weider <ole.weidner@rutgers.edu>"
__copyright__    = "Copyright 2014, http://radical.rutgers.edu"
__license__      = "MIT"
__example_name__ = "Bag of Tasks Example (generic)"

import sys
import os
import json
import random

from radical.ensemblemd import Kernel
from radical.ensemblemd import BagofTasks
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SingleClusterEnvironment


# ------------------------------------------------------------------------------
#
class CharCount(BagofTasks):
    """The CalculateChecksums class implements a Bag of Tasks. Since there
        is no explicit "Bag of Tasks" pattern template, we inherit from the
        radical.ensemblemd.Pipeline pattern and define just one step.
    """

    def __init__(self, steps, instances):
        BagofTasks.__init__(self, steps, instances)

    # def step_1(self, instance):
    #     """This step downloads a sample UTF-8 file from a remote websever and
    #        calculates the SHA1 checksum of that file. The checksum is written
    #        to an output file and tranferred back to the host running this
    #        script.
    #     """
    #     k = Kernel(name="misc.chksum")
    #     k.arguments            = ["--inputfile=UTF-8-demo.txt", "--outputfile=checksum{0}.sha1".format(instance)]
    #     k.upload_input_data  = "UTF-8-demo.txt"
    #     k.download_output_data = "checksum{0}.sha1".format(instance)
    #     return k


    def step_1(self, instance):
        """The first step of the pipeline creates a 1 MB ASCI file.
        """
        k = Kernel(name="misc.mkfile")
        k.arguments = ["--size=1000000", "--filename=asciifile-{0}.dat".format(instance)]
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
        k.link_input_data      = "$STEP_1/asciifile-{0}.dat".format(instance)
        k.download_output_data = "cfreqs-{0}.dat".format(instance)
        k.cores = 1
        return k


def find_profile(files):
    for item in files:
        if item.find('execution_profile') != -1:
            return item

# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

    
    try:

        # Create a new static execution context with one resource and a fixed
        # number of cores and runtime.

	scale = [1,16,32,64,128]
        num_of_iterations = 4
        #scale = [1]
        #num_of_iterations = 1
        pairings = []

        for core in scale:
            for i in range(0,num_of_iterations):
                pairings.append((core,i))

        random.shuffle(pairings)



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
            ccount = CharCount(instances=1,steps=2)
            cluster.run(ccount)
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

        # Set the 'instances' of the pipeline to 16. This means that 16 instances
        # of each pipeline step are executed.
        #
        # Execution of the 16 pipeline instances can happen concurrently or
        # sequentially, depending on the resources (cores) available in the
        # SingleClusterEnvironment.
        # ccount = CalculateChecksums(steps=1,instances=16)

        # os.system('wget -q -o UTF-8-demo.txt http://gist.githubusercontent.com/oleweidner/6084b9d56b04389717b9/raw/611dd0c184be5f35d75f876b13604c86c470872f/gistfile1.txt')

        # cluster.run(ccount)

        # # Print the checksums
        # print "\nResulting checksums:"
        # import glob
        # for result in glob.glob("checksum*.sha1"):
        #     print "  * {0}".format(open(result, "r").readline().strip())


    except EnsemblemdError, er:

        print "Ensemble MD Toolkit Error: {0}".format(str(er))
        raise # Just raise the execption again to get the backtrace
