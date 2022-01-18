from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='user')


urlpatterns = [
    path('v1/', include('users.urls')),
    path('v1/', include(router_v1.urls))
]
