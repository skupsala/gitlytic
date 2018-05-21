import subprocess
import json
import os
import csv

from datetime import datetime
from dateutil import tz

from gitlytic.project import get_project_output_dir
from gitlytic.repo import get_repo_path
from gitlytic.utils import cd
from gitlytic import settings


def analyse_snapshots(project_path, snapshot_commits):
    repo_snapshot_commit_dict = {}
    for snapshot_commit in snapshot_commits:
        if snapshot_commit['repo_name'] not in repo_snapshot_commit_dict:
            repo_snapshot_commit_dict[snapshot_commit['repo_name']] = [snapshot_commit]
        else:
            repo_snapshot_commit_dict[snapshot_commit['repo_name']].append(snapshot_commit)

    snapshots = {}
    for repo_name, repo_snapshot_commits in repo_snapshot_commit_dict.items():
        repo_path = get_repo_path(project_path, repo_name)
        repo_snapshots = {}
        with cd(repo_path):
            for snapshot_commit in repo_snapshot_commits:
                subprocess.check_call('git checkout {}'.format(snapshot_commit['commit_hash']), shell=True)
                snapshot = take_snapshot(snapshot_commit)
                repo_snapshots[snapshot_commit['commit_hash']] = snapshot

        snapshots[repo_name] = repo_snapshots

    save_snapshots(project_path, snapshots)


def take_snapshot(snapshot_commit):
    return {
        'cloc': cloc_snapshot(),
        'commit': snapshot_commit,
    }


def cloc_snapshot():
    raw_cloc_json_output = subprocess.check_output('cloc --json .', shell=True, universal_newlines=True)
    if raw_cloc_json_output.strip():
        return json.loads(raw_cloc_json_output.strip())
    else:
        return {}


def save_snapshots(project_path, snapshots):
    rows = []
    header_fields = {'repo_name', 'commit_hash'}
    for repo_name, repo_snapshots in snapshots.items():
        for commit_hash, snapshot in repo_snapshots.items():
            meta_fields = {
                'repo_name': repo_name,
                'commit_hash': commit_hash,
                'author_date': snapshot['commit']['author_date']
            }
            cloc_fields = {lang: (data['blank'] + data['comment'] + data['code'])
                           for lang, data in snapshot['cloc'].items() if lang != 'header'}
            row = {**meta_fields, **cloc_fields}
            header_fields = header_fields | set(row.keys())
            rows.append(row)

    base_output_dir = get_project_output_dir(project_path)
    cloc_snapshot_output_file = os.path.join(base_output_dir, 'snapshot_cloc.csv')
    with open(cloc_snapshot_output_file, 'w') as cloc_csv_file:
        cloc_csv_writer = csv.DictWriter(cloc_csv_file,
                                         fieldnames=header_fields,
                                         delimiter=settings.DELIMITER,
                                         quotechar=settings.QUOTECHAR,
                                         quoting=csv.QUOTE_NONNUMERIC)
        cloc_csv_writer.writeheader()
        for row in rows:
            # If we want to write 0 for missing fields we could use value below instead of row
            # {field: row[field] if field in row else 0 for field in header_fields}
            cloc_csv_writer.writerow(row)
