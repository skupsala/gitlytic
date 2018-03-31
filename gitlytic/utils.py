import os
import logging

# Default logger is used by third party packages eg. gitpython
default_logger = logging.getLogger()
default_logger.setLevel(logging.WARNING)
default_logger.addHandler(logging.StreamHandler())

logger = logging.getLogger('gitlytic')
logger.propagate = False
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, directory):
        self._dir = directory
        self._cwd = os.getcwd()
        self._pwd = self._cwd

    def __enter__(self):
        self._pwd = self._cwd
        os.chdir(self._dir)
        self._cwd = os.getcwd()
        return self

    def __exit__(self, *args):
        os.chdir(self._pwd)
        self._cwd = self._pwd
