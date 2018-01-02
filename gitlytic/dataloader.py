import os
import pandas as pd

from gitlytic.utils import default_logger as logger
from gitlytic.project import get_project_output_dir, get_project_name


def load_project_commit_df(project_path):
    def date_parser(date_str):
        if date_str:
            return pd.to_datetime(date_str[:-6], format='%Y-%m-%d %H:%M:%S')
        else:
            return None
    project_name = get_project_name(project_path)
    project_output_dir = get_project_output_dir(project_path)
    logger.info('Loading commits dataframe for {}'.format(project_name))
    git_commits_csv_filepath = os.path.join(project_output_dir, 'git_commits_{}.csv'.format(project_name))
    return pd.read_csv(git_commits_csv_filepath, index_col=None, parse_dates=['author_date', 'committer_date'],
                       date_parser=date_parser)
