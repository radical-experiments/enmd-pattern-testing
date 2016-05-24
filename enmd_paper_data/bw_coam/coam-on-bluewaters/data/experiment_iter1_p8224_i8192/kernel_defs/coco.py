#!/usr/bin/env python

"""A kernel that creates a new ASCII file with a given size and name.
"""

__author__    = "The ExTASY project"
__copyright__ = "Copyright 2015, http://www.extasy-project.org/"
__license__   = "MIT"

from copy import deepcopy

from radical.ensemblemd.exceptions import ArgumentError
from radical.ensemblemd.exceptions import NoKernelConfigurationError
from radical.ensemblemd.engine import get_engine
from radical.ensemblemd.kernel_plugins.kernel_base import KernelBase

# ------------------------------------------------------------------------------

_KERNEL_INFO = {

    "name":         "custom.coco",
    "description":  "Creates a new file of given size and fills it with random ASCII characters.",
    "arguments":   {"--grid=":
                        {
                            "mandatory": True,
                            "description": "No. of grid points"
                        },
                    "--dims=":
                        {
                            "mandatory": True,
                            "description": "No. of dimensions"
                        },
                    "--frontpoints=":
                        {
                            "mandatory": True,
                            "description": "No. of frontpoints = No. of simulation CUs"
                        },
                    "--topfile=":
                        {
                            "mandatory": True,
                            "description": "Reference coordinates filename"
                        },
                    "--mdfile=":
                        {
                            "mandatory": True,
                            "description": "Trajectory filenames"
                        },
                    "--output=":
                        {
                            "mandatory": True,
                            "description": "Output filename for postexec"
                        },
                    "--atom_selection=":
                        {
                            "mandatory": True,
                            "description": "Selection of atoms - None(all) or protein"
                        },
                    "--nompi=":
                        {
                            "mandatory": False,
                            "description": "If we want to run coco serially"
                        }
                    },
    "machine_configs": 
    {
        "*": {
            "environment"   : {"FOO": "bar"},
            "pre_exec"      : [],
            "executable"    : "pyCoCo",
            "uses_mpi"      : True
        },

        "ncsa.bw":
        {
            "environment"   : {"FOO": "bar"},
            "pre_exec"      : [
                                 "module use --append /projects/sciteam/gkd/modules",
                                 "module load openmpi",
                                 "module load bwpy",
                                 "source /projects/sciteam/gkd/virtenvs/coco_test/bin/activate",
                                 "export PATH=$PATH:/projects/sciteam/gkd/virtenvs/coco_test/bin",
                                 "export PYTHONPATH=$PYTHONPATH:/projects/sciteam/gkd/virtenvs/coco_test/lib/python-2.7/site-packages"],
            "executable"    : ["pyCoCo"],
            "uses_mpi"      : True
        }
    }
}


# ------------------------------------------------------------------------------
#
class kernel_coco(KernelBase):

    def __init__(self):

        super(kernel_coco, self).__init__(_KERNEL_INFO)
     	"""Le constructor."""
        		
    # --------------------------------------------------------------------------
    #
    @staticmethod
    def get_name():
        return _KERNEL_INFO["name"]
        

    def _bind_to_resource(self, resource_key):
        
        """(PRIVATE) Implements parent class method. 
        """
        if resource_key not in _KERNEL_INFO["machine_configs"]:
            if "*" in _KERNEL_INFO["machine_configs"]:
                # Fall-back to generic resource key
                resource_key = "*"
            else:
                raise NoKernelConfigurationError(kernel_name=_KERNEL_INFO["name"], resource_key=resource_key)

        cfg = _KERNEL_INFO["machine_configs"][resource_key]

        executable = cfg["executable"]
        
        if self.get_arg("--nompi="):
            arguments = ['--grid','{0}'.format(self.get_arg("--grid=")),
                        '--dims','{0}'.format(self.get_arg("--dims=")),
                        '--frontpoints','{0}'.format(self.get_arg("--frontpoints=")),
                        '--topfile','{0}'.format(self.get_arg("--topfile=")),
                        '--mdfile','{0}'.format(self.get_arg("--mdfile=")),
                        '--output','{0}'.format(self.get_arg("--output=")),
                        '--logfile','coco.log', 
                        '--nompi',
                        '--selection','{0}'.format(self.get_arg("--atom_selection="))
                        ]
        else:
            arguments = ['--grid','{0}'.format(self.get_arg("--grid=")),
                        '--dims','{0}'.format(self.get_arg("--dims=")),
                        '--frontpoints','{0}'.format(self.get_arg("--frontpoints=")),
                        '--topfile','{0}'.format(self.get_arg("--topfile=")),
                        '--mdfile','{0}'.format(self.get_arg("--mdfile=")),
                        '--output','{0}'.format(self.get_arg("--output=")),
                        '--logfile','coco.log',
                        '--selection','{0}'.format(self.get_arg("--atom_selection="))
                        ]                                                                     
       
        self._executable  = executable
        self._arguments   = arguments
        self._environment = cfg["environment"]
        self._uses_mpi    = cfg["uses_mpi"]
        self._pre_exec    = cfg["pre_exec"]  

# ------------------------------------------------------------------------------
