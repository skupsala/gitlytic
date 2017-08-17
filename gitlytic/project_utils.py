import os


def get_project_output_dir(project_path):
    return os.path.join(project_path, '.gitlytic')
