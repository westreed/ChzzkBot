import os
import sys


def resource_path(relative_path: str):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = "."

    return os.path.join(base_path, relative_path)


def get_abs_path(relative_path: str):
    return os.path.abspath(relative_path)