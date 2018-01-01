import os
import git
import csv
from datetime import datetime
from dateutil import tz

from gitlytic.utils import default_logger as logger
from gitlytic.project import get_project_output_dir, get_project_name, get_project_path
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
]


def git_commit_analysis(project_path):
    logger.info('Analysing git commits for project {}'.format(get_project_name(project_path)))
    git_repo_paths = find_git_repo_paths(project_path)
    for git_repo_path in git_repo_paths:
        git_repo_name = get_repo_name(git_repo_path)
        logger.info('Analysing git commits for repo {}'.format(git_repo_name))
        repo = git.Repo(git_repo_path)
        for commit in repo.iter_commits('master'):
            is_merge = False
            changed_file_count = 0
            insertions = 0
            deletions = 0
            if len(commit.parents) > 1:
                is_merge = True
            else:
                changed_file_count = len(commit.stats.files)
                for changed_file, change in commit.stats.files.items():
                    insertions += change['insertions']
                    deletions += change['deletions']
            yield {
                'repo_name': git_repo_name,
                'commit_hash': commit.hexsha,
                'author_name': commit.author.name,
                'author_email': commit.author.email,
                'author_date': datetime.fromtimestamp(commit.authored_date,
                                                      tz.tzoffset(None, -commit.author_tz_offset)),
                'committer_name': commit.committer.name,
                'committer_email': commit.committer.email,
                'committer_date': datetime.fromtimestamp(commit.committed_date,
                                                         tz.tzoffset(None, -commit.committer_tz_offset)),
                'subject': commit.summary,
                'body': commit.message,
                'changed_file_count': changed_file_count,
                'insertions': insertions,
                'deletions': deletions,
                'is_merge': is_merge,
            }


def write_git_commit_csv(project_path):
    project_name = get_project_name(project_path)
    output_file_path = os.path.join(get_project_output_dir(project_path),
                                    'git_commits_{}.csv'.format(project_name))
    with open(output_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=GIT_LOG_TSV_FIELDS, delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for commit_row in git_commit_analysis(project_path):
            writer.writerow(commit_row)


def analyse(project_path):
    write_git_commit_csv(project_path)
