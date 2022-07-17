# Scripts

Miscellaneous scripts.

The majority of scripts are written in Python and the recommended usage of them is described below.
The python scripts are published on PyPI and can be used as utilities for scripts/apps.

Of course, it is possible to clone this repo and use the all scripts as wanted.

## Recommended usage

### Install with pipx

    pipx install git+https://github.com/bjuvensjo/scripts.git@master

With pipx 

* this package is installed in an isolated Python environment
* all scripts specified in pyproject.toml will be globally available on your path, e.g. vang-azdo-clone-repos

If you want shorter names, one option is aliases, e.g. 

    alias acr=vang-azdo-clone-repos

### Use help

All Python scripts has help, e.g.

    > vang-azdo-clone-repos -h
    usage: clone_repos.py [-h] [-au AZURE_DEVOPS_URL] [--verify_certificate | --no-verify_certificate] [-t TOKEN] (-o ORGANISATION | -p PROJECTS [PROJECTS ...] | -r REPOS [REPOS ...]) [-b BRANCH] [-d CLONE_DIR] [-f]
    
    Clone Azure DevOps repos
    
    options:
      -h, --help            show this help message and exit
      -au AZURE_DEVOPS_URL, --azure_devops_url AZURE_DEVOPS_URL
                            The Azure DevOps REST API base url
      --verify_certificate, --no-verify_certificate
                            If certificate of Azure should be verified (default: True)
      -t TOKEN, --token TOKEN
                            The Azure DevOps authorisation token
      -o ORGANISATION, --organisation ORGANISATION
                            Azure DevOps organisation, e.g organisation
      -p PROJECTS [PROJECTS ...], --projects PROJECTS [PROJECTS ...]
                            Azure DevOps projects, e.g organisation/project
      -r REPOS [REPOS ...], --repos REPOS [REPOS ...]
                            Repos, e.g. organisation/project/repo
      -b BRANCH, --branch BRANCH
                            The clone branch
      -d CLONE_DIR, --clone_dir CLONE_DIR
                            The directory to clone into
      -f, --flat            Clone to flat structure

For the use of non-python scripts, look at the documentation in the scripts
      
## Develop
### Using pyenv and virtualenv

    pyenv install 3.10.5
    pyenv global 3.10.5 # or pyenv local 3.10.5
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

### Using conda

    conda create -n scripts python=3.10 
    conda activate scripts
    pip install -r requirements.txt
