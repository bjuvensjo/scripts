# Scripts

Miscellaneous scripts

## Suggested usage ##

1. Clone this repository
2. Install with pip3 install -e .
3. Add required environment variables, see e.g. vang/artifactory/api.py and vang/bitbucket/api.py
4. Create a directory, e.g. ~/bin, and add it to your path
5. Create symbolic links (see example below). If on windows, create cmd-files that calls the scripts
6. All python scripts has help, e.g 

        ~/bin clone-repos -h
        usage: clone-repos [-h]
                           (-p PROJECTS [PROJECTS ...] | -r REPOS [REPOS ...] | -c CONFIG)
                           [-b BRANCH] [-d DIR]
        
        Clone Bitbucket repos
        
        optional arguments:
          -h, --help            show this help message and exit
          -p PROJECTS [PROJECTS ...], --projects PROJECTS [PROJECTS ...]
                                Bitbucket projects, e.g key1 key2
          -r REPOS [REPOS ...], --repos REPOS [REPOS ...]
                                Repos, e.g. key1/repo1 key2/repo2
          -c CONFIG, --config CONFIG
                                Configuration file, see bb_clone_repos.json
          -b BRANCH, --branch BRANCH
                                The clone branch. Overrides branch in configuration
                                file (-c)
          -d DIR, --dir DIR     The directory to clone into

7. For the use of non-python scripts, look at the documentation in the scripts
      
## Symbolic links example ##

    ln -s ~/git/scripts/vang/artifactory/delete.py ~/bin/artifactory-delete
    ln -s ~/git/scripts/vang/artifactory/publish.py ~/bin/artifactory-publish
    ln -s ~/git/scripts/vang/bitbucket/clone_repos.py ~/bin/clone-repos
    ln -s ~/git/scripts/vang/bitbucket/clone_repos_with_commits_since.py ~/bin/clone-repos-with-commits-since
    ln -s ~/git/scripts/vang/bitbucket/create_from_template.py ~/bin/create-from-template
    ln -s ~/git/scripts/vang/bitbucket/create_repo.py ~/bin/create-repo
    ln -s ~/git/scripts/vang/bitbucket/delete_repos.py ~/bin/delete-repos
    ln -s ~/git/scripts/vang/bitbucket/enable_webhooks.py ~/bin/enable-webhooks
    ln -s ~/git/scripts/vang/bitbucket/fork_repos.py ~/bin/fork-repos
    ln -s ~/git/scripts/vang/bitbucket/fork_repos_git.py ~/bin/fork-repos-git
    ln -s ~/git/scripts/vang/bitbucket/get_branches.py ~/bin/get-branches
    ln -s ~/git/scripts/vang/bitbucket/get_clone_urls.py ~/bin/get-clone-urls
    ln -s ~/git/scripts/vang/bitbucket/get_clone_urls_grep.py ~/bin/get-clone-urls-grep
    ln -s ~/git/scripts/vang/bitbucket/get_default_branches.py ~/bin/get-default-branches
    ln -s ~/git/scripts/vang/bitbucket/get_projects.py ~/bin/get-projects
    ln -s ~/git/scripts/vang/bitbucket/get_repos.py ~/bin/get-repos
    ln -s ~/git/scripts/vang/bitbucket/get_tags.py ~/bin/get-tags
    ln -s ~/git/scripts/vang/bitbucket/has_branch.py ~/bin/has-branch
    ln -s ~/git/scripts/vang/bitbucket/has_tag.py ~/bin/has-tag
    ln -s ~/git/scripts/vang/bitbucket/open_remote.py ~/bin/open-remote
    ln -s ~/git/scripts/vang/bitbucket/set_default_branches.py ~/bin/set-default-branches
    ln -s ~/git/scripts/vang/jenkins/delete_jobs.py ~/bin/delete-jobs
    ln -s ~/git/scripts/vang/jenkins/get_jobs.py ~/bin/get-jobs
    ln -s ~/git/scripts/vang/jenkins/trigger_builds.py ~/bin/trigger-builds
    ln -s ~/git/scripts/vang/maven/get_artifact_id.py ~/bin/get-artifact-id
    ln -s ~/git/scripts/vang/maven/multi_module_project.py ~/bin/mmp
    ln -s ~/git/scripts/vang/maven/project.py ~/bin/mp
    ln -s ~/git/scripts/vang/maven/switch_settings.py ~/bin/switch-settings
    ln -s ~/git/scripts/vang/misc/basic.py ~/bin/basic
    ln -s ~/git/scripts/vang/misc/ext_local.py ~/bin/ext-local
    ln -s ~/git/scripts/vang/misc/mac_ip.py ~/bin/ip
    ln -s ~/git/scripts/vang/misc/s.py ~/bin/s
    ln -s ~/git/scripts/vang/pio/command_all.py ~/bin/command-all
    ln -s ~/git/scripts/vang/pio/rsr.py ~/bin/rsr
    ln -s ~/git/scripts/vang/tfs/clone_repos.py ~/bin/tfs-clone-repos
    ln -s ~/git/scripts/vang/tfs/create_repo.py ~/bin/tfs-create-repo
    ln -s ~/git/scripts/vang/tfs/create_from_template.py ~/bin/tfs-create-from-template
    ln -s ~/git/scripts/vang/tfs/delete_repo.py ~/bin/tfs-delete-repo
    ln -s ~/git/scripts/vang/tfs/get_branches.py ~/bin/tfs-get-branches
    ln -s ~/git/scripts/vang/tfs/get_projects.py ~/bin/tfs-get-projects
    ln -s ~/git/scripts/vang/tfs/get_repos.py ~/bin/tfs-get-repos


## Work on it

1. Create a virtual environment

    conda create -n scripts python=3.7 autopep8 flake8 jedi more-itertools pytest pytest-cov requests twine wheel yapf
