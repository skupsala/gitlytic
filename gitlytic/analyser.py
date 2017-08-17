import os
import subprocess
from utils import cd
from project_utils import get_project_output_dir

GIT_LOG_TSV_FORMAT = '%h%x09%an%x09%ad%x09%s'

def find_git_repo_paths(project_path):
    # Now assumes that no nested git repos (all in same level)
    return [os.path.join(project_path, directory) for directory in os.listdir(project_path) if
            os.path.exists(os.path.join(project_path, directory, '.git'))]


def git_log_tsv(project_path):
    git_repo_paths = find_git_repo_paths(project_path)
    for git_repo_path in git_repo_paths:
        with cd(git_repo_path):
            git_repo_name = os.path.split(git_repo_path)[1]
            output_file = os.path.join(get_project_output_dir(project_path), 'git_log_{}.tsv'.format(git_repo_name))
            subprocess.check_call('git log --date=iso --pretty=format:"{}" > {}'.format(GIT_LOG_TSV_FORMAT, output_file),
                                  shell=True)


def analyse(project_path):
    git_log_tsv(project_path)
