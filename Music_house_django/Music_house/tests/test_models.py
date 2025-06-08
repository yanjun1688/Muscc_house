from Api.models import *

def test_generate_unique_code():
    code1 = Room.generate_unique_code()
    code2 = Room.generate_unique_code()
    assert code1 != code2  # 确保生成的代码唯一（需注意测试数据库隔离）

def test_room_creation(db):
    room = Room.objects.create(host="host1", guest_can_pause=True, votes_to_skip=3)
    assert room.code is not None
    assert room.guest_can_pause is True