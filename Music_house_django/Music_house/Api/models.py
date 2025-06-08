from django.db import models
import string
import random
# Create your models here.
# 工具函数：生成唯一房间代码

def generate_unique_code():
    """
    生成一个唯一的6位大写字母房间代码。
    保证代码在 Room 表中不存在，避免冲突。
    """
    length = 6
    while True:
        code = ''.join(random.choices(string.ascii_uppercase,k=length))
        if Room.objects.filter(code=code).count() == 0:
            break
    return code
       
class Room(models.Model):
    """
    数据库模型：房间
    - code: 房间的唯一标识码
    - host: 房间的主机（唯一标识房间拥有者）
    - guest_can_pause: 是否允许客人暂停
    - votes_to_skip: 跳过当前内容需要的投票数
    - created_at: 房间创建时间
    """
    code  =  models.CharField(max_length=8,default=generate_unique_code,unique=True)
    host = models.CharField(max_length=60,unique=True)
    guest_can_pause = models.BooleanField(null=False,default=False)
    votes_to_skip = models.IntegerField(null=False,default=1)
    created_at = models.DateField(auto_now_add=True)