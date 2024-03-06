from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Message(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    sent_time = models.DateTimeField(default=timezone.now)  # Default value is the current time
    sender_is_read = models.BooleanField(default=False)
    receiver_is_read = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-sent_time']  # Messages will be ordered by sent time, newest first

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.sent_time}"

