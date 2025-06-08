from .models import spotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post, put, get
import requests

BASE_URL = "https://api.spotify.com/v1/me/"


def get_user_tokens(session_id):
    """
    获取用户的 Spotify token,如果不存在则返回 None。
    """
    try:
        user_tokens = spotifyToken.objects.filter(user=session_id)
        if user_tokens.exists():
            return user_tokens[0]
        return None
    except Exception as e:
        print(f"Error fetching tokens for user {session_id}: {e}")
        return None


def update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token):
    """
    更新或创建用户的 Spotify token。
    """
    try:
        expires_in = timezone.now() + timedelta(seconds=expires_in)
        tokens = get_user_tokens(session_id)

        if tokens:
            # 更新现有的 token 信息
            tokens.access_token = access_token
            tokens.token_type = token_type
            tokens.refresh_token = refresh_token
            tokens.expires_in = expires_in
            tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
        else:
            # 创建新的 token
            tokens = spotifyToken(user=session_id, access_token=access_token, refresh_token=refresh_token,
                                  token_type=token_type, expires_in=expires_in)
            tokens.save()
    except Exception as e:
        print(f"Error updating/creating tokens for user {session_id}: {e}")


def is_spotify_authenticated(session_id):
    """
    检查 Spotify token 是否有效，若无效则尝试刷新 token。
    """
    tokens = get_user_tokens(session_id)
    if tokens:
        if tokens.expires_in <= timezone.now():
            # Token 已过期，刷新 token
            refresh_spotify_token(session_id)
            tokens = get_user_tokens(session_id)  # 刷新后的 token 信息
            if tokens and tokens.expires_in > timezone.now():
                return True
        else:
            return True
    return False


def refresh_spotify_token(session_id):
    """
    刷新用户的 Spotify token。
    """
    tokens = get_user_tokens(session_id)
    if not tokens:
        # print(f"No tokens found for user {session_id}")
        return

    refresh_token = tokens.refresh_token
    try:
        response = post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }).json()

        access_token = response.get('access_token')
        token_type = response.get('token_type')
        expires_in = response.get('expires_in')
        new_refresh_token = response.get('refresh_token')

        # 如果没有返回新的 refresh_token，使用旧的 refresh_token
        if new_refresh_token is None:
            new_refresh_token = refresh_token

        if access_token:
            update_or_create_user_tokens(session_id, access_token, token_type, expires_in, new_refresh_token)
        else:
            print(f"Failed to refresh token for session {session_id}, response: {response}")
            return {'Error': 'Failed to refresh Spotify token'}

    except requests.exceptions.RequestException as e:
        print(f"Error while refreshing token for session {session_id}: {str(e)}")
        return {'Error': f'Request failed: {str(e)}'}


def execute_spotify_api_request(session_id, endpoint, post_=False, put_=False):
    tokens = get_user_tokens(session_id)

    if not tokens:
        return {'Error': 'No Spotify token found for user'}

    # 如果 token 过期，则刷新
    if tokens.expires_in <= timezone.now():
        refresh_spotify_token(session_id)
        tokens = get_user_tokens(session_id)  # 刷新后的 token

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {tokens.access_token}'
    }

    try:
        # 处理 POST 请求
        if post_:
            response = post(BASE_URL + endpoint, headers=headers)
        # 处理 PUT 请求
        elif put_:
            response = put(BASE_URL + endpoint, headers=headers)
        # 默认 GET 请求
        else:
            response = get(BASE_URL + endpoint, headers=headers)

        print(f"Response Status: {response.status_code}, Response Text: {response.text}")

        if response.status_code == 204:
            return {'Message': 'No content, but request was successful'}
        if response.status_code != 200:
            return {'Error': f"Request failed with status {response.status_code}", 'Response': response.text}

        return response.json() if response.text else {'Error': 'Empty response from Spotify'}

    except requests.exceptions.RequestException as e:
        # print(f"Error in API request: {e}")
        return {'Error': 'Request failed', 'details': str(e)}

def play_song(session_id):
    return execute_spotify_api_request(session_id,"player/play",put_=True)

def pause_song(session_id):
    return execute_spotify_api_request(session_id,"player/pause",put_=True)
# 该功能必须为Spotify的付费用户，免费用户api通不过~
def skip_song(user):
    try:
        token = spotifyToken.objects.get(user=user)  # 确保宿主已绑定 Spotify 账号
    except spotifyToken.DoesNotExist:
        return {'Error': 'Host has not connected Spotify'}  # 明确错误信息
    
    # 检查令牌是否过期（需确保时区正确）
    
    if token.expires_in <= timezone.now():
        # 刷新令牌
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': token.refresh_token,
            'client_id': 'YOUR_SPOTIFY_CLIENT_ID',  # 替换为实际值
            'client_secret': 'YOUR_SPOTIFY_CLIENT_SECRET',
        }
        response = requests.post('https://accounts.spotify.com/api/token', data=payload)
        if response.status_code != 200:
            return {'Error': 'Failed to refresh Spotify token'}
        
        data = response.json()
        # 更新令牌信息
        update_or_create_user_tokens(
            session_id=user,
            access_token=data['access_token'],
            token_type=data.get('token_type', 'Bearer'),
            expires_in=data.get('expires_in', 3600),
            refresh_token=data.get('refresh_token', token.refresh_token)
        )
    # 执行跳过操作
    headers = {'Authorization': f'Bearer {token.access_token}'}
    response = requests.post('https://api.spotify.com/v1/me/player/next', headers=headers)
    if response.status_code not in (200, 204):
        return {'Error': 'Spotify API error: ' + response.text}

