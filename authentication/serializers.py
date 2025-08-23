from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(required=False, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "age", "can_be_contacted", "can_data_be_shared", "created_time",
            "date_joined", "is_active"
        ]
        read_only_fields = ["id", "created_time", "date_joined", "is_active"]

class SignupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # ← pour que la réponse de signup contienne 'id'
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=False)  # ← optionnel
    email = serializers.EmailField(required=False, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password", "password_confirm",
            "age", "can_be_contacted", "can_data_be_shared", "first_name", "last_name"
        ]

    def validate(self, attrs):
        pwd = attrs.get("password")
        pwdc = attrs.get("password_confirm")
        # On ne vérifie la confirmation que si fournie
        if pwdc is not None and pwd != pwdc:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        age = attrs.get("age")
        if age is not None and age < 15:
            raise serializers.ValidationError({"age": "L'utilisateur doit avoir au moins 15 ans."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user
