from datetime import timedelta
from django.utils import timezone
from spotify.util import *
from . import conftest
from rest_framework.test import APIClient
from django.urls import reverse

def test_refresh_spotify_token_success(db, spotify_token, mocker):
    # Mock Spotify API 响应
    mock_post = mocker.patch("requests.post")
    mock_post.return_value.json.return_value = {
        "access_token": "new_access_token",
        "expires_in": 3600,
        "refresh_token": "new_refresh_token"
    }

    # 调用刷新函数
    refresh_spotify_token("user_session_key")

    # 验证 Token 是否更新
    token = spotifyToken.objects.get(user="user_session_key")
    assert token.access_token == "new_access_token"
    
def test_token_expiration_flow(db, spotify_token, mocker):
    # 设置 Token 为过期状态
    spotify_token.expires_in = timezone.now() - timedelta(minutes=5)
    spotify_token.save()

    # Mock 刷新逻辑
    mocker.patch("spotify.util.refresh_spotify_token")
    
    client = APIClient()
    response = client.get(reverse("spotify-current-song"))
    assert "error" not in response.json()