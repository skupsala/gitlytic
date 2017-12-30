import os
import subprocess
import git

from gitlytic import settings
from gitlytic.utils import cd, default_logger as logger
from gitlytic.project import get_project_output_dir, get_project_name, get_project_path
from gitlytic.repo import find_git_repo_paths, get_repo_name

GIT_LOG_FORMAT_OPTIONS = {
    'commit_hash': '%H',
    'author_name': '%an',
    'author_email': '%ae',
    'author_date': '%ad',
    'committer_name': '%cn',
    'committer_email': '%ce',
    'committer_date': '%cd',
    'subject': '%s',
    'body': '%b',
}

GIT_LOG_TSV_FIELDS = ['commit_hash',
                      'author_name',
                      'author_email',
                      'author_date',
                      'committer_name',
                      'committer_email',
                      'committer_date',
                      'subject']

GIT_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

GIT_LOG_TSV_HEADER = '{sep}'.join(GIT_LOG_TSV_FIELDS).format(sep=settings.FIELD_SEPARATOR)
GIT_LOG_TSV_FORMAT = '{sep}'.join([GIT_LOG_FORMAT_OPTIONS[field] for field in GIT_LOG_TSV_FIELDS]).format(
        sep=settings.FIELD_SEPARATOR)


def git_log_tsv(project_path):
    logger.info('Producing git_log.tsv files for project {}'.format(get_project_name(project_path)))
    git_repo_paths = find_git_repo_paths(project_path)
    for git_repo_path in git_repo_paths:
        with cd(git_repo_path):
            git_repo_name = get_repo_name(git_repo_path)
            logger.info('Producing git_log.tsv for {}'.format(git_repo_name))
            output_file_path = os.path.join(get_project_output_dir(project_path),
                                            'git_log_{}.tsv'.format(git_repo_name))
            with open(output_file_path, 'w') as output_file:
                output_file.write(GIT_LOG_TSV_HEADER + '\n')
            git_log_cmd = 'git log --date=format:"{}" --pretty=format:"{}" >> {}'.format(GIT_LOG_DATE_FORMAT,
                                                                                         GIT_LOG_TSV_FORMAT,
                                                                                         output_file_path)
            logger.debug(git_log_cmd)
            subprocess.check_call(git_log_cmd, shell=True)


def git_commit_analysis(project_path):
    logger.info('Analysing git commits for project {}'.format(get_project_name(project_path)))
    git_repo_paths = find_git_repo_paths(project_path)
    for git_repo_path in git_repo_paths:
        git_repo_name = get_repo_name(git_repo_path)
        logger.info('Analysing git commits for repo {}'.format(git_repo_name))
        repo = git.Repo(git_repo_path)
        for commit in repo.iter_commits('master', max_count=20):
            is_merge = False
            changed_files = 0
            insertions = 0
            deletions = 0
            if len(commit.parents) > 1:
                is_merge = True
            else:
                print('Commit {}'.format(commit.hexsha))
                changed_files = len(commit.stats.files)
                for changed_file, change in commit.stats.files.items():
                    insertions += change['insertions']
                    deletions += change['deletions']
                print('Changed files {}, insesrtions {}, deletions {}'.format(changed_files, insertions, deletions))
            yield (git_repo_name, commit.hexsha, is_merge, changed_files, insertions, deletions)


def analyse(project_path):
    git_log_tsv(project_path)
