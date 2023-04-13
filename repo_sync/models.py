from django.db import models

class Repository(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    last_synced = models.DateTimeField(auto_now_add=True)

class File(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    content = models.TextField()
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
