# Scripts

Miscellaneous scripts

## Suggested usage ##

1. Clone this repository
2. Add required environment variables, see artifactory_api.py and bb_api.py
2. Create a directory, e.g. ~/bin, and add it to your path
3. Create symbolic links (see example below). If on windows, create cmd-files that calls the scripts
4. All python scripts has help, e.g 

        ~/bin bb-clone-repos -h
        usage: bb-clone-repos [-h]
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

5. For the use of non-python scripts, look at the documentation in the script
      
## Symbolic links example ##

    ~/bin
    lrwxr-xr-x    artifactory-delete -> /Users/bjuvensjo/git/scripts/py/artifactory_delete.py
    lrwxr-xr-x    artifactory-publish -> /Users/bjuvensjo/git/scripts/py/artifactory_publish.py
    lrwxr-xr-x    basic -> /Users/bjuvensjo/git/scripts/py/basic.py
    lrwxr-xr-x    bb-api -> /Users/bjuvensjo/git/scripts/py/bb_api.py
    lrwxr-xr-x    bb-clone-repos -> /Users/bjuvensjo/git/scripts/py/bb_clone_repos.py
    lrwxr-xr-x    bb-create-repo -> /Users/bjuvensjo/git/scripts/py/bb_create_repo.py
    lrwxr-xr-x    bb-delete-repos -> /Users/bjuvensjo/git/scripts/py/bb_delete_repos.py
    lrwxr-xr-x    bb-enable-webhooks -> /Users/bjuvensjo/git/scripts/py/bb_enable_webhooks.py
    lrwxr-xr-x    bb-fork-repos -> /Users/bjuvensjo/git/scripts/py/bb_fork_repos.py
    lrwxr-xr-x    bb-get-branches -> /Users/bjuvensjo/git/scripts/py/bb_get_branches.py
    lrwxr-xr-x    bb-get-clone-urls -> /Users/bjuvensjo/git/scripts/py/bb_get_clone_urls.py
    lrwxr-xr-x    bb-get-clone-urls-grep -> /Users/bjuvensjo/git/scripts/py/bb_get_clone_urls_grep.py
    lrwxr-xr-x    bb-get-default-branches -> /Users/bjuvensjo/git/scripts/py/bb_get_default_branches.py
    lrwxr-xr-x    bb-get-projects -> /Users/bjuvensjo/git/scripts/py/bb_get_projects.py
    lrwxr-xr-x    bb-get-repos -> /Users/bjuvensjo/git/scripts/py/bb_get_repos.py
    lrwxr-xr-x    bb-get-tags -> /Users/bjuvensjo/git/scripts/py/bb_get_tags.py
    lrwxr-xr-x    bb-has-branch -> /Users/bjuvensjo/git/scripts/py/bb_has_branch.py
    lrwxr-xr-x    bb-has-tag -> /Users/bjuvensjo/git/scripts/py/bb_has_tag.py
    lrwxr-xr-x    bb-open-remote -> /Users/bjuvensjo/git/scripts/py/bb_open_remote.py
    lrwxr-xr-x    bb-set-default-branches -> /Users/bjuvensjo/git/scripts/py/bb_set_default_branches.py
    lrwxr-xr-x    bb-utils -> /Users/bjuvensjo/git/scripts/py/bb_utils.py
    lrwxr-xr-x    command-all -> /Users/bjuvensjo/git/scripts/py/command_all.py
    lrwxr-xr-x    git-open-remote -> /Users/bjuvensjo/git/scripts/sh/git-open-remote.sh
    lrwxr-xr-x    maven-reactor-summary -> /Users/bjuvensjo/git/scripts/py/maven_reactor_summary.py
    lrwxr-xr-x    maven-switch-settings -> /Users/bjuvensjo/git/scripts/py/maven_switch_settings.py
    lrwxr-xr-x    mmp -> /Users/bjuvensjo/git/scripts/py/maven_multi_module_project.py
    lrwxr-xr-x    mp -> /Users/bjuvensjo/git/scripts/py/maven_project.py
    lrwxr-xr-x    rsr -> /Users/bjuvensjo/git/scripts/py/rsr.py
    lrwxr-xr-x    s -> /Users/bjuvensjo/git/scripts/py/s.py
    lrwxr-xr-x    toHtmlAndPdf -> /Users/bjuvensjo/git/scripts/sh/toHtmlAndPdf.sh


