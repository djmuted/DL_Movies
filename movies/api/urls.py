from rest_framework import routers
from django.urls import include, path

from .views import MovieViewSet, ProfileViewSet, FavoriteMoviesViewSet

router = routers.DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'favorites', FavoriteMoviesViewSet, basename='favorites')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
