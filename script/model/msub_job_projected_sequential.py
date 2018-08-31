
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
o_path = os.path.abspath(os.path.join( os.pardir,os.pardir,'result', 'contagion', 'projection', 'seq', 'out'))
if not os.path.exists(o_path ):
    os.makedirs( o_path)


# Path to save output and error file for bash job
e_path = os.path.abspath(os.path.join( os.pardir, os.pardir, 'result', 'contagion', 'projection', 'seq', 'error'))
if not os.path.exists(e_path ):
    os.makedirs( e_path)

# Path to data  file 
d_path = os.path.abspath(os.path.join( os.pardir,os.pardir,'data', 'raw_data'))
d_path = os.path.join(d_path, 'movies.json')
if not os.path.exists(o_path ):
    raise ValueError

# Path to save output  file for result
r_path = os.path.abspath(os.path.join( '/projects/b1022/Projects/junelee/', 'movie', 'contagion','projection', 'seq'))

if not os.path.exists(r_path ):
    os.makedirs(r_path)


programname = 'sequential_contagion.py'
belief_type = 'empirical'
pdtna = [np.arange(0.0,1.1,0.1), [1.0], [1.0], list(range(20)), [1,2]]
pdtna_list  = list(product(*pdtna))

for p, d, t, n, a in pdtna_list:
    date = subprocess.Popen('date', stdout=subprocess.PIPE, shell=True)
    (datetime, err) = date.communicate()
    print ('Time process ran', datetime)
    print ('\t Parameter p is equal to {:.2f}'.format(p))
    print ('\t Parameter d is equal to {:.2f}'.format(d))
    print ('\t Parameter t is equal to {:.2f}'.format(t))
    print ('\t Parameter n is equal to {}'.format(n))
    print ('\t Parameter a is equal to {}',firnat(a))
    with open(bash_path + "/job_script_proj_p{}d{}t{}n{}a{}.sh".format(int(100*p), int(100*d), int(100*t), int(n), int(a)), 'w') as queue_out:
            queue_out.write(
"""
#!/bin/bash
#MSUB -N contagion_jobscript_projection
#MSUB -A b1022

# ressource list                                                
#MSUB -l nodes=1:ppn=1
#MSUB -l walltime=32:00:00
#MSUB -q buyin


# ressource list    
#MSUB -o {}
#MSUB -e {}

pwd
module load python/anaconda3
source activate movie-network
cd
cd {}
python {} {} {} --belief_type {} -p {} -d {} -t {} -n {} -a {}
""".format(o_path, e_path, current_path, programname, d_path, r_path, belief_type, p, d, t, n, a))



    queue_out.close()
    os.system("msub {}/job_script_proj_p{}d{}t{}n{}a{}.sh".format(bash_path, int(100*p), int(100*d), int(100*t), int(n), int(a)))
