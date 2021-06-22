from rest_framework import serializers
from .models import Movie, Profile


class MovieSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    liked_movies = MovieSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['liked_movies']
