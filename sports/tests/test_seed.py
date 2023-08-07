"""The seed_demo_data management command used for local demos and screenshots."""

from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command

from sports.management.commands.seed_demo_data import PLAYERS, TEAMS
from sports.models import Player, Team


def _seed(*args):
    call_command('seed_demo_data', *args, stdout=StringIO())


def test_seed_creates_the_demo_roster_and_user(db):
    _seed()
    assert Team.objects.count() == len(TEAMS)
    assert Player.objects.count() == len(PLAYERS)
    assert User.objects.get(username='demo').check_password('demo-password-123')


def test_seed_is_idempotent(db):
    _seed()
    _seed()
    assert Team.objects.count() == len(TEAMS)
    assert Player.objects.count() == len(PLAYERS)
    assert User.objects.filter(username='demo').count() == 1


def test_seed_assigns_the_listed_memberships(db):
    _seed()
    for first, last, memberships in PLAYERS:
        player = Player.objects.get(first_name=first, last_name=last)
        assert sorted(str(team) for team in player.teams.all()) == sorted(memberships)


def test_seed_does_not_reset_an_existing_users_password(db):
    User.objects.create_user(username='demo', password='kept-by-the-owner-123')
    _seed()
    assert User.objects.get(username='demo').check_password('kept-by-the-owner-123')


def test_seed_accepts_a_custom_user(db):
    _seed('--user', 'coach', '--password', 'another-long-password-1')
    assert User.objects.get(username='coach').check_password('another-long-password-1')
