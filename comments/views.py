from rest_framework import viewsets, permissions
from .models import Comment
from .serializers import CommentSerializer
from core.permissions import IsProjectMemberOrReadOnly

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    # Certains tests attendent une liste non paginée
    pagination_class = None

    def get_queryset(self):
        return (
            Comment.objects.select_related("issue", "author", "issue__project")
            .filter(issue__project__contributors__user=self.request.user)
            .distinct()
            .order_by("-created_time")
        )
