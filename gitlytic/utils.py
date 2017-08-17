import os


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
