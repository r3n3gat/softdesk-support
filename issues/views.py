from django.db.models import Exists, OuterRef
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import Issue
from .serializers import IssueSerializer
from core.permissions import IsAuthorOrReadOnlyWithinProject
from projects.models import Contributor


def _normalize_status(raw: str) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip().lower().replace("_", " ")
    if s in {"to do", "todo"}:
        return "TODO"
    if s in {"in progress", "doing", "en cours"}:
        return "IN_PROGRESS"
    if s in {"done", "finished", "terminé", "termine", "fini"}:
        return "DONE"
    return None


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnlyWithinProject]

    def get_queryset(self):
        # Base queryset : toutes les issues, pour que la permission objet puisse s'appliquer
        base = (
            Issue.objects.select_related("project", "author", "assignee")
            .order_by("-created_time")
        )

        # Est-ce que l'utilisateur est contributeur du projet ?
        contrib_qs = Contributor.objects.filter(
            project=OuterRef("project"), user=self.request.user
        )

        # En lecture (SAFE) ou action list -> on restreint aux projets dont l'utilisateur est contributeur
        is_safe = self.request.method in permissions.SAFE_METHODS
        is_list_action = getattr(self, "action", None) == "list"
        if is_safe or is_list_action:
            return base.annotate(_is_contrib=Exists(contrib_qs)).filter(_is_contrib=True)

        # En écriture (PATCH/PUT/DELETE),  retourne le base queryset pour éviter un 404
        # la permission objet = 403 si l'utilisateur n'est pas l'auteur
        return base

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if "status" in data:
            norm = _normalize_status(data.get("status"))
            if norm:
                data["status"] = norm
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
