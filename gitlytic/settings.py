import os

DATA_DIR = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'data'))
DELIMITER = ','
QUOTECHAR = '"'

PROJECT_DEFAULT_SETTINGS = {
    'analysis_branch': 'origin/master',
    'snapshot_timedelta': {
        'weeks': 1
    }
}
