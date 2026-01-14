from django.db import models
from datetime import datetime, timezone

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=30, unique=True)
    passhash = models.CharField()
    is_active = models.BooleanField()
    is_admin = models.BooleanField()


class UserPermission(models.Model):
    group = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField()


class Session(models.Model):
    uuid = models.UUIDField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()

    def is_active(self) -> bool:
        return self.expires_at > datetime.now(timezone.utc)
