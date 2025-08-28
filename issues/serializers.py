from rest_framework import serializers
from .models import Issue
from projects.models import Contributor

class IssueSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id", "project", "name", "description",
            "priority", "tag", "status",
            "assignee", "author", "created_time"
        ]
        read_only_fields = ["id", "author", "created_time"]
        extra_kwargs = {
            # en création project est requis; en update partiel, DRF gère avec PATCH
            "assignee": {"required": False, "allow_null": True},
            "description": {"required": False},
            "name": {"required": False},
            "priority": {"required": False},
            "tag": {"required": False},
            "status": {"required": False},
        }

    def validate(self, attrs):
        project = attrs.get("project") or getattr(self.instance, "project", None)
        assignee = attrs.get("assignee", getattr(self.instance, "assignee", None))
        if assignee:
            # l'assigné doit être contributeur du même projet
            is_contrib = Contributor.objects.filter(project=project, user=assignee).exists()
            if not is_contrib:
                raise serializers.ValidationError({"assignee": "Assignee must be a project contributor."})
        return attrs

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("author", None)
        return super().update(instance, validated_data)
