import pytest
from django.contrib.auth.models import User
from Api.models import Room
from spotify.models import spotifyToken
from django.utils import timezone
from datetime import timedelta
import sys
print(sys.executable)

@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass123")

@pytest.fixture
def room(db):
    return Room.objects.create(
        host="host_session_key",
        guest_can_pause=True,
        votes_to_skip=2
    )
    
@pytest.fixture
def spotify_token(db):
    return spotifyToken.objects.create(
        user="user_session_key",
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=timezone.now() + timedelta(hours=1)
    )