from rest_framework import status, permissions, mixins, viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404

from .models import User, Follow
from .serializers import (CustomUserSerializer, CustomUserCreateSerializer, 
                          FollowSerializer, )


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

    # @action(['get'], detail=False)
    # def subscriptions(self, request)
    #     serializer = FollowSerializer(request.user.follower, many = True)
    #     return Response(serializer.data)

    # @action(
    #     ['post', 'delete'],
    #     detail=True,
    #     url_name='subscriptions',
    #     #serializer_class=FollowSerializer  
    # )
    # def create_or_delete_subscription(self, request, pk=None)
    #     data = {
    #         'user': request.user,
    #         'following': pk
    #     }
    #     if request.method =='DELETE':
    #         subscription = get_object_or_404(Follow, **data)
    #         self.perform_destroy(subscription)
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     serializer = FollowSerializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=request.user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
        
