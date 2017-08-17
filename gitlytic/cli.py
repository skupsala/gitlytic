import os
import sys
import argparse

from settings import DATA_DIR
from project_utils import get_project_output_dir
from analyser import analyse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('project', help='Project name to be analysed inside data/ dir')
    args = parser.parse_args()

    project_path = os.path.join(DATA_DIR, args.project)
    if not os.path.exists(project_path):
        print(DATA_DIR)
        print('No such project: {}'.format(args.project), file=sys.stderr)
        sys.exit(os.EX_DATAERR)

    output_dir = get_project_output_dir(project_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print('Analyzing {}'.format(args.project))
    analyse(project_path)
