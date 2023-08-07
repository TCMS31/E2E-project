"""Query layer for the sports app.

Views describe *what* to render; this module decides *how* the rows are
fetched. Keeping the querysets here means the join strategy, the prefetching
and any future filtering live in one testable place instead of being spread
across a dozen class-based views.
"""

from django.db.models import Count, Prefetch

from .models import Player, Team


def team_list():
    """Teams for the index page, with their roster size already counted.

    ``Count`` is an aggregate on the same query, so rendering the roster size
    for N teams costs one query rather than N.
    """
    return Team.objects.annotate(player_count=Count('players')).order_by('city', 'mascot')


def team_detail_queryset():
    """Teams with their roster prefetched, for the detail page."""
    return Team.objects.prefetch_related(
        Prefetch('players', queryset=Player.objects.order_by('last_name', 'first_name'))
    )


def player_list():
    """Players with their team memberships prefetched.

    The list template renders each player's teams. Without the prefetch that is
    one extra query per row (a classic N+1); with it the whole page is two
    queries regardless of how many players are shown.
    """
    return Player.objects.prefetch_related('teams').order_by('last_name', 'first_name')


def player_detail_queryset():
    """Players with team memberships prefetched, for the detail page."""
    return Player.objects.prefetch_related('teams')
