import os
import git
import csv
import json
from datetime import datetime, timedelta
from dateutil import tz
from gitlytic import settings, snapshot_analysis

from gitlytic.utils import logger
from gitlytic.project import get_project_output_dir, get_project_name, get_project_settings
from gitlytic.repo import find_git_repo_paths, get_repo_name

GIT_LOG_TSV_FIELDS = [
    'repo_name',
    'commit_hash',
    'author_name',
    'author_email',
    'author_date',
    'committer_name',
    'committer_email',
    'committer_date',
    'subject',
    'body',
    'changed_file_count',
    'insertions',
    'deletions',
    'is_merge',
    'cumulative_loc',
    'cumulative_author_count',
    # Repo branch count tells branch count "existing" alongside master
    'repo_branch_count',
]


def parse_merge_commit_resolution_changes(repo, merge_commit):
    raw_merge_show_output = repo.git.show(merge_commit.hexsha, '-C', '--oneline')
    first_file_occurred = False
    insertions = 0
    deletions = 0
    for line in raw_merge_show_output.split('\n'):
        if line.startswith('@@@'):
            first_file_occurred = True
            continue
        if first_file_occurred:
            if line.startswith('++'):
                insertions += 1
            elif line.startswith('--'):
                deletions += 1
    return {
        'insertions': insertions,
        'deletions': deletions,
    }


def git_commit_analysis(project_path, specific_repositories=None):
    logger.info('Analysing git commits for project {}'.format(get_project_name(project_path)))
    project_settings = get_project_settings(project_path)
    snapshot_timedelta = timedelta(**project_settings['snapshot_timedelta'])
    previous_versions = load_previous_analysis_version(project_path)
    git_repo_paths = find_git_repo_paths(project_path)

    analysis_head_commits = []
    for git_repo_path in git_repo_paths:
        git_repo_name = get_repo_name(git_repo_path)
        if specific_repositories and git_repo_name not in specific_repositories:
            logger.info('Skipping git commit analysis for repo {}'.format(git_repo_name))
            continue
        logger.info('Analysing git commits for repo {}'.format(git_repo_name))
        repo = git.Repo(git_repo_path)
        # FIXME Cumulative loc and author_count does not yet work as exceptected for non-linear history
        if git_repo_name in previous_versions:
            commit_range = '{from_commit}..{to_commit}'.format(
                    from_commit=previous_versions[git_repo_name]['commit_hash'],
                    to_commit=project_settings['analysis_branch'])
            cumulative_loc = previous_versions[git_repo_name]['cumulative_loc']
            cumulative_authors = set(previous_versions[git_repo_name]['cumulative_authors'])
            repo_active_heads = set(previous_versions[git_repo_name]['repo_active_heads'])
        else:
            commit_range = project_settings['analysis_branch']
            cumulative_loc = 0
            cumulative_authors = set()
            repo_active_heads = set()

        # TODO use better way to iterate in reverse order - now all commits are in memory due to reversed(list(...)) call
        commits = list(reversed(list(repo.iter_commits(commit_range, topo_order=True))))
        analysed_commit = None
        previous_snapshot_commit = None
        for idx, commit in enumerate(commits):
            print('\rAnalysing {percentage}% ( {current} / {total} ) commits'.format(
                    percentage=int((idx / len(commits)) * 100.0),
                    current=idx,
                    total=len(commits)
            ), end='\r')
            insertions = 0
            deletions = 0
            changed_file_count = 0
            if len(commit.parents) > 1:
                is_merge = True
                merge_resolution = parse_merge_commit_resolution_changes(repo, commit)
                insertions = merge_resolution['insertions']
                deletions = merge_resolution['deletions']
            else:
                is_merge = False
                changed_file_count = len(commit.stats.files)
                for changed_file, change in commit.stats.files.items():
                    insertions += change['insertions']
                    deletions += change['deletions']

            repo_active_heads.add(commit.hexsha)
            if commit.parents:
                for parent in commit.parents:
                    if parent.hexsha in repo_active_heads:
                        repo_active_heads.remove(parent.hexsha)

            cumulative_loc = cumulative_loc + insertions - deletions
            cumulative_authors.add(commit.author.email)

            author_date = datetime.fromtimestamp(commit.authored_date,
                                                 tz.tzoffset(None, -commit.author_tz_offset))
            committer_date = datetime.fromtimestamp(commit.committed_date,
                                                    tz.tzoffset(None, -commit.committer_tz_offset))

            analysed_commit = {
                'repo_name': git_repo_name,
                'commit_hash': commit.hexsha,
                'author_name': commit.author.name,
                'author_email': commit.author.email,
                'author_date': author_date,
                'committer_name': commit.committer.name,
                'committer_email': commit.committer.email,
                'committer_date': committer_date,
                'subject': commit.summary,
                'body': commit.message,
                'changed_file_count': changed_file_count,
                'insertions': insertions,
                'deletions': deletions,
                'is_merge': is_merge,
                'cumulative_loc': cumulative_loc,
                'cumulative_author_count': len(cumulative_authors),
                'repo_branch_count': len(repo_active_heads)
            }

            if previous_snapshot_commit is None \
                    or previous_snapshot_commit['author_date'] + snapshot_timedelta <= committer_date:
                previous_snapshot_commit = analysed_commit
                analysed_commit['_should_snapshot'] = True
            else:
                analysed_commit['_should_snapshot'] = False

            yield analysed_commit
        else:
            if analysed_commit:
                analysis_head_commits.append(analysed_commit)
    else:
        # In the end we modify our previous versions and update versions file
        for analysis_head_commit in analysis_head_commits:
            previous_versions[analysis_head_commit['repo_name']] = {
                'commit_hash': analysis_head_commit['commit_hash'],
                'cumulative_loc': cumulative_loc,
                'cumulative_authors': list(cumulative_authors),
                'repo_active_heads': list(repo_active_heads)
            }

        output_version_file_path = os.path.join(get_project_output_dir(project_path),
                                                'git_commits_version_{}.json'.format(get_project_name(project_path)))
        with open(output_version_file_path, 'w') as version_file:
            json.dump(previous_versions, version_file)


def load_previous_analysis_version(project_path):
    project_name = get_project_name(project_path)
    version_file_path = os.path.join(get_project_output_dir(project_path),
                                     'git_commits_version_{}.json'.format(project_name))
    if os.path.exists(version_file_path):
        with open(version_file_path, 'r', newline='') as versions_file:
            return json.load(versions_file)
    return {}


def run_and_save_git_commit_analysis(project_path, specific_repositories=None):
    project_name = get_project_name(project_path)

    output_file_path = os.path.join(get_project_output_dir(project_path),
                                    'git_commits_{}.csv'.format(project_name))
    should_write_header_row = True
    if os.path.exists(output_file_path):
        should_write_header_row = False

    snapshot_commits = []
    with open(output_file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=GIT_LOG_TSV_FIELDS, delimiter=settings.DELIMITER,
                                quotechar=settings.QUOTECHAR,
                                quoting=csv.QUOTE_NONNUMERIC)
        if should_write_header_row:
            writer.writeheader()
        for analysed_commit in git_commit_analysis(project_path, specific_repositories=specific_repositories):
            logger.debug('Analysed commit {}'.format(analysed_commit))
            if analysed_commit['_should_snapshot']:
                snapshot_commits.append(analysed_commit)
            # Filter out private / temporary keys like _should_snapshot
            commit_row = {key: value for key, value in analysed_commit.items() if not key.startswith('_')}
            writer.writerow(commit_row)

    return snapshot_commits


def analyse(project_path, specific_repositories=None):
    project_name = get_project_name(project_path)
    if specific_repositories:
        logger.info('Starting analysis for project {project} - only for repositories {repositories}'.format(
                project=project_name,
                repositories=', '.join(specific_repositories)
        ))
    else:
        logger.info('Starting analysis for project {project} - all repositories'.format(
                project=project_name
        ))
    snapshot_commits = run_and_save_git_commit_analysis(project_path, specific_repositories=specific_repositories)
    snapshot_analysis.analyse_snapshots(snapshot_commits)
