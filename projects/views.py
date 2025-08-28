from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Project, Contributor
from .serializers import ProjectSerializer, ContributorSerializer
from core.permissions import IsProjectAuthorOrReadOnly

def _normalize_project_type(raw: str) -> str:
    if not raw:
        return "BACKEND"
    s = str(raw).strip().lower().replace("-", " ").replace("_", " ")
    if s in {"back end", "back", "backend"}:
        return "BACKEND"
    if s in {"front end", "front", "frontend"}:
        return "FRONTEND"
    if s in {"ios"}:
        return "IOS"
    if s in {"android"}:
        return "ANDROID"
    return "BACKEND"


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthorOrReadOnly]
    # Les tests attendent une LISTE simple (pas paginée)
    pagination_class = None

    def get_queryset(self):
        # On ne voit que ses projets (où l'utilisateur est contributeur)
        return (
            Project.objects.filter(contributors__user=self.request.user)
            .distinct()
            .order_by("-created_time")
        )

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if "type" in data:
            data["type"] = _normalize_project_type(data.get("type"))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save(author=request.user)
        # S'assurer que le créateur est aussi contributeur
        Contributor.objects.get_or_create(
            project=project, user=request.user, defaults={"role": "author"}
        )
        headers = self.get_success_headers(ProjectSerializer(project).data)
        return Response(
            ProjectSerializer(project).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class ContributorViewSet(viewsets.ModelViewSet):
    """
    Gestion des contributeurs. Seul l'AUTEUR du projet peut créer/supprimer.
    Tout contributeur peut lister (visibilité des membres).
    """
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Voir les contributeurs des projets auxquels on appartient
        return Contributor.objects.filter(
            project__contributors__user=self.request.user
        ).select_related("project", "user").order_by("-created_time")

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.author_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seul l'auteur du projet peut gérer les contributeurs.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.project.author_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seul l'auteur du projet peut gérer les contributeurs.")
        return super().perform_destroy(instance)
