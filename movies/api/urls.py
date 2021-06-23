from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework import routers

from .views import FavoriteMoviesViewSet, MovieViewSet, UserCreate

router = routers.DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'favorites', FavoriteMoviesViewSet, basename='favorites')

urlpatterns = [
    # main API
    path('v1/', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/register/', UserCreate.as_view(), name="register"),
    # documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
