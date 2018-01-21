import json
import os

from gitlytic import settings
from gitlytic.utils import default_logger as logger, cd
import subprocess


def get_project_path(project_name):
    return os.path.join(settings.DATA_DIR, project_name)


def get_project_name(project_path):
    return os.path.split(project_path)[1]


def get_project_output_dir(project_path):
    return os.path.join(project_path, '.gitlytic')


def get_project_output_dir_by_name(project_name):
    return os.path.join(get_project_path(project_name), '.gitlytic')


def update_project(project_path):
    for dirname in os.listdir(project_path):
        repo_path = os.path.join(project_path, dirname)
        if dirname == '.gitlytic':
            continue
        if not os.path.exists(os.path.join(repo_path, '.git')):
            logger.info('{} is not a git repo - skipping update'.format(dirname))
            continue
        with cd(repo_path):
            logger.info('Updating repo {}'.format(dirname))
            try:
                subprocess.check_call('git fetch', shell=True)
            except subprocess.CalledProcessError:
                logger.warn('Failed to update repo {}'.format(dirname))


def get_project_settings(project_path):
    project_settings_path = os.path.join(project_path, '.gitlyticrc')
    if os.path.exists(project_settings_path):
        logger.info('Found .gitlyticrc -  extracting settings')
        with open(project_settings_path, 'r') as project_settings_file:
            try:
                project_settings = json.load(project_settings_file)
                return {**settings.PROJECT_DEFAULT_SETTINGS, **project_settings}
            except:
                logger.error('Error on reading .gitlyticrc - json file reqiored')
                return settings.PROJECT_DEFAULT_SETTINGS
    else:
        return settings.PROJECT_DEFAULT_SETTINGS
