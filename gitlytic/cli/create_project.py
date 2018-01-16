import os
import sys
import argparse
import subprocess

from gitlytic.project import get_project_path
from gitlytic.utils import cd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', help='Project name to be created')
    parser.add_argument('--git-repo-urls', help='List of urls to git repos like: --git-repo-urls url1 url2 url3',
                        nargs='+', default=[])
    args = parser.parse_args()

    project_path = get_project_path(args.project)
    if os.path.exists(project_path):
        print('Project already exists: {}'.format(args.project), file=sys.stderr)
        sys.exit(os.EX_DATAERR)

    if not args.git_repo_urls:
        print('Required git repo urls missing', file=sys.stderr)
        sys.exit(os.EX_DATAERR)

    os.makedirs(project_path)
    with cd(project_path):
        try:
            for git_repo_url in args.git_repo_urls:
                print('Cloning git repo:')
                print(git_repo_url)
                subprocess.check_call('git clone {}'.format(git_repo_url), shell=True)
        except subprocess.CalledProcessError:
            print('Error on cloning project repos', file=sys.stderr)

    print('Project {} created'.format(args.project))
