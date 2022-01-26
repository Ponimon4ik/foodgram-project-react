from rest_framework import (status, permissions, mixins,
                            viewsets, pagination, )
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.serializers import SetPasswordSerializer
from django.db.models import Count

from .models import User, Follow
from .serializers import (CustomUserSerializer, CustomUserCreateSerializer,
                          )
from api.serializers import FollowReadSerializer, FollowSerializer
from api.utils import managing_subscriptions


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
        return managing_subscriptions(request, pk, Follow, FollowSerializer)
