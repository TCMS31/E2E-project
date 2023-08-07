"""Pytest bootstrap.

The settings module refuses to start without DJANGO_SECRET_KEY when DEBUG is
off, which is exactly the production behaviour we want. Tests supply a
throwaway key here so the suite exercises the DEBUG-off path.
"""

import os

os.environ.setdefault('DJANGO_SECRET_KEY', 'test-only-key-not-used-anywhere-else')
os.environ.setdefault('DJANGO_ALLOWED_HOSTS', 'testserver,localhost,127.0.0.1')
