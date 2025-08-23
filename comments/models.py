import uuid
from django.db import models
from django.conf import settings
from issues.models import Issue


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_comments')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.issue.name} by {self.author.username}"