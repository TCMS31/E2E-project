"""Authentication and access-control behaviour."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

PROTECTED_URLS = [
    ('home', ()),
    ('team_list', ()),
    ('team_create', ()),
    ('player_list', ()),
    ('player_create', ()),
]


@pytest.mark.parametrize('name,args', PROTECTED_URLS)
def test_anonymous_user_is_redirected_to_login(client, db, name, args):
    response = client.get(reverse(name, args=args))
    assert response.status_code == 302
    assert response.url.startswith(reverse('login'))


@pytest.mark.parametrize('name', ['team_detail', 'team_update', 'team_delete'])
def test_anonymous_user_cannot_reach_team_detail_pages(client, team, name):
    response = client.get(reverse(name, args=(team.pk,)))
    assert response.status_code == 302
    assert response.url.startswith(reverse('login'))


def test_login_sends_user_to_the_team_list(client, user, password):
    response = client.post(reverse('login'), {'username': user.username, 'password': password})
    assert response.status_code == 302
    assert response.url == reverse('team_list')


def test_signup_creates_a_user_and_redirects_to_login(client, db):
    response = client.post(
        reverse('signup'),
        {
            'username': 'newcoach',
            'password1': 'a-sufficiently-long-password',
            'password2': 'a-sufficiently-long-password',
        },
    )
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert User.objects.filter(username='newcoach').exists()


def test_logout_requires_post(auth_client):
    """A GET-able logout can be fired by any third-party page or prefetcher."""
    assert auth_client.get(reverse('logout')).status_code == 405


def test_logout_via_post_ends_the_session(auth_client):
    response = auth_client.post(reverse('logout'))
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert auth_client.get(reverse('team_list')).status_code == 302
