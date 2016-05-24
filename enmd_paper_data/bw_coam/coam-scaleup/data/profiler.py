import pandas as pd
import glob
import os
import numpy as np
import math
import matplotlib.pyplot as plt

# Time extraction - possibly not used
#---------------------------------------------------------------------------------------
def extract_time(t1,t2,t3=None,t4=None):

	if t3 is not None:

		t1=int(t1)
		t2=int(t2)
		t3=int(t3)
		t4=int(t4)
		return ((t2-t1)+(t4-t3))

	else:

		t1=int(t1)
		t2=int(t2)
		return (t2-t1)

# Useful for strong scaling
#---------------------------------------------------------------------------------------
def collapse_ranges(ranges):

	final = []

	# sort ranges into a copy list
	_ranges = sorted (ranges, key=lambda x: x[0])

	START = 0
	END = 1

	base = _ranges[0] # smallest range

	for _range in _ranges[1:]:
		if _range[START] <= base[END]:
			# ranges overlap -- extend the base
			base[END] = max(base[END], _range[END])

		else:

			# ranges don't overlap -- move base to final, and current _range
			# becomes the new base
			final.append(base)
			base = _range

    	# termination: push last base to final
    	final.append(base)

    	return final


def get_Toverlap(df, start_state, stop_state):
 
 	overlap = 0
	ranges = []

	for index, row in df.iterrows():
		if not pd.isnull(row[start_state]) and not pd.isnull(row[stop_state]):
			ranges.append([row[start_state], row[stop_state]])

	for crange in collapse_ranges(ranges):
		overlap += crange[1] - crange[0]

	return overlap
#---------------------------------------------------------------------------------------


# Extract individual components from DF
#---------------------------------------------------------------------------------------
def extract_timing_info(df, inst):

	filter_df = df[['step','Executing','AgentStagingOutputPending']]

	sim_df = filter_df[:2*inst]
	ana_df = filter_df[2*inst:]

	sim_df['AgentStagingOutputPending'] = pd.to_numeric(sim_df['AgentStagingOutputPending'],errors='raise')

	print type(sim_df["AgentStagingOutputPending"][0])

	# Extract simulation time
	# -----------------------------------------------------------------------------------------
	sim_k1 = get_Toverlap(sim_df[:inst], 'Executing', 'AgentStagingOutputPending')
	sim_k2 = get_Toverlap(sim_df[inst:], 'Executing', 'AgentStagingOutputPending')

	sim_time = sim_k1 + sim_k2
	#print sim_time
	#sim_time = 0

	#print 'Exec 1: ', (max(sim_df[:inst]['AgentStagingOutputPending']) - min(sim_df[:inst]['Executing'])) 
	#print 'Exec 2: ',(max(sim_df[inst:]['AgentStagingOutputPending']) - min(sim_df[inst:]['Executing']))


	# Extract analysis time
	# -----------------------------------------------------------------------------------------
	ana_time = 0
	try:
		per_unit_exec_time  = list()
		for row in ana_df.iterrows():
			step,t1,t2 = row[1:][0]
			ana_time += extract_time(t1,t2)
	except:
		ana_time = 0

	return [sim_time,ana_time]
#---------------------------------------------------------------------------------------

def plotter(data_df, err_df, resource, cps, type):

	# Ten shades of gray
	colormap = plt.cm.binary(np.linspace(0, 1, 10))

	ax1 = data_df.plot(kind='bar',stacked=False,
			title='Amber-CoCo extasy workflow executed on {0}'.format(resource),
			color=[colormap[4],colormap[6]],
               		ylim=(0,3000),
               		fontsize=20,
               		rot=0,
               		yerr=err_df,
               		position=0)

	ax1.set_xlabel('No. of simulations/Cores (cores/sim = {0})'.format(cps),fontsize=20)
	ax1.set_ylabel('Time (seconds)',fontsize=20)
	ax1.set_title(ax1.get_title(),fontsize=20)
	ax1.legend(fontsize=20,loc='upper right')

	fig = plt.gcf()
    	fig.set_size_inches(20,8)
    	fig.savefig('plot_grlsd_{0}_{1}.png'.format(resource,type), dpi=100)


def weak_scaling(instances, cores_per_sim, cores, trials, resource):

	data_df = pd.DataFrame(columns=[ 'sim execution time', 'ana execution time' ] )
	err_df = pd.DataFrame(columns=[ 'sim execution time', 'ana execution time' ] )

	for i in instances:

		sim_list = []
		ana_list = []
		total_cores = i*cores_per_sim
		for t in range(trials):

			print 'Trial, instances: ',t+1,i
			print 'experiment_iter{0}_p{2}_i{1}/execution*.csv'.format(t+1, i, total_cores + 32)
			fname = glob.glob('experiment_iter{0}_p{2}_i{1}/execution*.csv'.format(t+1, i, total_cores + 32))[0]

			exec_df = pd.read_csv('{0}'.format(fname), header=0, sep=',', skipinitialspace=True)

			
			exec_time = extract_timing_info(exec_df, i)

			sim_list.append(exec_time[0])
			ana_list.append(exec_time[1])


		data_df.loc["{0}/{1}".format(i, total_cores)] = [ np.average(sim_list), np.average(ana_list) ]
		err_df.loc["{0}/{1}".format(i, total_cores)] = [ np.std(sim_list)/math.sqrt(trials), np.std(ana_list)/math.sqrt(trials)]

	plotter(data_df,err_df, resource, cores_per_sim, 'weak')
	

def strong_scaling(instances, cores_per_sim, cores, trials, resource):

	data_df = pd.DataFrame(columns=[ 'sim execution time', 'ana execution time' ] )
	err_df = pd.DataFrame(columns=[ 'sim execution time', 'ana execution time' ] )

	for c in cores:

		sim_list = []
		ana_list = []
		for t in range(trials):

			print 'Trial, instances, cores: ',t,i,c
			#print 'experiment_iter{0}_p{2}_i{1}/execution*.csv'.format(t+1, i, total_cores + 32)
			fname = glob.glob('experiment_iter{0}_p{2}_i{1}/execution*.csv'.format(t+1, instances, c+32))[0]

			exec_df = pd.read_csv('{0}'.format(fname), header=0, sep=',', skipinitialspace=True)

			exec_time = extract_timing_info(exec_df, i)
			sim_list.append(exec_time[0])
			ana_list.append(exec_time[1])


		data_df.loc["{0}/{1}".format(i, c)] = [ np.average(sim_list), np.average(ana_list) ]
		err_df.loc["{0}/{1}".format(i, c)] = [ np.std(sim_list)/math.sqrt(trials), np.std(ana_list)/math.sqrt(trials)]

	plotter(data_df,err_df, resource, cores_per_sim, 'strong')


if __name__ == "__main__":


	trials = 1
	resource = "NCSA_Bluewaters"

	# Weak scaling
	instances = [256,512,1024,2048]
	#instances = [2048]
	cores_per_sim = 32
	cores = [ (i*cores_per_sim + 32) for i in instances ]	
	weak_scaling(instances, cores_per_sim, cores, trials, resource)

	# Strong scaling
	instances = 128
	cores_per_sim = 32
	cores = [ (i*cores_per_sim ) for i in [16,32,64,128] ]
	#strong_scaling(instances, cores_per_sim, cores, trials, resource)

	
	
