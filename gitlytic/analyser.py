import os
import subprocess
import settings
from utils import cd, default_logger as logger
from project import get_project_output_dir, get_project_name
from repo import find_git_repo_paths, get_repo_name


GIT_LOG_FORMAT_OPTIONS = {
    'commit_hash': '%H',
    'author_name': '%an',
    'author_email': '%ae',
    'author_date': '%aI',
    'committer_name': '%cn',
    'committer_email': '%ce',
    'committer_date': '%cI',
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
            subprocess.check_call(
                    'git log --date=iso --pretty=format:"{}" >> {}'.format(GIT_LOG_TSV_FORMAT, output_file_path),
                    shell=True)


def analyse(project_path):
    git_log_tsv(project_path)
