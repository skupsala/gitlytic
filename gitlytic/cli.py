import os
import sys
import argparse

from project_utils import get_project_output_dir, get_project_path
from analyser import analyse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('project', help='Project name to be analysed inside data/ dir')
    args = parser.parse_args()

    project_path = get_project_path(args.project)
    if not os.path.exists(project_path):
        print('No such project: {}'.format(args.project), file=sys.stderr)
        sys.exit(os.EX_DATAERR)

    output_dir = get_project_output_dir(project_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print('Analyzing {}'.format(args.project))
    analyse(project_path)
