import os
import sys
import time
import math
import datetime
import numpy as np
import matplotlib.pyplot as plt
from textwrap import wrap

PWD    = os.path.dirname(os.path.abspath(__file__))

#-------------------------------------------------------------------------------

def get_overhead(t1, t2):

    t1 = datetime.datetime.strptime(t1, "%Y-%m-%d %H:%M:%S.%f")
    t2 = datetime.datetime.strptime(t2, "%Y-%m-%d %H:%M:%S.%f")

    return (t2-t1).total_seconds()

#-------------------------------------------------------------------------------

def calc_standard_err(data):

    size = len(data)
    # standard deviation
    std = np.std(data)
    # error
    std_error = std / (math.sqrt(size))

    return std_error

#-------------------------------------------------------------------------------

def minimize_data(data, minval):
    for i in range(len(data)):
        data[i] = data[i] - minval
    return data

#-------------------------------------------------------------------------------

def read_data(name, cycle, cores):

    try:
        r_file = open('../data/data.2.1/' + name + ".csv", "r")
    except IOError:
        print 'Warning: unable to access template file...'

    line_buffer = r_file.readlines()
    r_file.close()

    md_times = []
    md_times_err = []

    exchange_times = []
    exchange_times_err = []

    data_times = []
    data_times_err = []

    overhead_times = []
    

    md_times_new = []
    md_times_stagein = []
    md_times_alloc = []
    md_times_exec = []
    md_times_stageout = []
    md_times_done = []

    exchange_times_new = []
    exchange_times_stagein = []
    exchange_times_alloc = []
    exchange_times_exec = []
    exchange_times_stageout = []
    exchange_times_done = []


    for line in line_buffer:
        row = line.split(';')

        for i in range(len(row)):
            row[i] = row[i].lstrip()


        if (len(row) > 2):
            if row[0].startswith('unit') and row[8].startswith('md_step'):
                if row[7] == cycle:
                    try:
                        row[1] = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[1] = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[4] = datetime.datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[4] = datetime.datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[5] = datetime.datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[5] = datetime.datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[6] = datetime.datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S.%f") 
                    except:
                        row[6] = datetime.datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S")
                        pass

                    md_times_new.append(row[1])
                    md_times_stagein.append(row[2])
                    md_times_alloc.append(row[3])
                    md_times_exec.append(row[4])
                    md_times_stageout.append(row[5])
                    md_times_done.append(row[6])
            
            # if ex
            if row[0].startswith('unit') and row[8].startswith('ex_step'):
                if row[7] == cycle:
                    try:
                        row[1] = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[1] = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[4] = datetime.datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[4] = datetime.datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[5] = datetime.datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        row[5] = datetime.datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
                        pass
                    try:
                        row[6] = datetime.datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S.%f") 
                    except:
                        row[6] = datetime.datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S")
                        pass

                    exchange_times_new.append(row[1])
                    exchange_times_stagein.append(row[2])
                    exchange_times_alloc.append(row[3])
                    exchange_times_exec.append(row[4])
                    exchange_times_stageout.append(row[5])
                    exchange_times_done.append(row[6])

        # step timings
        if (len(row) > 2):
            if row[0].startswith(cycle) and row[1] == 'md_step':
                if type(row[2]) is str:
                    row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")
                if type(row[3]) is str:
                    row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
                md_step_start = row[2]
                md_step_stop  = row[3]
                md_step_duration = row[4]
                #print "md duration: "
                #print md_step_duration
            if row[0].startswith(cycle) and row[1] == 'ex_step':
                if type(row[2]) is str:
                    row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")
                if type(row[3]) is str:
                    row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
                ex_step_start = row[2]
                ex_step_stop  = row[3]
                ex_step_duration = row[4]
            if row[0].startswith(cycle) and row[1] == 'pp_step':
                if type(row[2]) is str:
                    row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")
                if type(row[3]) is str:
                    row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
                pp_step_start = row[2]
                pp_step_stop  = row[3]
                pp_step_duration = [4]

        # enmd overhead step timings
        if (len(row) > 2):
            if row[0].startswith(cycle) and row[1].startswith('md_step_enmd_overhead'):
                if type(row[2]) is str:
                    row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")
                if type(row[3]) is str:
                    row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
                enmd_md_step_start    = row[2]
                enmd_md_step_stop     = row[3]
                enmd_md_step_duration = row[4]
            if row[0].startswith(cycle) and row[1].startswith('ex_step_enmd_overhead'):
                if type(row[2]) is str:
                    row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")
                if type(row[3]) is str:
                    row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
                enmd_ex_step_start    = row[2]
                enmd_ex_step_stop     = row[3]
                enmd_ex_step_duration = row[4]
            if row[0].startswith(cycle) and row[1].startswith('pp_step_enmd_overhead'):
                if type(row[2]) is str:
                    row[2] = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")
                if type(row[3]) is str:
                    row[3] = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
                enmd_pp_step_start    = row[2]
                enmd_pp_step_stop     = row[3]
                enmd_pp_step_duration = row[4]

    #---------------------------------------------------------------------------
    # exec

    # ok
    temp = ( max(md_times_stageout) - min(md_times_exec) ).total_seconds()
    md_times.append(temp)

    temp = ( max(exchange_times_stageout) - min(exchange_times_exec) ).total_seconds()
    exchange_times.append( temp )

    #---------------------------------------------------------------------------
    # data
    
    md_data = []

    data_in = []
    data_out = []
    for i in range(len(md_times_new)):
        d_out = abs( (  md_times_done[i]  - md_times_stageout[i] ).total_seconds() )
        d_in  = abs( (  md_times_alloc[i] - md_times_stagein[i] ).total_seconds() )
        data_in.append(d_in)
        data_out.append(d_out)

    tmp0 = abs( (  max(md_times_exec) - min(md_times_exec) ).total_seconds() )

    #print "exec_diff: "
    #print tmp0

    tmp1 = abs( (  max(md_times_stagein) - min(md_times_stagein) ).total_seconds() )

    #print "stage_in_diff: "
    #print tmp1

    tmp2 = abs( (  max(md_times_stageout) - min(md_times_stageout) ).total_seconds() )

    #print "stage_out_diff: "
    #print tmp2

    

    # OK
    d_out = abs( ( max(exchange_times_done)  - min(exchange_times_stageout) ).total_seconds() )
    d_in  = abs( ( max(exchange_times_alloc) - min(exchange_times_stagein) ).total_seconds() )
    ex_data = (d_in + d_out)

    data_times.append( np.mean(data_in) + ( np.mean(data_out) * (640.0 / cores) ) + ex_data )

    #---------------------------------------------------------------------------
    # overhead, not OK

    tmp_md_exec = sorted(md_times_exec)

    diff = abs((tmp_md_exec[cores-1] - tmp_md_exec[0])).total_seconds()

   
    #temp1      = float(md_step_duration)
    enmd_over1 = float(enmd_md_step_duration)

    #rp_over1 = temp1 - md_times[0] - np.mean(md_data) - enmd_over1


    rp_over1 = diff

    #print "rp over1: "
    #print rp_over1

    #---------------------------------------------------------------------------
    # OK
    temp2      = float(ex_step_duration)
    enmd_over2 = float(enmd_ex_step_duration)

    rp_over2 = temp2 - exchange_times[0] - np.mean(ex_data) - enmd_over2

    #print "rp over2: "
    #print rp_over2
    #---------------------------------------------------------------------------

    rp_overhead = abs( rp_over1 + rp_over2 )


    #---------------------------------------------------------------------------
    # OK
    enmd_over3 = float(enmd_pp_step_duration)

    enmd_overhead   = enmd_over1 + enmd_over2 + enmd_over3

    #print "enmd_over"
    #print enmd_overhead
    #---------------------------------------------------------------------------

    return md_times[0], exchange_times[0], data_times[0], rp_overhead, enmd_overhead  
    
#-------------------------------------------------------------------------------

def gen_graph():

    md_times = []
    md_times_err = []

    exchange_times = []
    exchange_times_err = []

    data_times = []
    data_times_err = []

    rp_overhead_times = []
    rp_overhead_times_err = []

    enmd_overhead_times = []
    enmd_overhead_times_err = []
    
    #---------------------------------------------------------------------------
    # 20/640; 

    # 3 cycles
    name1 = 'execution_profile_rp.session.antons-pc.antons.016712.0018'

    md_times1, \
    exchange_times1, \
    data_times1, \
    rp_overhead1, \
    enmd_overhead1 = read_data(name1, 'cycle_1', 20)

    md_times2, \
    exchange_times2, \
    data_times2, \
    rp_overhead2, \
    enmd_overhead2 = read_data(name1, 'cycle_2', 20)

    md_times3, \
    exchange_times3, \
    data_times3, \
    rp_overhead3, \
    enmd_overhead3 = read_data(name1, 'cycle_3', 20)

    md_times4, \
    exchange_times4, \
    data_times4, \
    rp_overhead4, \
    enmd_overhead4 = read_data(name1, 'cycle_3', 20)

    #---------------------------------------------------------------------------

    temp = [md_times1, md_times2, md_times3, md_times4]
    md_times.append(np.mean(temp))

    temp_list = [md_times1, md_times2, md_times3, md_times4]
    err = calc_standard_err(temp_list)
    md_times_err.append(err)

    temp = [exchange_times3, exchange_times3, exchange_times3, exchange_times4]
    exchange_times.append(np.mean(temp))

    temp_list = [exchange_times3, exchange_times3, exchange_times3, exchange_times4]
    err = calc_standard_err(temp_list)
    exchange_times_err.append(err)
    
    temp = [data_times1, data_times2, data_times3, data_times4]
    data_times.append(np.mean(temp))

    temp_list = [data_times1, data_times2, data_times3, data_times4]
    err = calc_standard_err(temp_list)

    data_times_err.append(err)

    temp = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    rp_overhead_times.append(np.mean(temp))

    temp_list = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    err = calc_standard_err(temp_list)
    rp_overhead_times_err.append(err)

    temp = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    enmd_overhead_times.append(np.mean(temp))

    temp_list = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    err = calc_standard_err(temp_list)
    enmd_overhead_times_err.append(err)

    #---------------------------------------------------------------------------
    # 40/640

    # 4 cycles
    name1 = 'execution_profile_rp.session.antons-pc.antons.016711.0004'

    md_times1, \
    exchange_times1, \
    data_times1, \
    rp_overhead1, \
    enmd_overhead1 = read_data(name1, 'cycle_1', 40)

    md_times2, \
    exchange_times2, \
    data_times2, \
    rp_overhead2, \
    enmd_overhead2 = read_data(name1, 'cycle_2', 40)

    md_times3, \
    exchange_times3, \
    data_times3, \
    rp_overhead3, \
    enmd_overhead3 = read_data(name1, 'cycle_3', 40)

    md_times4, \
    exchange_times4, \
    data_times4, \
    rp_overhead4, \
    enmd_overhead4 = read_data(name1, 'cycle_4', 40)

    #---------------------------------------------------------------------------

    temp = [md_times1, md_times2, md_times3, md_times4]
    md_times.append(np.mean(temp))

    temp_list = [md_times1, md_times2, md_times3, md_times4]
    err = calc_standard_err(temp_list)
    md_times_err.append(err)

    temp = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    exchange_times.append(np.mean(temp))

    temp_list = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    err = calc_standard_err(temp_list)
    exchange_times_err.append(err)
    
    temp = [data_times1, data_times2, data_times3, data_times4]
    data_times.append(np.mean(temp))

    temp_list = [data_times1, data_times2, data_times3, data_times4]
    err = calc_standard_err(temp_list)

    data_times_err.append(err)


    temp = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    rp_overhead_times.append(np.mean(temp))

    temp_list = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    err = calc_standard_err(temp_list)
    rp_overhead_times_err.append(err)

    temp = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    enmd_overhead_times.append(np.mean(temp))

    temp_list = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    err = calc_standard_err(temp_list)
    enmd_overhead_times_err.append(err)

    #---------------------------------------------------------------------------
    # 80/640

    # 4 cycles
    name1 = 'execution_profile_rp.session.antons-pc.antons.016711.0003'


    md_times1, \
    exchange_times1, \
    data_times1, \
    rp_overhead1, \
    enmd_overhead1 = read_data(name1, 'cycle_1', 80)

    md_times2, \
    exchange_times2, \
    data_times2, \
    rp_overhead2, \
    enmd_overhead2 = read_data(name1, 'cycle_2', 80)

    md_times3, \
    exchange_times3, \
    data_times3, \
    rp_overhead3, \
    enmd_overhead3 = read_data(name1, 'cycle_3', 80)

    md_times4, \
    exchange_times4, \
    data_times4, \
    rp_overhead4, \
    enmd_overhead4 = read_data(name1, 'cycle_4', 80)

    #---------------------------------------------------------------------------

    temp = [md_times1, md_times2, md_times3, md_times4]
    md_times.append(np.mean(temp))

    temp_list = [md_times1, md_times2, md_times3, md_times4]
    err = calc_standard_err(temp_list)
    md_times_err.append(err)

    temp = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    exchange_times.append(np.mean(temp))

    temp_list = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    err = calc_standard_err(temp_list)
    exchange_times_err.append(err)
    
    temp = [data_times1, data_times2, data_times3, data_times4]
    data_times.append(np.mean(temp))

    temp_list = [data_times1, data_times2, data_times3, data_times4]
    err = calc_standard_err(temp_list)

    data_times_err.append(err)


    temp = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    rp_overhead_times.append(np.mean(temp))

    temp_list = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    err = calc_standard_err(temp_list)
    rp_overhead_times_err.append(err)

    temp = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    enmd_overhead_times.append(np.mean(temp))

    temp_list = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    err = calc_standard_err(temp_list)
    enmd_overhead_times_err.append(err)

    #---------------------------------------------------------------------------
    # 160/640

    # 4 cycles
    name1 = 'execution_profile_rp.session.antons-pc.antons.016711.0000'

    md_times1, \
    exchange_times1, \
    data_times1, \
    rp_overhead1, \
    enmd_overhead1 = read_data(name1, 'cycle_1', 160)

    md_times2, \
    exchange_times2, \
    data_times2, \
    rp_overhead2, \
    enmd_overhead2 = read_data(name1, 'cycle_2', 160)

    md_times3, \
    exchange_times3, \
    data_times3, \
    rp_overhead3, \
    enmd_overhead3 = read_data(name1, 'cycle_3', 160)

    md_times4, \
    exchange_times4, \
    data_times4, \
    rp_overhead4, \
    enmd_overhead4 = read_data(name1, 'cycle_4', 160)

    #---------------------------------------------------------------------------

    temp = [md_times1, md_times2, md_times3, md_times4]
    md_times.append(np.mean(temp))

    temp_list = [md_times1, md_times2, md_times3, md_times4]
    err = calc_standard_err(temp_list)
    md_times_err.append(err)

    temp = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    exchange_times.append(np.mean(temp))

    temp_list = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    err = calc_standard_err(temp_list)
    exchange_times_err.append(err)
    
    temp = [data_times1, data_times2, data_times3, data_times4]
    data_times.append(np.mean(temp))

    temp_list = [data_times1, data_times2, data_times3, data_times4]
    err = calc_standard_err(temp_list)

    data_times_err.append(err)


    temp = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    rp_overhead_times.append(np.mean(temp))

    temp_list = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    err = calc_standard_err(temp_list)
    rp_overhead_times_err.append(err)

    temp = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    enmd_overhead_times.append(np.mean(temp))

    temp_list = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    err = calc_standard_err(temp_list)
    enmd_overhead_times_err.append(err)

    #---------------------------------------------------------------------------
    # 320/640

    # 4 cycles; ok
    name1  = 'execution_profile_rp.session.antons-pc.antons.016710.0043'

    md_times1, \
    exchange_times1, \
    data_times1, \
    rp_overhead1, \
    enmd_overhead1 = read_data(name1, 'cycle_1', 320)

    md_times2, \
    exchange_times2, \
    data_times2, \
    rp_overhead2, \
    enmd_overhead2 = read_data(name1, 'cycle_2', 320)

    md_times3, \
    exchange_times3, \
    data_times3, \
    rp_overhead3, \
    enmd_overhead3 = read_data(name1, 'cycle_3', 320)

    md_times4, \
    exchange_times4, \
    data_times4, \
    rp_overhead4, \
    enmd_overhead4 = read_data(name1, 'cycle_4', 320)

    #---------------------------------------------------------------------------

    temp = [md_times1, md_times2, md_times3, md_times4]
    md_times.append(np.mean(temp))

    temp_list = [md_times1, md_times2, md_times3, md_times4]
    err = calc_standard_err(temp_list)
    md_times_err.append(err)

    temp = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    exchange_times.append(np.mean(temp))

    temp_list = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    err = calc_standard_err(temp_list)
    exchange_times_err.append(err)
    
    temp = [data_times1, data_times2, data_times3, data_times4]
    data_times.append(np.mean(temp))

    temp_list = [data_times1, data_times2, data_times3, data_times4]
    err = calc_standard_err(temp_list)

    data_times_err.append(err)


    temp = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    rp_overhead_times.append(np.mean(temp))

    temp_list = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    err = calc_standard_err(temp_list)
    rp_overhead_times_err.append(err)

    temp = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    enmd_overhead_times.append(np.mean(temp))

    temp_list = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    err = calc_standard_err(temp_list)
    enmd_overhead_times_err.append(err)

    #---------------------------------------------------------------------------
    # 640/640

    # 4 cycles; ok
    name1 = 'execution_profile_rp.session.antons-pc.antons.016710.0040'

    md_times1, \
    exchange_times1, \
    data_times1, \
    rp_overhead1, \
    enmd_overhead1 = read_data(name1, 'cycle_1', 640)

    md_times2, \
    exchange_times2, \
    data_times2, \
    rp_overhead2, \
    enmd_overhead2 = read_data(name1, 'cycle_2', 640)

    md_times3, \
    exchange_times3, \
    data_times3, \
    rp_overhead3, \
    enmd_overhead3 = read_data(name1, 'cycle_3', 640)

    md_times4, \
    exchange_times4, \
    data_times4, \
    rp_overhead4, \
    enmd_overhead4 = read_data(name1, 'cycle_4', 640)

    #---------------------------------------------------------------------------

    temp = [md_times1, md_times2, md_times3, md_times4]
    md_times.append(np.mean(temp))

    temp_list = [md_times1, md_times2, md_times3, md_times4]
    err = calc_standard_err(temp_list)
    md_times_err.append(err)

    temp = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    exchange_times.append(np.mean(temp))

    temp_list = [exchange_times1, exchange_times2, exchange_times3, exchange_times4]
    err = calc_standard_err(temp_list)
    exchange_times_err.append(err)
    
    temp = [data_times1, data_times2, data_times3, data_times4]
    data_times.append(np.mean(temp))

    temp_list = [data_times1, data_times2, data_times3, data_times4]
    err = calc_standard_err(temp_list)

    data_times_err.append(err)


    temp = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    rp_overhead_times.append(np.mean(temp))

    temp_list = [rp_overhead1, rp_overhead2, rp_overhead3, rp_overhead4]
    err = calc_standard_err(temp_list)
    rp_overhead_times_err.append(err)

    temp = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    enmd_overhead_times.append(np.mean(temp))

    temp_list = [enmd_overhead1, enmd_overhead2, enmd_overhead3, enmd_overhead4]
    err = calc_standard_err(temp_list)
    enmd_overhead_times_err.append(err)

    #---------------------------------------------------------------------------

    enmd_core_times = []
    enmd_core_times_err = []

    # 20/640

    # 
    ov1 = get_overhead('2015-10-03 15:41:32.076960', '2015-10-03 15:41:37.038074')
    ov2 =  get_overhead('2015-10-03 15:35:21.911598', '2015-10-03 15:35:55.901527')
    enmd_core_times.append(ov1 + ov2)
    enmd_core_times_err.append(0.023)

    # 40/640
    ov1 = get_overhead('2015-10-03 15:41:31.076960', '2015-10-03 15:41:35.038074')
    # f
    ov2 =  get_overhead('2015-10-03 15:35:23.911598', '2015-10-03 15:35:54.901527')
    enmd_core_times.append(ov1 + ov2)
    enmd_core_times_err.append(0.023)

    # 80/640
    ov1 = get_overhead('2015-10-03 14:24:20.050102', '2015-10-03 14:24:23.378524')
    ov2 =  get_overhead('2015-10-03 15:35:23.911598', '2015-10-03 15:35:42.901527')
    enmd_core_times.append(ov1 + ov2)
    enmd_core_times_err.append(0.023)

    # 160/640
    ov1 = get_overhead('2015-10-02 22:50:55.646717', '2015-10-02 22:51:01.392015')
    ov2 =  get_overhead('2015-10-02 23:27:55.165851', '2015-10-02 23:28:26.576013')
    enmd_core_times.append(ov1 + ov2)
    enmd_core_times_err.append(0.023)

    # 320/640
    ov1 = get_overhead('2015-10-02 17:42:54.244845', '2015-10-02 17:42:59.339712')
    ov2 =  get_overhead('2015-10-02 19:46:32.738925', '2015-10-02 19:46:56.483119')
    enmd_core_times.append(ov1 + ov2)
    enmd_core_times_err.append(0.023)


    # 640/640
    ov1 = get_overhead('2015-10-02 17:16:31.229571', '2015-10-02 17:16:36.655848')
    ov2 =  get_overhead('2015-10-02 17:33:25.414652', '2015-10-02 17:33:52.622988')
    enmd_core_times.append(ov1 + ov2)
    enmd_core_times_err.append(0.023)


    # Five subplots, the axes array is 1-d
    f, axarr = plt.subplots(3, sharex=True)

    N = 6

    ind = np.arange(N)   
    width = 0.2   
    plt.rc("font", size=12)

    data_times_bottom = []
    md_bottom = []
    ex_bottom = []
    for i in range(0,6):
        ex_bottom.append(data_times[i])
        md_bottom.append(data_times[i] + exchange_times[i])


    p0 = axarr[2].bar(ind+0.5*width, rp_overhead_times,   width, yerr=rp_overhead_times_err, color='red', edgecolor = "white")
    p1 = axarr[2].bar(ind-1.5*width, enmd_overhead_times, width, yerr=enmd_overhead_times_err, color='darkslategray', edgecolor = "white")
    p2 = axarr[2].bar(ind-0.5*width, enmd_core_times,     width, yerr=enmd_core_times_err, color='olive', edgecolor = "white")
    
    p3 = axarr[1].bar(ind-width, data_times, width, yerr=data_times_err, color='black', edgecolor = "white")
    p4 = axarr[1].bar(ind, exchange_times, width, yerr=exchange_times_err, color='blue', edgecolor = "white")

    p5 = axarr[0].bar(ind-0.5*width, md_times, width, yerr=md_times_err, color='darkgreen', edgecolor = "white")
    
    #---------------------------------------------------------------------------

    axarr[0].set_ylabel('Time in seconds')
    axarr[1].set_ylabel('Time in seconds')
    axarr[2].set_ylabel('Time in seconds')
    
    text ='Performance Characterization of T-REMD Alanine Dipeptide with Amber Kernel on SuperMIC. (rp-0.35; 8/8/8)'
    axarr[0].set_title('\n'.join(wrap(text,70)))

    plt.xticks(ind, ('20/640', '40/640', '80/640', '160/640', '320/640', '640/640') )

    ax = plt.gca()
    ax.yaxis.grid(True, which='major')

    plt.xlabel('Pilot size/Replicas')

    axarr[0].set_yticks(np.arange(0,5000,500))
    axarr[1].set_yticks(np.arange(0,50,5))
    axarr[2].set_yticks(np.arange(0,50,5))

    
    axarr[0].yaxis.grid(True, which='major')
    axarr[1].yaxis.grid(True, which='major')
    axarr[2].yaxis.grid(True, which='major')

    axarr[0].legend((p5[0], p4[0], p3[0], p2[0], p1[0], p0[0]), ('MD-step-times', 'Exchange-step times', 'Data-movement times', 'ENMD-core-overhead', 'ENMD-pattern-overhead', 'RP-overhead'))
    

    plt.savefig('../plots/strong-scaling-04.10.2015.pdf')


#-------------------------------------------------------------------------------

if __name__ == "__main__":
    
    gen_graph()
