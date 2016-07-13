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


	def simulation_stage(self, iteration, instance):
		k = Kernel(name="misc.idle")
		k.arguments = ["--duration=10"]
		return [k]

	def analysis_stage(self, iteration, instance):
		k = Kernel(name="misc.idle")
		k.arguments = ["--duration=5"]
		return [k]


# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

	try:

		# Create a new resource handle with one resource and a fixed
		# number of cores and runtime.
		cluster = SingleClusterEnvironment(
			resource="xsede.stampede",
			cores=128,
			walltime=10,
			username='vivek91',
			queue='development',
			project='TG-MCB090174',
			database_url='mongodb://entk_user:entk_user@ds029224.mlab.com:29224/entk_doc',
			)

		# Allocate the resources. 
		cluster.allocate()

		# We set both the the simulation and the analysis stage 'instances' to 16.
		# If they
		mssa = MSSA(iterations=1, simulation_instances=128, analysis_instances=1)

		cluster.run(mssa)

		cluster.deallocate()
		cluster.profile(mssa)

	except EnsemblemdError, er:

		print "Ensemble MD Toolkit Error: {0}".format(str(er))
		raise # Just raise the execption again to get the backtrace

