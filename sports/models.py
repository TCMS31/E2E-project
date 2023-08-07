"""Domain models for the sports roster.

A :class:`Player` may appear on several :class:`Team` rosters, so the two are
joined by a many-to-many relation. The reverse accessor is named ``players``
(rather than Django's default ``player_set``) because the templates and the
selectors layer read a team's roster as ``team.players``.
"""

from django.db import models
from django.db.models.functions import Lower


class Team(models.Model):
    """A club, identified by the city it plays in and its mascot.

    Uniqueness ignores case: "Boston Rockets" and "boston rockets" are the same
    club, and letting both in splits one roster across two rows.
    """

    city = models.CharField(max_length=100)
    mascot = models.CharField(max_length=100)

    class Meta:
        ordering = ('city', 'mascot')
        constraints = (
            models.UniqueConstraint(
                Lower('city'),
                Lower('mascot'),
                name='unique_team_city_mascot_ci',
                violation_error_message='A team with this city and mascot already exists.',
            ),
        )

    def __str__(self):
        return f'{self.city} {self.mascot}'


class Player(models.Model):
    """A person who can be on the roster of zero or more teams."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    teams = models.ManyToManyField(Team, related_name='players', blank=True)

    class Meta:
        ordering = ('last_name', 'first_name')
        indexes = (models.Index(fields=('last_name', 'first_name'), name='player_name_idx'),)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
