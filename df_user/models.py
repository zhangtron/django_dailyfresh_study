from django.db import models

# Create your models here.

class UserInfo(models.Model):
    uname = models.CharField(max_length=20)
    upwd = models.CharField(max_length=40)
    uemail = models.CharField(max_length=40)
    uaddr = models.CharField(max_length=100,default='')
    unickname = models.CharField(max_length=20,default='')
    upostal = models.CharField(max_length=6,default='')
    uphone = models.CharField(max_length=11,default='')
    # default, blank是python层面的约束，不影响数据库结构修改后不用迁移
