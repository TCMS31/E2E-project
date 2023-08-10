"""Query-count guards.

These are the regression tests for the N+1 that the selectors layer removes.
They assert a *constant* query count so the guard keeps working as the page
size changes.
"""

import pytest
from django.urls import reverse

from sports.models import Player, Team


@pytest.fixture
def populated_roster(db):
    teams = [Team.objects.create(city=f'City{i}', mascot=f'Mascot{i}') for i in range(5)]
    players = []
    for i in range(40):
        p = Player.objects.create(first_name=f'First{i}', last_name=f'Last{i:02d}')
        p.teams.add(teams[i % len(teams)])
        players.append(p)
    return teams, players


def test_player_list_query_count_is_constant(
    auth_client, populated_roster, django_assert_num_queries
):
    """Rendering N players must not cost N queries.

    Five queries in total: session and user lookups, the paginator count, the
    page of players, and one query for all of their team memberships. Without
    ``prefetch_related`` the last of those becomes one query per row.
    """
    with django_assert_num_queries(5):
        response = auth_client.get(reverse('player_list'))
    assert response.status_code == 200


def test_player_list_queries_do_not_grow_with_the_number_of_rows(
    auth_client, db, django_capture_on_commit_callbacks
):
    """The strongest form of the N+1 guard: cost is flat in the row count."""
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    def queries_for(n):
        Player.objects.all().delete()
        Team.objects.all().delete()
        t = Team.objects.create(city='Flat', mascot='Cost')
        for i in range(n):
            Player.objects.create(first_name=f'F{i}', last_name=f'L{i:02d}').teams.add(t)
        with CaptureQueriesContext(connection) as ctx:
            assert auth_client.get(reverse('player_list')).status_code == 200
        return len(ctx)

    assert queries_for(5) == queries_for(25)


def test_team_list_query_count_is_constant(
    auth_client, populated_roster, django_assert_num_queries
):
    """Roster sizes come from one annotated aggregate, not one query per team."""
    with django_assert_num_queries(4):
        response = auth_client.get(reverse('team_list'))
    assert response.status_code == 200


def test_lists_are_paginated(auth_client, populated_roster, settings):
    settings.PAGE_SIZE = 25
    response = auth_client.get(reverse('player_list'))
    assert response.context['is_paginated'] is True
    assert len(response.context['players']) == 25
    assert response.context['paginator'].count == 40

    page_two = auth_client.get(reverse('player_list'), {'page': 2})
    assert len(page_two.context['players']) == 15


def test_pagination_pages_do_not_overlap(auth_client, populated_roster):
    first = {p.pk for p in auth_client.get(reverse('player_list')).context['players']}
    second = {p.pk for p in auth_client.get(reverse('player_list'), {'page': 2}).context['players']}
    assert not first & second
    assert len(first | second) == 40
