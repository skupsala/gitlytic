set -e

source gl/bin/activate
pycharm . &
cd gitlytic/notebooks
jupyter notebook
