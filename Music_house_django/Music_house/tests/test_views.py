from django.urls import reverse
from rest_framework.test import APIClient
from Api.models import Room
from spotify.util import refresh_spotify_token
import requests_mock
from . import conftest


def test_create_room_api(db):
    client = APIClient()
    response = client.post(
        reverse("create-room"),
        {"guest_can_pause": True, "votes_to_skip": 2},
        format="json"
    )
    assert response.status_code == 201
    assert Room.objects.count() == 1
    
def test_spotify_callback(db, requests_mock):
    # Mock Spotify Token 端点
    requests_mock.post(
        "https://accounts.spotify.com/api/token",
        json={
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_in": 3600
        }
    )

    client = APIClient()
    response = client.get(reverse("spotify-callback") + "?code=testcode")

    # 验证重定向和 Token 存储
    assert response.status_code == 302
    assert spotifyToken.objects.count() == 1