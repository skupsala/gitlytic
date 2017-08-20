set -e

source venv/bin/activate
pycharm . &
cd gitlytic/notebooks
jupyter notebook
