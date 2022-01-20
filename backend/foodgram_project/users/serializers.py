from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.validators import UniqueTogetherValidator

from .models import User, Follow

EMAIL_ERROR = "Пользователь с таким email уже существует"


class CustomUserCreateSerializer(UserCreateSerializer):

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email')
            )
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(EMAIL_ERROR)
        return value


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', )


# class FollowReadSerializer(serializers.ModelSerializer):

#     class Meta:
#         fields = ('')
#         model = Follow


# class FollowSerializer(serializers.ModelSerializer):
#     # Попробовать со скрытым полем
#     user = serializers.SlugRelatedField(
#         read_only=True, slug_field='username',
#         default=serializers.CurrentUserDefault()
#     )
#     following = serializers.SlugRelatedField(
#         queryset=User.objects.all(), slug_field='username')

#     class Meta:
#         fields = ('user', 'following')
#         model = Follow
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=['user', 'following']
#             )
#         ]

#     def validate_following(self, value):
#         if value == self.context['request'].user:
#             raise serializers.ValidationError(ERROR_MESSAGE)
#         return value