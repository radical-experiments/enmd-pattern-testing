Experiment Description
----------------------

The SAL execution pattern was used with the following specifications:

* simulation\_instances = [16,32,64,128], kernel = "/bin/sleep 10", data\_staged = None
* analysis\_instances = 1, kernel = "/bin/sleep 5", data\_staged = None
* iterations = 1.

* The # of cores used is always equal to the # of simulation instances to keep # of generations = 1.
* Remote host = xsede.stampede
