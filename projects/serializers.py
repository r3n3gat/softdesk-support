from rest_framework import serializers
from .models import Project, Contributor

class ProjectSerializer(serializers.ModelSerializer):
    # Expose uniquement l'id de l'auteur
    author = serializers.ReadOnlyField(source="author.id")
    # 'title' sert d'alias d'entrée pour 'name'
    title = serializers.CharField(write_only=True, required=False)
    # Laisse 'type' libre côté API ; la normalisation est faite dans la vue
    type = serializers.CharField(required=False, allow_blank=True, max_length=50)

    class Meta:
        model = Project
        fields = ["id", "name", "title", "description", "type", "author", "created_time"]
        read_only_fields = ["id", "author", "created_time"]
        extra_kwargs = {
            # autorise PATCH partiel sans exiger ces champs
            "name": {"required": False},
            "description": {"required": False},
            "type": {"required": False},
        }

    def validate(self, attrs):
        # Si 'name' absent mais 'title' fourni : mappe vers 'name'
        if not attrs.get("name"):
            title_from_input = getattr(self, "initial_data", {}).get("title")
            if title_from_input:
                attrs["name"] = title_from_input
        return attrs

    def create(self, validated_data):
        # IMPORTANT : ne jamais passer 'title' au modèle
        validated_data.pop("title", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Même logique en update
        validated_data.pop("title", None)
        return super().update(instance, validated_data)


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ["id", "user", "project", "role", "created_time"]
        read_only_fields = ["id", "created_time"]
