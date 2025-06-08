from django.shortcuts import render
# from django.http import HttpResponse
from rest_framework import generics,status
from  .serializers import RoomSerializers,CreateRoomSerializers,UpdateRoomSerializers
from .models import  Room
from rest_framework.views import APIView
from rest_framework.response import Response
from  django.http  import JsonResponse
import sys
print(sys.executable)
# Create your views here.
class RoomView(generics.ListAPIView):
    queryset =  Room.objects.all()
    serializer_class = RoomSerializers
# 根据session来执行身份验证，有就用当前的，没有就创建一个
# 用序列转化器验证传入数据是否合法并提前需要的字段，合法后再根据host来判断是否有创建过房间，有就直接更新这两个字段，没有就重新创建一个。



# 看不懂别写了，废物。
# 出大问题，不该用session_key来作为host，会导致host!=实际的用户标识，应该用Django自带的user模型来关联第三方id
class GetRoom(APIView):
    serializer_class = RoomSerializers
    lookup_url_kwarg = 'code'
    
    def get(self,request,format=None):
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data =  RoomSerializers(room[0]).data
                data['is_host'] = self.request.session.session_key ==room[0].host
                return Response(data,status=status.HTTP_200_OK)
            return Response({'Bad Request':"Invalid Room Code"},status=status.HTTP_400_BAD_REQUEST)
        return Response({'Bad Request': "Code parameter not found"}, status=status.HTTP_400_BAD_REQUEST)
class JoinRoom(APIView):
    lookup_url_kwarg = 'code'
    def  post(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
            
        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            room_result  = Room.objects.filter(code=code)
            if len(room_result) > 0 :
                room = room_result[0]
                self.request.session['room_code'] = code 
                return Response({'message':'Room Joined!'},status=status.HTTP_200_OK)
            return Response({'Bad Reques':'Invalid RoomCode!'},status=status.HTTP_400_BAD_REQUEST)
            
            
        return Response({'Bad Request':'Invalid post data, did not find a code key'},status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializers
    
    def post(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if  queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                self.request.session['room_code'] = room.code
                return Response(RoomSerializers(room).data,status=status.HTTP_200_OK)
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause,
                            votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code
                return Response(RoomSerializers(room).data,status=status.HTTP_201_CREATED)
        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserInRoom(APIView):
    def get(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        data = {
            'code':self.request.session.get('room_code')
        }
        return JsonResponse(data,status=status.HTTP_200_OK)

class LeaveRoom(APIView):
    def post(self,request,format=None):
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code')
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host=host_id)
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()
                
        return Response({'Message':'Success'},status=status.HTTP_200_OK)
    
class UpdateRoom(APIView):
    serializers_class = UpdateRoomSerializers
    def patch(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        serialize = self.serializers_class(data=request.data)
        if serialize.is_valid():
            guest_can_pause = serialize.data.get('guest_can_pause')
            votes_to_skip = serialize.data.get('votes_to_skip')
            code = serialize.data.get('code')
            
            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({'message':'Room not found'},status=status.HTTP_404_NOT_FOUND)
            room =queryset[0]
            user_id = self.request.session.session_key
            if room.host !=user_id:
                 return Response({'message':' You are not the host of this room'},status=status.HTTP_403_NOT_FOUND)
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause','votes_to_skip'])
            return Response(RoomSerializers(room).data,status=status.HTTP_200_OK)
        return Response({'Bad Request':'Invalid Data...'},status=status.HTTP_400_BAD_REQUEST)