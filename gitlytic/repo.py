import os


def find_git_repo_paths(project_path):
    # Now assumes that no nested git repos (all in same level)
    return [os.path.join(project_path, directory) for directory in os.listdir(project_path) if
            os.path.exists(os.path.join(project_path, directory, '.git'))]


def get_repo_name(repo_path):
    return os.path.split(repo_path)[1]


def get_repo_path(project_path, repo_name):
    return os.path.join(project_path, repo_name)
