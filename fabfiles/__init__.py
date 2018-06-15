from fabric.api import cd, env, task, local, run, settings, sudo, prefix, put, lcd, get
from fabric.contrib.project import rsync_project
from functools import wraps
import json
import requests
import datetime
import os

@task
def istanbul():
    env.hosts = ["istanbul.chem-eng.northwestern.edu"]
    env.environment = "istanbul"
    env.project_dir = "~/projects/movie_propagation"

def istanbul_env(f):
    @wraps(f)
    def wrapper():
        if "environment" not in env:
            print("E: Should activate some environment first")
            return
        if env.environment != "istanbul":
            print("E: Only works on istanbul environment")
            return
        cwd = os.getcwd()
        if not cwd.endswith("/movie_propagation"):
            print(f"E: Shoud run from the root folder ({cwd})")
            return
        f()

    return wrapper

@task
@istanbul_env
def run_nb():
    print("Boom!")

# FOR JUNE:
@task
@istanbul_env
def rsync_code_dont_run_it():
    run(f"mkdir -p \"{env.project_dir}\"")
    for folder in ["src", "script"]:
        rsync_project(
            env.project_dir,
            local_dir=os.getcwd() + f"/{folder}",
            delete=True,
            exclude=["*.pyc", "__pycache__", ".DS_Store", ".git", ".gitignore", ".vscode", "output", "videos", ".ipynb_checkpoints"])

@task
@istanbul_env
def push_nb():
    #push working copies of notebook to istanbul
    with cd(env.project_dir):
        run(f"mkdir -p ./notebooks_workingcopy/")
        with cd("notebooks_workingcopy/"):
            run(f"ln -sfn ../src src")
        run(f"rsync -u ./notebooks/*.ipynb ./notebooks_workingcopy/")
        run(f"ln -sfn /home/projects/movie-network ./notebooks_workingcopy/movie-network")

@task
@istanbul_env
def pull_nb():
    #pull cleaned notebook from istanbul
    with cd(f"{env.project_dir}/notebooks"):
        run("source ~/miniconda3/bin/activate movie_network ; for notebook in *.ipynb ; do jupyter nbconvert \"$notebook\" --to notebook --ClearOutputPreprocessor.enabled=True --stdout >\"../notebooks/$notebook\" ; done")
    get(f"{env.project_dir}/notebooks/*", "notebooks/")

@task
@istanbul_env
def copy_file(filename):
    cwd = os.getcwd()
    
    if not filename.startswith(cwd):
        print(f"E: file {filename} is not in the working dir: {cwd}")
        return
    
    if not filename.startswith(f"{cwd}/code"):
        print(f"I: file {filename} is not rsyncing to the server")
        return
        
    base = filename[0:len(cwd)]
    relfilename = filename[len(cwd)+1:]
    put(filename, f"{env.project_dir}/{relfilename}")
        

