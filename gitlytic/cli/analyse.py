import os
import sys
import argparse
import shutil
import logging

from gitlytic.utils import logger
from gitlytic.project import get_project_output_dir, get_project_path, update_project
from gitlytic.analyser import analyse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', help='Project name to be analysed inside data/ dir')
    parser.add_argument('--repositories',
                        help='By default analyses all repositories. Give comma separated list of repositories " \
                        "to analyse only specific repositories. Eg. repo1,repo2,repo3')
    parser.add_argument('--clean', action='store_true',
                        help='Forces clean analysis by removing cached analysis')
    parser.add_argument('--update', action='store_true', help='Pulls latest changes for all repositories')
    parser.add_argument('--verbose', action='store_true', help='Use verbose output. Useful for inspection / debugging')
    args = parser.parse_args()

    project_path = get_project_path(args.project)
    if not os.path.exists(project_path):
        print('No such project: {}'.format(args.project), file=sys.stderr)
        sys.exit(os.EX_DATAERR)

    if args.update:
        print('Updating project {}'.format(args.project))
        update_project(project_path)

    if args.repositories:
        specific_repositories = args.repositories.split(',')
    else:
        specific_repositories = None

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    output_dir = get_project_output_dir(project_path)
    if args.clean and os.path.exists(output_dir):
        print('Removing cached analysis')
        shutil.rmtree(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    analyse(project_path, specific_repositories=specific_repositories)
