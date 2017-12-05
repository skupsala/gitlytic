import os

from gitlytic import settings


def get_project_path(project_name):
    return os.path.join(settings.DATA_DIR, project_name)


def get_project_name(project_path):
    return os.path.split(project_path)[1]


def get_project_output_dir(project_path):
    return os.path.join(project_path, '.gitlytic')


def get_project_output_dir_by_name(project_name):
    return os.path.join(get_project_path(project_name), '.gitlytic')
