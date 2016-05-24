#!/bin/bash

## NOTES: This script is to automate the process of running the workflows scripts with different 
## configurations. You can log on to a persistent machine and use tmux to open a new session. 
## INSTANCES is the number of simulations to be executed
## CORES is the number of cores to be reserved
## (INSTANCE,CORE) gives us a data point.
## ITERS is the number of times the experiment is to be repeated for every (INSTANC,CORE)
## datapoint in order to obtain an average and stddev.
## CORES_PER_SIM is the number of cores per simulation

## Requirements: Open the resource config file, set the username, walltime(estimate) and 
## number of iterations. Set ITERS, INSTANCES, CORES and CORES_PER_SIM in this file.
## Check the entire script to comment/uncomment specific lines for weak/strong scaling
## experiments.


## TMUX quick-brief:
## tmux new -s <session_name>
## (make sure you enable the virtualenv again in this new session)
## Ctrl+d to detach from the session
## tmux a -t <session_name> to attach back to the session
## DO NOT EXIT THE SESSION. ONLY DETACH !


export RADICAL_ENMD_PROFILING=1
export RADICAL_ENMD_VERBOSE=info
export RADICAL_PILOT_PROFILE=True

ITERS="1"			# No. of trials for averaging results
#INSTANCES="256 512 1024 2048 4096"       #Weak scaling
INSTANCES="8192"                            #Strong scaling
#CORES="8224"
#CORES="1056 2080 4128"

CORES_PER_SIM="1"		# Cores per simulation

ORIG="`pwd`"

#rm -rf dait
mkdir -p data				# Folder with all the data

for iter in $ITERS
do
#	for size in $CORES
#	do
		for inst in $INSTANCES
		do
#				nodes=$(( $(( $size - 32 )) / $CORES_PER_SIMS ))
#				if [ $inst -eq $nodes ]; 
#				then
				size=$(( inst*$CORES_PER_SIM + 32 ))
				export EXPERIMENT=experiment_iter${iter}_p${size}_i${inst}
				cd $ORIG/data
				rm -rf $EXPERIMENT
				mkdir -p $EXPERIMENT
				cd $EXPERIMENT					# Folder for this datapoint

				# Copy necessary files and folders into the above folder				
				cp ../../extasy_amber_coco.py .			#gmxcoco
				cp ../../inp_files . -r
				cp ../../kernel_defs . -r

				# Replace variables in the config files with datapoint values				
				cat ../../bluewaters.rcfg | sed -e "s/CORES/$size/g" > bluewaters.rcfg					
				cat ../../cocoamber.wcfg | sed -e "s/INSTANCES/$inst/g" | sed -e "s/CPS/$CORES_PER_SIM/g" > cocoamber.wcfg			

				# Run the script with the specific datapoints
				# You can comment the following line and run this script to see how the folder structure 
				# comes out
				python extasy_amber_coco.py --RPconfig bluewaters.rcfg --Kconfig cocoamber.wcfg
#				fi
		done
#	done
done

