import datetime
import numpy as np
import math

if __name__ == '__main__':

	size=[16,32,64,128,256,512]
	trials = [1,2,3]
	for k in size:
		temp=[]
		for t in trials:
			f1 = open('experiment_iter{1}_p{0}_i{0}/record.data'.format(k,t),'r')
			data = f1.readlines()
			record = {}
			for l in data:
				record[l.split('=')[0].strip()] = datetime.datetime.strptime(l.split('=')[1].strip(), "%Y-%m-%d %H:%M:%S.%f")
	
			pre_active = (record['Allocating']-record['Start']).total_seconds() + (record['Executing'] - record['Allocated']).total_seconds() 

			active = (record['Pilot wait']-record['Executing']).total_seconds() + (record['Preloop wait']-record['Pilot active']).total_seconds() + (record['Sims-1 wait']-record['Preloop done']).total_seconds() + (record['Sims-2 wait']-record['Sims-1 done']).total_seconds() + (record['Ana-1 wait']-record['Sims-2 done']).total_seconds() + (record['Ana-2 wait']-record['Ana-1 done']).total_seconds() + (record['Iter done']-record['Ana-2 done']).total_seconds() 

			post_active = (record['Deallocating']-record['Iter done']).total_seconds() 
	
			enmd_time = pre_active + active + post_active

			temp.append(enmd_time)
		print 'Size: {0}, Average: {1}, Error: {2}'.format(k,np.average(temp),np.std(temp)/math.sqrt(len(trials)))
