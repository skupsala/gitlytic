import subprocess

from gitlytic.repo import get_repo_path
from gitlytic.utils import cd


def analyse_snapshots(project_path, snapshot_commits):
    repo_snapshot_commit_dict = {}
    for snapshot_commit in snapshot_commits:
        if snapshot_commit['repo_name'] not in repo_snapshot_commit_dict:
            repo_snapshot_commit_dict[snapshot_commit['repo_name']] = [snapshot_commit]
        else:
            repo_snapshot_commit_dict[snapshot_commit['repo_name']].append(snapshot_commit)

    for repo_name, repo_snapshot_commits in repo_snapshot_commit_dict.items():
        repo_path = get_repo_path(project_path, repo_name)
        with cd(repo_path):
            for snapshot_commit in repo_snapshot_commits:
                subprocess.check_call('git checkout {}'.format(snapshot_commit['commit_hash']), shell=True)
                snapshot()


def snapshot():
    raw_cloc_output = subprocess.check_output('cloc .', shell=True)
    # TODO parse cloc output