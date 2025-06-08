# 序列转换器，可以理解为是数据转换，方便前后端用json交互。
from  rest_framework import serializers
from .models import Room
class RoomSerializers(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id','code','host','guest_can_pause','votes_to_skip','created_at')
        
class CreateRoomSerializers(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('guest_can_pause','votes_to_skip')
 

class UpdateRoomSerializers(serializers.ModelSerializer):
    code = serializers.CharField(validators=[])
    # 重新定义了code，因为表里面是unique
    class Meta:
        model = Room
        fields = ('guest_can_pause','votes_to_skip','code')
        

        