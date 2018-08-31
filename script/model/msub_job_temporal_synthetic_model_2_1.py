
#!/usr/bin/env python
'''
Job submission for quest
'''
#This import is necessary so that we can modify the permissions on the
#submission script
import os
import numpy as np
import subprocess
from itertools import product
# Current path
current_path = os.path.abspath(os.path.join(''))


# Path to save bash file
bash_path = os.path.abspath(os.path.join( 'bash_save'))
if not os.path.exists(bash_path ):
    os.makedirs( bash_path)

# Path to save output  file for bash job
o_path = os.path.abspath(os.path.join( os.pardir,os.pardir,'result', 'contagion', 'temporal', 'synthetic', 'model_2_1', 'out'))
if not os.path.exists(o_path ):
    os.makedirs( o_path)


# Path to save output and error file for bash job
e_path = os.path.abspath(os.path.join( os.pardir, os.pardir, 'result', 'contagion', 'temporal', 'synthetic', 'model_2_1', 'error'))
if not os.path.exists(e_path ):
    os.makedirs( e_path)

# Path to data  file 
d_path = os.path.abspath(os.path.join( os.pardir,os.pardir,'data', 'synthetic', 'model_2_1'))
if not os.path.exists(o_path ):
    raise ValueError

# Path to save output  file for result
r_path = os.path.abspath(os.path.join( '/projects/b1022/Projects/junelee/', 'movie', 'contagion','temporal', 'synthetic', 'model_2_1'))

if not os.path.exists(r_path ):
    os.makedirs(r_path)


programname = 'temporal_contagion_synthetic_2.py'
belief_type = 'empirical'
pdtn = [[0.1, 0.3, 0.5, 0.7, 0.9], [1.0], [1.0], list(range(20))]
pdtn_list  = list(product(*pdtn))

for p, d, t, n in pdtn_list:
    date = subprocess.Popen('date', stdout=subprocess.PIPE, shell=True)
    (datetime, err) = date.communicate()
    print ('Time process ran', datetime)
    print ('\t Parameter p is equal to {:.2f}'.format(p))
    print ('\t Parameter d is equal to {:.2f}'.format(d))
    print ('\t Parameter t is equal to {:.2f}'.format(t))   
    with open(bash_path + "/job_script_synthetic_2_1_p{}d{}t{}n{}.sh".format(int(100*p), int(100*d), int(100*t), int(n)), 'w') as queue_out:
            queue_out.write(
"""
#!/bin/bash
#MSUB -N contagion_jobscript_synthetic_2_1
#MSUB -A b1022

# ressource list                                                
#MSUB -l nodes=1:ppn=1
#MSUB -l walltime=168:00:00
#MSUB -q buyin


# ressource list    
#MSUB -o {}
#MSUB -e {}

pwd
module load python/anaconda3
source activate movie-network
cd
cd {}
python {} {} {} --belief_type {} -p {} -d {} -t {} -n {}
""".format(o_path, e_path, current_path, programname, d_path, r_path, belief_type, p, d, t, n))



    queue_out.close()
    os.system("msub {}/job_script_synthetic_2_1_p{}d{}t{}n{}.sh".format(bash_path, int(100*p), int(100*d), int(100*t), int(n)))
