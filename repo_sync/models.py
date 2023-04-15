from django.db import models
from django.contrib.auth.models import User

class Repository(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField()
    last_synced = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='repositories/', blank=True, null=True)

    def __str__(self):
        return self.name

class File(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=255)

    def __str__(self):
        return self.name