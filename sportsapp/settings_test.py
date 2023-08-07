"""Settings for the pytest suite.

pytest-django imports the settings module before any conftest.py runs, so a
key set from conftest arrives too late and the production settings refuse to
load. Supplying the throwaway key here keeps the suite on the DEBUG-off path
without asking contributors to export anything.
"""

import os

os.environ.setdefault('DJANGO_SECRET_KEY', 'test-only-key-not-used-anywhere-else')
os.environ.setdefault('DJANGO_ALLOWED_HOSTS', 'testserver,localhost,127.0.0.1')

from .settings import *  # noqa: E402, F403
