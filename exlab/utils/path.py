import os
from pathlib import Path


def basepath(file_: str, parent: int=0) -> str:
    """
    :return: Base folder, containing the *data*, *src*... folders
    """
    path = Path(file_).resolve()
    for _ in range(parent + 1):
        path = path.parent
    return path

def extpath(path: str, extension: str) -> str:
    extension = extension.strip('.')
    return '{}.{}'.format(os.path.splitext(path)[0], extension)


def ymlpath(path: str) -> str:
    return extpath(path, 'yml')


def ymlbpath(base: str, path: str) -> str:
    return os.path.join(base, extpath(path, 'yml'))
