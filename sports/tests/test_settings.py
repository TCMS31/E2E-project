"""The settings module's environment handling."""

import importlib

import pytest
from django.core.exceptions import ImproperlyConfigured


def _reload_settings(monkeypatch, **env):
    import sportsapp.settings as settings_module

    for key in ('DJANGO_SECRET_KEY', 'DJANGO_DEBUG', 'DJANGO_ALLOWED_HOSTS'):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return importlib.reload(settings_module)


def test_missing_secret_key_is_fatal_when_debug_is_off(monkeypatch):
    """The committed key is gone; production must supply its own."""
    with pytest.raises(ImproperlyConfigured, match='DJANGO_SECRET_KEY'):
        _reload_settings(monkeypatch, DJANGO_DEBUG='0')


def test_debug_mode_falls_back_to_a_development_key(monkeypatch):
    module = _reload_settings(monkeypatch, DJANGO_DEBUG='1')
    assert module.SECRET_KEY
    assert module.DEBUG is True


def test_allowed_hosts_is_read_as_a_comma_separated_list(monkeypatch):
    module = _reload_settings(
        monkeypatch, DJANGO_DEBUG='1', DJANGO_ALLOWED_HOSTS='a.example, b.example'
    )
    assert module.ALLOWED_HOSTS == ['a.example', 'b.example']


def test_allowed_hosts_is_not_a_wildcard_by_default(monkeypatch):
    module = _reload_settings(monkeypatch, DJANGO_DEBUG='1')
    assert '*' not in module.ALLOWED_HOSTS
