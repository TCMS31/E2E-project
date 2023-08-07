"""Django admin registrations.

The admin is the fastest way to inspect and seed data during development, so
both models are registered with list views that match the public pages.
"""

from django.contrib import admin

from .models import Player, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('city', 'mascot')
    search_fields = ('city', 'mascot')
    ordering = ('city', 'mascot')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name')
    ordering = ('last_name', 'first_name')
    filter_horizontal = ('teams',)
