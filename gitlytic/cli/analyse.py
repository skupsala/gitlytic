import os
import sys
import argparse
import shutil

from gitlytic.project import get_project_output_dir, get_project_path, update_project
from gitlytic.analyser import analyse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', help='Project name to be analysed inside data/ dir')
    parser.add_argument('--clean', action='store_true',
                        help='Forces clean analysis by removing cached analysis')
    parser.add_argument('--update', action='store_true', help='Fetch latest')
    args = parser.parse_args()

    project_path = get_project_path(args.project)
    if not os.path.exists(project_path):
        print('No such project: {}'.format(args.project), file=sys.stderr)
        sys.exit(os.EX_DATAERR)

    if args.update:
        print('Updating project {}'.format(args.project))
        update_project(project_path)

    output_dir = get_project_output_dir(project_path)
    if args.clean and os.path.exists(output_dir):
        print('Removing cached analysis')
        shutil.rmtree(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    analyse(project_path)
