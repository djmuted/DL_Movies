from datetime import datetime

from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Movie, Profile
from .serializers import MovieSerializer, ProfileSerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MovieSerializer

    """
    GET /api/movies
    lists all movies
    """

    def get_queryset(self):
        queryset = Movie.objects.all()

        # filter by year
        year = self.request.query_params.get('year')
        if year is not None:
            if year.isdigit() and int(year) > 1800 and int(year) <= datetime.now().year + 10:  # year validation
                queryset = queryset.filter(release_date__range=[year+"-01-01", year+"-12-31"])
            else:
                raise ParseError(detail="Invalid year format")

        # filter by title
        title = self.request.query_params.get('title')
        if title is not None:
            queryset = queryset.filter(title__icontains=title)

        return queryset


class ProfileViewSet(LoginRequiredMixin, viewsets.GenericViewSet):
    serializer_class = ProfileSerializer

    def list(self, request, *args, **kwargs):
        instance = Profile.objects.get(user=request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FavoriteMoviesViewSet(LoginRequiredMixin, viewsets.GenericViewSet):
    queryset = Movie.objects.all()
    serializer_class = serializers.Serializer

    """
    GET /api/favorites/
    lists user's favorite movies
    """

    def list(self, request, *args, **kwargs):
        instance = Profile.objects.get(
            user=self.request.user).liked_movies.all()
        serializer = MovieSerializer(instance, many=True, context={'request': request})
        return Response(serializer.data)

    """
    PATCH /api/favorites/:id
    adds a movie to favorites
    """

    def partial_update(self, request, pk=None):
        if not Movie.objects.filter(pk=pk).exists():
            raise NotFound(detail="Movie does not exist", code=404)

        profile = Profile.objects.get(user=request.user)
        profile.liked_movies.add(pk)
        profile.save()
        return Response()  # 200 OK

    """
    DELETE /api/favorites/:id
    removes a movie from favorites
    """

    def destroy(self, request, pk=None):
        profile = Profile.objects.get(user=request.user)
        profile.liked_movies.remove(pk)
        profile.save()
        return Response()  # 200 OK
