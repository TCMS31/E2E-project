"""Shared fixtures for the sports test suite."""

import pytest
from django.contrib.auth.models import User

from sports.models import Player, Team


@pytest.fixture
def password():
    return 'a-sufficiently-long-test-password'


@pytest.fixture
def user(db, password):
    return User.objects.create_user(username='coach', email='coach@example.com', password=password)


@pytest.fixture
def auth_client(client, user, password):
    client.force_login(user)
    return client


@pytest.fixture
def team(db):
    return Team.objects.create(city='Boston', mascot='Rockets')


@pytest.fixture
def player(db, team):
    p = Player.objects.create(first_name='Ada', last_name='Lovelace')
    p.teams.add(team)
    return p
