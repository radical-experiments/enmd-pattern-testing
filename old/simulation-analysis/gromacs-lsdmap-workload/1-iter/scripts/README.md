To generate the data
--------------------

* Install EnsembleMD:

```
virtualenv $HOME/enmd
source $HOME/enmd/bin/activate
pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.git@$devel#egg=radical.ensemblemd
export RADICAL_ENMD_VERBOSE=info
```

* Set the user credentials in stampede.rcfg
* Set required parameters in gromacslsdmap.wcfg (or leave as default)
* Set parameters (iters, cores, instances) in runme.sh (or leave as default)
* Run runme.sh using ```sh runme.sh```


