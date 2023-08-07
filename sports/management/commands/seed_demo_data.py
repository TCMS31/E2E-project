"""Populate the database with a small, realistic roster.

Used for local development and for capturing the screenshots in docs/. It is
idempotent: running it twice leaves the same rows behind.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

TEAMS = [
    ('Austin', 'Comets'),
    ('Boston', 'Rockets'),
    ('Chicago', 'Wolves'),
    ('Denver', 'Summits'),
    ('Portland', 'Anchors'),
]

PLAYERS = [
    ('Ada', 'Lovelace', ['Boston Rockets']),
    ('Grace', 'Hopper', ['Boston Rockets', 'Denver Summits']),
    ('Alan', 'Turing', ['Chicago Wolves']),
    ('Katherine', 'Johnson', ['Austin Comets', 'Portland Anchors']),
    ('Mary', 'Jackson', ['Austin Comets']),
    ('Dorothy', 'Vaughan', ['Denver Summits']),
    ('Barbara', 'Liskov', ['Portland Anchors', 'Chicago Wolves']),
    ('Radia', 'Perlman', ['Boston Rockets']),
    ('Margaret', 'Hamilton', ['Chicago Wolves']),
    ('Shafi', 'Goldwasser', []),
]


class Command(BaseCommand):
    help = 'Create demo teams, players and a demo user.'

    def add_arguments(self, parser):
        parser.add_argument('--user', default='demo', help='Username to create.')
        parser.add_argument(
            '--password', default='demo-password-123', help='Password for the demo user.'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from sports.models import Player, Team

        teams = {}
        for city, mascot in TEAMS:
            team, _ = Team.objects.get_or_create(city=city, mascot=mascot)
            teams[f'{city} {mascot}'] = team

        for first, last, memberships in PLAYERS:
            player, _ = Player.objects.get_or_create(first_name=first, last_name=last)
            player.teams.set(teams[name] for name in memberships)

        user_model = get_user_model()
        username = options['user']
        user, created = user_model.objects.get_or_create(username=username)
        if created:
            user.set_password(options['password'])
            user.save(update_fields=['password'])

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded {len(TEAMS)} teams, {len(PLAYERS)} players and user "{username}".'
            )
        )
