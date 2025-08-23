# comments/serializers.py

from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'description', 'issue', 'author', 'created_time']
        read_only_fields = ['id', 'author', 'created_time']

    def create(self, validated_data):
        """
        Assigne automatiquement l'auteur au user connecté.
        """
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('author', request.user)
        return super().create(validated_data)
