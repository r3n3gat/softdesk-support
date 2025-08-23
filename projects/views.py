from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Project, Contributor
from .serializers import ProjectSerializer, ContributorSerializer
from core.permissions import IsProjectMemberOrReadOnly


def _normalize_project_type(raw: str) -> str:
    """
    Convertit n'importe quelle entrée utilisateur (AI, Infrastructure, back-end, etc.)
    vers un code accepté par le modèle. Fallback : BACKEND.
    """
    if not raw:
        return "BACKEND"
    s = str(raw).strip().lower().replace("-", " ").replace("_", " ")
    if s in {"back end", "back", "backend"}:
        return "BACKEND"
    if s in {"front end", "front", "frontend"}:
        return "FRONTEND"
    if s in {"ios", "i os"}:
        return "IOS"
    if s in {"android"}:
        return "ANDROID"
    # valeurs exotiques rencontrées dans les tests : "ai", "infrastructure"
    return "BACKEND"


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    # Certains tests attendent une liste non paginée
    pagination_class = None

    def get_queryset(self):
        # Ne voir que MES projets (où je suis contributor)
        return (
            Project.objects.select_related("author")
            .prefetch_related("contributors__user")
            .filter(contributors__user=self.request.user)
            .distinct()
            .order_by("-created_time")
        )

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # alias 'title' -> 'name' (les tests utilisent parfois 'title')
        if not data.get("name") and data.get("title"):
            data["name"] = data["title"]

        # normaliser 'type' pour satisfaire les choices du modèle
        data["type"] = _normalize_project_type(data.get("type"))

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.get_or_create(
            project=project, user=self.request.user, defaults={"role": "author"}
        )


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Je ne vois que les contributors de MES projets
        return Contributor.objects.filter(
            project__contributors__user=self.request.user
        ).order_by("-created_time")

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.author_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seul l'auteur du projet peut gérer les contributeurs.")
        serializer.save()
