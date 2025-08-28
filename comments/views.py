from rest_framework import viewsets, permissions
from .models import Comment
from .serializers import CommentSerializer
from core.permissions import IsAuthorOrReadOnlyWithinProject

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnlyWithinProject]
    pagination_class = None

    def get_queryset(self):
        return (
            Comment.objects.select_related("issue", "author", "issue__project")
            .filter(issue__project__contributors__user=self.request.user)
            .distinct()
            .order_by("-created_time")
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
