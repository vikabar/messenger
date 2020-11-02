from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Message(models.Model):
    message_body = models.TextField()
    message_subject = models.TextField()
    is_read = models.BooleanField(default=False)
    creation_date = models.DateTimeField(editable=False, auto_now_add=True)
    sender = models.ForeignKey('auth.User', related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey('auth.User', related_name='received_messages', on_delete=models.CASCADE)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_receiver = models.BooleanField(default=False)

    def mark_deleted_by_sender(self):
        self.is_deleted_by_sender = True
        self.save()

    def mark_deleted_by_receiver(self):
        self.is_deleted_by_receiver = True
        self.save()

    def mark_read(self):
        self.is_read = True
        self.save()

    class Meta:
        ordering = ['-creation_date']