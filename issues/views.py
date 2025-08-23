from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Issue
from .serializers import IssueSerializer
from core.permissions import IsProjectMemberOrReadOnly


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
    return None  # laisse DRF gérer si valeur non mappée


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]

    def get_queryset(self):
        base_qs = (
            Issue.objects.select_related("project", "author", "assignee")
            .distinct()
            .order_by("-created_time")
        )
        # 👉 Pour les actions DÉTAIL (retrieve/update/partial_update/destroy),
        # on NE filtre PAS par contributeur : l'objet est trouvé,
        # puis la permission objet renverra 403 si nécessaire.
        action = getattr(self, "action", None)
        if action in ("retrieve", "update", "partial_update", "destroy") or self.kwargs.get("pk"):
            return base_qs

        # Pour les LISTES, on filtre par contributeur du projet
        return base_qs.filter(project__contributors__user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        # Normaliser 'status' AVANT la validation (sinon ChoiceField bloque)
        if "status" in data:
            norm = _normalize_status(data.get("status"))
            if norm:
                data["status"] = norm

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
