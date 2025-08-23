from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from .models import Issue
from projects.models import Contributor

_STATUS_ALLOWED = {"TODO", "IN_PROGRESS", "DONE"}
_STATUS_ALIASES = {"to do": "TODO", "in progress": "IN_PROGRESS", "finished": "DONE", "done": "DONE"}

class IssueSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.id")

    class Meta:
        model = Issue
        fields = ["id", "name", "description", "project", "author", "assignee",
                  "priority", "tag", "status", "created_time"]
        read_only_fields = ["id", "author", "created_time"]

    def _normalize_status(self, val):
        if val in _STATUS_ALLOWED:
            return val
        key = str(val).lower().replace("_", " ").strip()
        return _STATUS_ALIASES.get(key)

    def validate(self, attrs):
        request = self.context.get("request")
        project = attrs.get("project") or getattr(self.instance, "project", None)
        assignee = attrs.get("assignee")

        if request and request.user and project:
            if not Contributor.objects.filter(project=project, user=request.user).exists():
                raise PermissionDenied("Vous devez être contributeur du projet.")

        if assignee and project and not Contributor.objects.filter(project=project, user=assignee).exists():
            raise serializers.ValidationError({"assignee": "L'assigné doit être contributeur du projet."})

        status_val = attrs.get("status")
        if status_val is not None:
            norm = self._normalize_status(status_val)
            if norm is None:
                raise serializers.ValidationError({"status": "Utilise TODO / IN_PROGRESS / DONE."})
            attrs["status"] = norm
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault("author", request.user)
        return super().create(validated_data)
