"""HTTP layer for the sports app.

Every view here is thin on purpose: it names a template and delegates the
queryset to :mod:`sports.selectors`. Anything that looks like a query decision
(joins, prefetching, ordering) belongs in that module, not in this one.
"""

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from . import selectors
from .forms import PlayerForm, TeamForm


class PaginatedListView(LoginRequiredMixin, ListView):
    """Shared base for the roster list pages.

    Reads the page size from settings at request time so every list view
    paginates the same way, and so a future list view gets pagination by
    inheriting rather than by remembering to set an attribute.
    """

    def get_paginate_by(self, queryset):
        return settings.PAGE_SIZE


class HomeView(LoginRequiredMixin, View):
    """Landing page with links into the two rosters."""

    def get(self, request):
        return render(request, 'index.html')


class TeamListView(PaginatedListView):
    template_name = 'team_list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        return selectors.team_list()


class TeamCreateView(LoginRequiredMixin, CreateView):
    form_class = TeamForm
    template_name = 'team_form.html'
    success_url = reverse_lazy('team_list')
    extra_context = {
        'heading': 'Add a team',
        'submit_label': 'Create team',
        'cancel_url': reverse_lazy('team_list'),
    }


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    form_class = TeamForm
    template_name = 'team_form.html'
    success_url = reverse_lazy('team_list')
    extra_context = {
        'heading': 'Edit team',
        'submit_label': 'Save changes',
        'cancel_url': reverse_lazy('team_list'),
    }

    def get_queryset(self):
        return selectors.team_detail_queryset()


class TeamDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'team_confirm_delete.html'
    success_url = reverse_lazy('team_list')
    context_object_name = 'team'

    def get_queryset(self):
        return selectors.team_detail_queryset()


class TeamDetailView(LoginRequiredMixin, DetailView):
    template_name = 'team_detail.html'
    context_object_name = 'team'

    def get_queryset(self):
        return selectors.team_detail_queryset()


class PlayerListView(PaginatedListView):
    template_name = 'player_list.html'
    context_object_name = 'players'

    def get_queryset(self):
        return selectors.player_list()


class PlayerCreateView(LoginRequiredMixin, CreateView):
    form_class = PlayerForm
    template_name = 'player_form.html'
    success_url = reverse_lazy('player_list')
    extra_context = {
        'heading': 'Add a player',
        'submit_label': 'Create player',
        'cancel_url': reverse_lazy('player_list'),
    }


class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PlayerForm
    template_name = 'player_form.html'
    success_url = reverse_lazy('player_list')
    extra_context = {
        'heading': 'Edit player',
        'submit_label': 'Save changes',
        'cancel_url': reverse_lazy('player_list'),
    }

    def get_queryset(self):
        return selectors.player_detail_queryset()


class PlayerDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'player_confirm_delete.html'
    success_url = reverse_lazy('player_list')
    context_object_name = 'player'

    def get_queryset(self):
        return selectors.player_detail_queryset()


class PlayerDetailView(LoginRequiredMixin, DetailView):
    template_name = 'player_detail.html'
    context_object_name = 'player'

    def get_queryset(self):
        return selectors.player_detail_queryset()


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class LoginView(DjangoLoginView):
    """Login page.

    Where to send a user after login is Django's ``LOGIN_REDIRECT_URL``;
    ``success_url`` is not consulted by ``LoginView`` and setting it has no
    effect, which is why it is absent here.
    """

    form_class = AuthenticationForm
    template_name = 'login.html'
    redirect_authenticated_user = True


class LogoutView(View):
    """Log the current user out.

    POST only: a logout reachable by GET can be triggered by any third-party
    page embedding the URL, and prefetching browsers can fire it by accident.
    """

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


def healthz(request):
    """Liveness/readiness probe for the container healthcheck.

    Touches the database so a healthy response means more than "the process is
    up". Unauthenticated by design: probes do not hold sessions.
    """
    try:
        connection.ensure_connection()
    except Exception:  # noqa: BLE001 - any driver error means "not ready"
        return JsonResponse({'status': 'error', 'database': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok', 'database': 'ok'})


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


def custom_500_view(request):
    return render(request, '500.html', status=500)
