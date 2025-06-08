from django.shortcuts import render,redirect
from .credentials import REDIRECT_URI,CLIENT_ID,CLIENT_SECRET
from rest_framework.views import APIView
from requests import Request,post
from rest_framework import status
from rest_framework.response import Response
from .util import *
from Api.models import Room
import logging


logger = logging.getLogger('django')

class AuthURL(APIView):
    def get(self,request,format=None):
        # 用户-读取-播放状态 用户-修改-播放状态 用户-读取-当前播放
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
        
        url = Request('GET','https://accounts.spotify.com/authorize',params={
            'scope':scopes,
            'response_type':'code',
            'redirect_uri':REDIRECT_URI,
            'client_id':CLIENT_ID
        }).prepare().url
        
        return Response({'url':url},status=status.HTTP_200_OK)
    
# def spotify_callback(request,fotmat=None):
#     code = request.GET.get('code')
#     error = request.GET.get('error')
#     response = post('https://accounts.spotify.com/api/token',data={
#         'grant_type':'authorization_code',
#         'code':code,
#         'redirect_uri':REDIRECT_URI,
#         'client_id':CLIENT_ID,
#         'client_secret':CLIENT_SECRET     
#     }).json()
    
#     access_token = response.get('access_token')
#     token_type = response.get('token_type')
#     refresh_token = response.get('refresh_token')
#     expires_in = response.get('expires_in')
#     error = response.get('error')
    
#     if not request.session.exists(request.session.session_key):
#         request.session.create()
        
#     update_or_create_user_tokens(
#         request.session.session_key,access_token,token_type,expires_in,refresh_token
#     )
    
#     return  redirect('frontend:')
def spotify_callback(request, format=None):
    code = request.GET.get('code')
    url_error = request.GET.get('error')
    
    if url_error:
        logger.error(f"Spotify auth error: {url_error}")
        return redirect('frontend:error')
    
    if not code:
        return redirect('frontend:')
    
    try:
        response = post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET          
        })
        response_data = response.json()
        
        access_token = response_data.get('access_token')
        token_type = response_data.get('token_type')
        refresh_token = response_data.get('refresh_token')
        expires_in = response_data.get('expires_in')
        api_error = response_data.get('error')
        
        if api_error or not access_token:
            logger.error(f"Spotify API error: {api_error}")
            return redirect('frontend:error')
            
        if not request.session.exists(request.session.session_key):
            request.session.create()
            
        update_or_create_user_tokens(
            request.session.session_key,
            access_token,
            token_type,
            expires_in,
            refresh_token
        )
        
        return redirect('frontend:')
        
    except Exception as e:
        logger.error(f"Exception in spotify_callback: {str(e)}")
        return redirect('frontend:error')


class IsAuthenticated(APIView):
    def get(self,request,format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status':is_authenticated},status=status.HTTP_200_OK)
    
class CurrentSong(APIView):
    def get (self,request,format = None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({},status=status.HTTP_404_NOT_FOUND)
        host = room.host
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(host,endpoint)
        print(response)
        if  'error' in response or 'item' not in response:
            return Response({},status=status.HTTP_204_NO_CONTENT)
        
        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')

        artist_string = ""
        for i, artists in enumerate(item.get('artists')):
            if i > 0:
                artist_string += ","
            name = artists.get('name')
            artist_string += name

        song = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': 0,
            'id': song_id
        }

        return  Response(response,status=status.HTTP_200_OK)

class PauseSong(APIView):
    def put(self,response,format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]
        if self.request.session.session_key == room.host  or room.guest_can_pause:
            pause_song(room.host)
            return Response({},status=status.HTTP_204_NO_CONTENT)
        return Response({},status=status.HTTP_403_FORBIDDEN)

class PlaySong(APIView):
    def put(self,response,format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]
        if self.request.session.session_key == room.host  or room.guest_can_pause:
            play_song(room.host)
            return Response({},status=status.HTTP_204_NO_CONTENT)
        return Response({},status=status.HTTP_403_FORBIDDEN)          
        
                
# class SkipSong(APIView):
#     def post(self, request, format=None):
#         room_code = self.request.session.get('room_code')
#         room_qs = Room.objects.filter(code=room_code)
#         if not room_qs.exists():
#             return Response({'Error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
#         room = room_qs[0]
#         result = skip_song(room.host)  # 直接用 room.host，不检查权限，因为初始架构使用session会有问题。
#         if 'Error' in result:
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)
#         return Response({}, status=status.HTTP_204_NO_CONTENT)
    
class SkipSong(APIView):
    def post(self, request, format=None):
        # 确保 session 存在
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            
        room_code = self.request.session.get('room_code')
        room_qs = Room.objects.filter(code=room_code)
        if not room_qs.exists():
            return Response({'Error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
            
        room = room_qs[0]
        # 关键改动：检查当前用户是否是宿主
        if self.request.session.session_key != room.host:
            return Response({'Error': 'Only host can skip'}, status=status.HTTP_403_FORBIDDEN)  # 确保返回 403
            
        # 后续逻辑保持不变
        result = skip_song(room.host)
        if 'Error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response({}, status=status.HTTP_204_NO_CONTENT)