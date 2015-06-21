#!/bin/bash

ITERS="1 2 3"
INSTANCES="16 32 64 128"
CORES="16 32 64 128"

ORIG="`pwd`"

rm -rf data
mkdir -p data

for iter in $ITERS
do
	for size in $CORES
	do
		for inst in $INSTANCES
		do
			if [ $inst -ge $size ];
			then
				export EXPERIMENT=experiment_iter${iter}_p${size}_i${inst}
				cd $ORIG/data
				rm -rf $EXPERIMENT
				mkdir -p $EXPERIMENT
				cd $EXPERIMENT
				cp ../../extasy_gromacs_lsdmap.py .
				cp ../../workflow.sh .
				cat ../../stampede.rcfg | sed -e "s/CORES/$size/g" > stampede.rcfg
				cat ../../gromacslsdmap.wcfg | sed -e "s/INSTANCES/$inst/g" > gromacslsdmap.wcfg
				python extasy_gromacs_lsdmap.py --RPconfig stampede.rcfg --Kconfig gromacslsdmap.wcfg
				#while [ ! -f $ORIG/data/$EXPERIMENT/exp_$size_$inst.pkl ]
				#do
				#	sleep 0
				#done
				#mutt -s "$iter/$size/$inst" b.vivek91@gmail.com < extasy.log			
			fi
		done
	done
done
