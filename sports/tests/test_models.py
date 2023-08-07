"""Model-level behaviour, including the reverse-accessor regression."""

import pytest
from django.db import IntegrityError

from sports.models import Player, Team


def test_team_str(team):
    assert str(team) == 'Boston Rockets'


def test_player_str_and_full_name(player):
    assert str(player) == 'Ada Lovelace'
    assert player.full_name == 'Ada Lovelace'


def test_team_exposes_players_reverse_accessor(team, player):
    """Regression: the detail template reads ``team.players``.

    Before ``related_name='players'`` existed the accessor was ``player_set``,
    so the template silently rendered an empty roster for every team.
    """
    assert list(team.players.all()) == [player]


def test_duplicate_team_is_rejected(team):
    with pytest.raises(IntegrityError):
        Team.objects.create(city='Boston', mascot='Rockets')


def test_players_are_ordered_by_name(db):
    Player.objects.create(first_name='Zoe', last_name='Adams')
    Player.objects.create(first_name='Alan', last_name='Turing')
    assert [p.last_name for p in Player.objects.all()] == ['Adams', 'Turing']


def test_deleting_a_team_keeps_its_players(team, player):
    team.delete()
    player.refresh_from_db()
    assert player.teams.count() == 0
