This folder contains data and plots generated from EnsembleMD toolkit (0.3.14). The data is arranged as follows:

1) partA: This folder contains weak scaling data for the pipeline, SAL, RE patterns. 
Kernels: 'mkfile', 'ccount'
Resource: XSEDE.Comet
Scale range: 24-192
Purpose: Characterize each of the patterns. Decompose the time to completion to present execution time, overheads, data transfer time.
Comments: Within folder 'partA', there are 3 folders pipeline, sal, re which hold the respective data and plots. Data is present in folders named 'experiment\_p{0}\_i{1}' where '0' is the cores used and '1' is the number of instances/tasks. The plotting script 'merge\_plot.ipynb' produces the plot with merged results from all patterns. The 'plotter\_\*.pynb' plot the specific pattern plots.

2) partB: This folder contains weak scaling data for the SAL pattern.
Kernels: 'gromacs','lsdmap'
Resource: XSEDE.Comet
Scale range: 24-192
Purpose: Observe if there is any change in the overheads due to change in kernel. Validate the hypoethesis that changing the kernels (keeping all other parameters constant) does not effect the overheads and hence the TTC.
Comments: Within folder 'partB', the data exists in folders named 'experiment\_p{0}\_i{1}' where '0' is the cores used and '1' is the number of instances/tasks. The plotting script 'plotter.ipynb' produce the plot which contains the execution time and overheads.

3) partC: This folder contains data for both weak and strong tests for the SAL, RE patterns.
Kernels: 'amber' and 'coco' for SAL pattern, 'amber' and 'exchange' (temperature) for RE pattern
Resource: XSEDE.Stampede for SAL, XSEDE.SuperMIC for RE
Purpose: Observe the performance of SAL and RE pattern (and thus EnsembleMD toolkit) in strong and weak scaling tests.
System used: alanine dipeptide molecule with 2881 atoms.
Comments:Within folder 'partA', there are 2 folders sal, re which hold the respective data and plots. For SAL pattern, data is present in folders named '{2}/experiment\_p{0}\_i{1}' where '0' is the cores used, '1' is the number of instances/tasks and {2} is either 'strong' or 'weak'. The plotting script 'plotter.ipynb' produces the output graph with weak scaling data. For RE pattern, data can found in 'data' folder, plotting scripts can be found in 'bin' and the graphs in 'plots'.
