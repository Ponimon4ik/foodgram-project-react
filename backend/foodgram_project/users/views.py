from rest_framework import (status, permissions, mixins,
                            viewsets, pagination, )
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import User, Follow
from .serializers import (CustomUserSerializer, CustomUserCreateSerializer,
                          )
from api.serializers import FollowReadSerializer, FollowSerializer


class ListCreateRetrieveViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    pass


class UserViewSet(ListCreateRetrieveViewSet):

    queryset = User.objects.all().order_by('id')
    pagination_class = pagination.LimitOffsetPagination

    def get_permissions(self):
        if self.action in ['me', 'set_password', 'retrieve']:
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'list']:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        elif self.request.method == 'POST':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(detail=False,)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(['post'], detail=False,)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['get'], detail=False,
    )
    def subscriptions(self, request):
        follows = request.user.follower.select_related('following')
        authors_id = []
        for e in follows:
            authors_id.append(e.following.id)
        queryset = User.objects.filter(pk__in=authors_id).annotate(
            recipes_count=Count('recipes'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowReadSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowReadSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        ['post', 'delete'],
        detail=True,
        url_path='subscribe',
    )
    def create_or_delete_subscription(self, request, pk=None):
        data = {
            'user': request.user,
            'following': pk
        }
        if request.method == 'DELETE':
            get_object_or_404(User, pk=pk)
            if Follow.objects.filter(**data).exists():
                subscription = get_object_or_404(Follow, **data)
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы не были подписаны на данного автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(User, pk=pk)
        serializer = FollowSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
