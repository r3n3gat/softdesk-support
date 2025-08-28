from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.id")
    class Meta:
        model = Comment
        fields = ["id", "description", "issue", "author", "created_time"]
        read_only_fields = ["id", "author", "created_time"]
    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


    def update(self, instance, validated_data):
        validated_data.pop("author", None)
        return super().update(instance, validated_data)
