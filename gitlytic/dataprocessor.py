import os
import pandas as pd

import settings
from utils import default_logger as logger
from project import get_project_output_dir


def load_project_commits(project_path):
    project_df = None
    for f in os.listdir(get_project_output_dir(project_path)):
        if f.startswith('git_log_') and f.endswith('.tsv'):
            repo_name = f.replace('git_log_', '', 1).replace('.tsv', '', 1)
            repo_df = load_repo_commits(project_path, repo_name)
            if project_df is None:
                project_df = repo_df
            else:
                project_df = pd.concat([project_df, repo_df], verify_integrity=True)
    return project_df


def load_repo_commits(project_path, repo_name):
    logger.info('Loading commits dataframe for {}'.format(repo_name))
    project_output_dir = get_project_output_dir(project_path)
    repo_git_log_tsv_path = os.path.join(project_output_dir, 'git_log_{}.tsv'.format(repo_name))
    return pd.DataFrame.from_csv(repo_git_log_tsv_path, sep=settings.FIELD_SEPARATOR,
                                 parse_dates=['author_date', 'committer_date'], infer_datetime_format=True)
