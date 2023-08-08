"""Measure the cost of rendering the player list as the roster grows.

Compares the naive queryset (what the views used before the selectors layer
existed) against ``sports.selectors.player_list``. Run it with:

    DJANGO_DEBUG=1 python scripts/benchmark_roster.py
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportsapp.settings')
os.environ.setdefault('DJANGO_DEBUG', '1')

import django  # noqa: E402

django.setup()

from django.db import connection  # noqa: E402
from django.template.loader import render_to_string  # noqa: E402
from django.test.runner import DiscoverRunner  # noqa: E402
from django.test.utils import (  # noqa: E402
    CaptureQueriesContext,
    setup_test_environment,
    teardown_test_environment,
)

from sports import selectors  # noqa: E402
from sports.models import Player, Team  # noqa: E402

SIZES = (50, 200, 1000)
TEMPLATE = 'player_list.html'


def build_roster(size):
    Player.objects.all().delete()
    Team.objects.all().delete()
    teams = [Team.objects.create(city=f'City{i:03d}', mascot='Club') for i in range(10)]
    through = Player.teams.through
    players = Player.objects.bulk_create(
        Player(first_name=f'First{i:05d}', last_name=f'Last{i:05d}') for i in range(size)
    )
    through.objects.bulk_create(
        through(player_id=p.pk, team_id=teams[i % len(teams)].pk) for i, p in enumerate(players)
    )


def measure(queryset):
    start = time.perf_counter()
    with CaptureQueriesContext(connection) as ctx:
        render_to_string(TEMPLATE, {'players': list(queryset)})
    return len(ctx), (time.perf_counter() - start) * 1000


def main():
    setup_test_environment()
    runner = DiscoverRunner(verbosity=0, interactive=False)
    old_config = runner.setup_databases()
    try:
        print(
            f'{"rows":>6} | {"naive q":>8} {"naive ms":>9} | {"selector q":>11} {"selector ms":>12}'
        )
        print('-' * 60)
        for size in SIZES:
            build_roster(size)
            naive_q, naive_ms = measure(Player.objects.order_by('last_name'))
            fast_q, fast_ms = measure(selectors.player_list())
            print(f'{size:>6} | {naive_q:>8} {naive_ms:>9.1f} | {fast_q:>11} {fast_ms:>12.1f}')
    finally:
        runner.teardown_databases(old_config)
        teardown_test_environment()


if __name__ == '__main__':
    main()
