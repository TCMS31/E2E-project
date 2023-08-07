"""End-to-end behaviour of the team and player pages."""

import pytest
from django.urls import reverse

from sports.models import Player, Team


def test_home_page_renders(auth_client):
    response = auth_client.get(reverse('home'))
    assert response.status_code == 200
    assert b'Teams and players' in response.content


def test_team_list_shows_roster_size_for_each_team(auth_client, team, player):
    response = auth_client.get(reverse('team_list'))
    assert response.status_code == 200
    assert response.context['teams'][0].player_count == 1


def test_team_detail_lists_the_roster(auth_client, team, player):
    """Regression: the roster was always rendered as empty.

    ``team_detail.html`` reads ``team.players``; the model had no such accessor,
    and Django templates swallow the resulting attribute error, so the page
    said "No players" no matter how many players the team had.
    """
    response = auth_client.get(reverse('team_detail', args=(team.pk,)))
    assert response.status_code == 200
    body = response.content.decode()
    assert 'Ada Lovelace' in body
    assert 'No players on this roster yet' not in body


def test_player_detail_renders(auth_client, player):
    """Regression: this page raised TemplateDoesNotExist.

    The view pointed at ``player_detail.html``, which had never been written,
    so every "Details" link on the player list was a 500.
    """
    response = auth_client.get(reverse('player_detail', args=(player.pk,)))
    assert response.status_code == 200
    assert b'Ada Lovelace' in response.content


def test_player_list_renders_team_memberships(auth_client, player):
    response = auth_client.get(reverse('player_list'))
    assert response.status_code == 200
    assert b'Boston Rockets' in response.content


def test_create_team(auth_client):
    response = auth_client.post(reverse('team_create'), {'city': '  Austin ', 'mascot': ' Comets '})
    assert response.status_code == 302
    assert response.url == reverse('team_list')
    created = Team.objects.get(city='Austin')
    assert created.mascot == 'Comets'


def test_create_team_rejects_missing_fields(auth_client):
    response = auth_client.post(reverse('team_create'), {'city': '', 'mascot': ''})
    assert response.status_code == 200
    assert response.context['form'].errors
    assert Team.objects.count() == 0


def test_update_team(auth_client, team):
    response = auth_client.post(
        reverse('team_update', args=(team.pk,)),
        {'city': 'Boston', 'mascot': 'Comets'},
    )
    assert response.status_code == 302
    team.refresh_from_db()
    assert team.mascot == 'Comets'


def test_delete_team(auth_client, team):
    response = auth_client.post(reverse('team_delete', args=(team.pk,)))
    assert response.status_code == 302
    assert not Team.objects.filter(pk=team.pk).exists()


def test_create_player_with_team(auth_client, team):
    response = auth_client.post(
        reverse('player_create'),
        {'first_name': 'Grace', 'last_name': 'Hopper', 'teams': [team.pk]},
    )
    assert response.status_code == 302
    created = Player.objects.get(last_name='Hopper')
    assert list(created.teams.all()) == [team]


def test_create_player_without_a_team_is_allowed(auth_client):
    response = auth_client.post(
        reverse('player_create'), {'first_name': 'Solo', 'last_name': 'Agent'}
    )
    assert response.status_code == 302
    assert Player.objects.get(last_name='Agent').teams.count() == 0


def test_update_player(auth_client, player):
    response = auth_client.post(
        reverse('player_update', args=(player.pk,)),
        {'first_name': 'Ada', 'last_name': 'Byron', 'teams': []},
    )
    assert response.status_code == 302
    player.refresh_from_db()
    assert player.last_name == 'Byron'
    assert player.teams.count() == 0


def test_delete_player(auth_client, player):
    response = auth_client.post(reverse('player_delete', args=(player.pk,)))
    assert response.status_code == 302
    assert not Player.objects.filter(pk=player.pk).exists()


def test_missing_team_returns_404(auth_client, db):
    assert auth_client.get(reverse('team_detail', args=(9999,))).status_code == 404


@pytest.mark.parametrize('url_name', ['team_list', 'player_list'])
def test_empty_lists_render_an_empty_state(auth_client, url_name):
    response = auth_client.get(reverse(url_name))
    assert response.status_code == 200
    assert b'Add the first' in response.content


def test_healthz_is_public_and_reports_ok(client, db):
    response = client.get(reverse('healthz'))
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'database': 'ok'}
