from django.db import models

class Message(models.Model):
    session_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=50)
    message = models.TextField()

    def __str__(self):
        return f"{self.sender}: {self.message}"
