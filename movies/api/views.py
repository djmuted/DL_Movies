from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Movie, Profile
from .serializers import MovieSerializer, ProfileSerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    # GET /api/movies
    # lists all movies


class ProfileViewSet(LoginRequiredMixin, viewsets.GenericViewSet):
    serializer_class = ProfileSerializer

    def list(self, request, *args, **kwargs):
        instance = Profile.objects.get(user=request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FavoriteMoviesViewSet(LoginRequiredMixin, viewsets.GenericViewSet):
    queryset = Movie.objects.all()
    serializer_class = serializers.Serializer

    # GET /api/favorites/
    # lists user's favorite movies
    def list(self, request, *args, **kwargs):
        instance = Profile.objects.get(
            user=self.request.user).liked_movies.all()
        serializer = MovieSerializer(
            instance, many=True, context={'request': request})
        return Response(serializer.data)

    # PATCH /api/favorites/:id
    # adds a movie to favorites
    def partial_update(self, request, pk=None):
        if not Movie.objects.filter(pk=pk).exists():
            raise NotFound(detail="Movie does not exist", code=404)

        profile = Profile.objects.get(user=request.user)
        profile.liked_movies.add(pk)
        profile.save()
        return Response()  # 200 OK

    # DELETE /api/favorites/:id
    # removes a movie from favorites
    def destroy(self, request, pk=None):
        profile = Profile.objects.get(user=request.user)
        profile.liked_movies.remove(pk)
        profile.save()
        return Response()  # 200 OK
