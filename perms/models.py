from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=30)
    passhash = models.CharField()
    is_active = models.BooleanField()
    is_admin = models.BooleanField()


class UserPermission(models.Model):
    group = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField()


class Session(models.Model):
    uuid = models.UUIDField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
