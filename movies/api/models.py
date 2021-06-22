from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Movie(models.Model):
    title = models.CharField(max_length=255)
    tagline = models.TextField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    release_date = models.DateField()
    homepage = models.URLField(null=True, blank=True)
    imdb_id = models.CharField(max_length=24, null=True, blank=True)
    adult = models.BooleanField()
    budget = models.IntegerField(null=True)
    genres = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liked_movies = models.ManyToManyField(Movie, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
