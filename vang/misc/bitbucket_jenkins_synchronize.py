#!/usr/bin/env python3
import logging
from datetime import datetime
from re import fullmatch

from vang.bitbucket.api import get_all
from vang.bitbucket.get_projects import get_projects
from vang.bitbucket.get_repos import get_repos
from vang.core.core import pmap_unordered, get_in
from vang.jenkins.get_jobs import get_jobs

logging.basicConfig(level=logging.INFO)


def matches(v, pattern):
    return fullmatch(pattern, v)


def young_enough(commit_datetime, max_head_commit_age):
    return (datetime.now() - commit_datetime).days < max_head_commit_age


def complement_and_filter_repos(repos, branch_pattern, max_head_commit_age):
    def inner(r):
        branches = {}
        for b in get_all(f'/rest/api/1.0/projects/{r["key"]}/repos/{r["name"]}/branches'):
            branch_name = b['displayId']
            if matches(branch_name, branch_pattern):
                commits = get_all(f'/rest/api/1.0/projects/{r["key"]}/repos/{r["name"]}/commits',
                                  {'until': branch_name}, 1)
                if commits:
                    commit_datetime = datetime.fromtimestamp(commits[0]['authorTimestamp'] / 1000)
                    if young_enough(commit_datetime, max_head_commit_age):
                        branches[branch_name] = commit_datetime

        if branches:
            r = dict(r, branches=branches)
            logging.debug('Including repo: %s', r)
            return r

        logging.debug('Excluding repo: %s', r)
        return None

    for repo in pmap_unordered(
            inner,
            repos,
            processes=30):
        if repo:
            yield repo


def find_repos(project_pattern, repo_pattern):
    for p in get_projects():
        key = p['key']
        if matches(key, project_pattern):
            for r in get_repos(p['key']):
                if matches(r['name'], repo_pattern):
                    repo = {
                        'key': key,
                        'name': r['name'],
                        'cloneUrl': get_in(r, ['links', 'clone', 0, 'href'])
                        # 'cloneUrl': r['links']['clone'][0]['href'],
                    }
                    logging.debug('Found repo: %s', repo)
                    yield repo


def get_repo_info(project_pattern, repo_pattern, branch_pattern, tag_pattern, max_head_commit_age, **kwargs):
    # TODO: Add tag info
    repos = find_repos(project_pattern, repo_pattern)

    updated_repos = {}
    for repo in complement_and_filter_repos(repos, branch_pattern, max_head_commit_age):
        for branch in repo['branches'].keys():
            updated_repos[(repo['key'], repo['name'], branch)] = repo
    return updated_repos


def get_job_info(project_pattern, repo_pattern, branch_pattern, tag_pattern, **kwargs):
    # TODO: Add tag info
    jobs = {}
    for job in get_jobs():
        job_name = job['name']
        try:
            key, name, branch = job_name.split('_')  # Is branch sometimes also tag?
            if matches(key, project_pattern) and matches(name, repo_pattern) and matches(branch, branch_pattern):
                job = {
                    'name': job_name,
                    'url': job['url'],
                    'repo': (key, name, branch)
                }
                jobs[(key, name, branch)] = job
                logging.debug('Including job: %s', job)
            else:
                logging.debug('Excluding job: %s', job_name)
        except ValueError:
            logging.debug('Excluding job: %s', job_name)
    return jobs


def synchronize(cfg):
    repos = get_repo_info(**cfg)
    jobs = get_job_info(**cfg)
    for job in jobs.values():
        if job['repo'] in repos:
            logging.info('Updating job: %s', job)
        else:
            logging.info('Deleting job: %s', job)

    for k, repo in repos.items():
        if k not in jobs:
            logging.info('Creating job: %s', repo)


if __name__ == '__main__':
    from timeit import default_timer as timer

    start = timer()

    cfg = {
        'project_pattern': 'ESAUTO',
        'repo_pattern': '.*',
        'branch_pattern': 'develop|release.*',
        'tag_pattern': [],
        'max_head_commit_age': 30
    }

    synchronize(cfg)

    from timeit import default_timer as timer

    end = timer()
    print(end - start)
