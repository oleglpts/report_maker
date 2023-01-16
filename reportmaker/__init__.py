import os
import pathlib
from pkg_resources import resource_string


def copy_config():
    files = {
        'data/config.json': 'config.json',
        'data/test/chinook.sqlite': 'test/chinook.sqlite',
        'data/locale/ru/LC_MESSAGES/report.mo': 'locale/ru/LC_MESSAGES/report.mo',
        'data/locale/en/LC_MESSAGES/report.mo': 'locale/en/LC_MESSAGES/report.mo'
    }
    for file_name in files:
        path = pathlib.Path('%s/.report' % os.getenv('HOME'), files[file_name])
        path.parent.mkdir(parents=True, exist_ok=True)
        text = resource_string(__name__, file_name)
        open(str(path), 'wb').write(text)
