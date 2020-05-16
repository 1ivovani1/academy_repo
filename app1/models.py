from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15,null=False,default='')
    avatar = models.FileField(upload_to='media/avatars/',null=False,default='../static/main_avatar.jpg')

class Ad(models.Model):
    name = models.CharField(max_length=200,null=False,default='Новое обьявление')
    description = models.TextField(null=False,default='Описание обьявления')
    price = models.IntegerField(null=False,default=0)
    image = models.FileField(upload_to='media/',null=False)
    owner = models.CharField(max_length=255,null=False,default='')
    owner_id = models.IntegerField(null=False,default=0)

    def __str__(self):
        return self.name
