from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from .models import User


class CustomUserSerializer(UserCreateSerializer):
   # password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')
