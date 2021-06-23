import json

from django.contrib.auth.models import User
from django.urls import reverse
from movies.api.models import Movie
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APITransactionTestCase


class RegisterTestCase(APITestCase):

    register_url = reverse("register")

    def test_register(self):
        data = {"username": "testcase", "password": "12345"}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginTestCase(APITestCase):

    login_url = reverse("login")

    def setUp(self):
        self.username = "testlogin"
        self.password = "password"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_correct(self):

        data = {"username": self.username, "password": self.password}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_username(self):
        data = {"username": "nonexistentuser", "password": self.password}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_password(self):
        data = {"username": self.username, "password": "wrongpassword"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_payload(self):
        response = self.client.post(self.login_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTestCase(APITestCase):

    logout_url = reverse("logout")

    def setUp(self):
        self.user = User.objects.create_user(username="testlogout", password="password")
        self.token = Token.objects.create(user=self.user)

    def test_logout_correct(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token "+self.token.key)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token "+"someinvalidtoken")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_no_token(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MovieViewSetTestCase(APITransactionTestCase):

    reset_sequences = True

    def setUp(self):
        for i in range(7):
            Movie.objects.create(title="Movie "+str(i), adult=False)

    def test_movie_list(self):
        list_url = reverse("movie-list")
        response = self.client.get(list_url)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json['results']), 7)

    def test_movie_detail_correct(self):
        tested_id = 3
        detail_url = reverse("movie-detail", kwargs={"pk": tested_id})
        response = self.client.get(detail_url)
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json['id'], tested_id)

    def test_movie_detail_non_existent(self):
        tested_id = 9999
        detail_url = reverse("movie-detail", kwargs={"pk": tested_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_movie_detail_invalid_id(self):
        tested_id = "alphabetic"
        detail_url = reverse("movie-detail", kwargs={"pk": tested_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FavoriteMoviesListTestCase(APITestCase):

    list_url = reverse("favorites-list")

    def setUp(self):
        self.user = User.objects.create_user(username="testusername", password="somepassword")
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token "+self.token.key)

    def test_favorites_list_authenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_favorites_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FavoriteMoviesAddTestCase(APITransactionTestCase):

    reset_sequences = True
    list_url = reverse("favorites-list")

    def setUp(self):
        for i in range(7):
            Movie.objects.create(title="Movie "+str(i), adult=False)
        self.user = User.objects.create_user(username="testusername", password="somepassword")
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token "+self.token.key)

    def test_favorites_add_authenticated(self):
        # favorites list should be empty
        response = self.client.get(self.list_url)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json), 0)
        # add to favorites
        tested_id = 3
        detail_url = reverse("favorites-detail", kwargs={"pk": tested_id})
        response = self.client.patch(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # favorites list should not be empty
        response = self.client.get(self.list_url)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json), 1)

    def test_favorites_add_unauthenticated(self):
        self.client.force_authenticate(user=None)
        tested_id = 3
        detail_url = reverse("favorites-detail", kwargs={"pk": tested_id})
        response = self.client.patch(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_favorites_remove_authenticated(self):
        tested_id = 3
        # add to favorites
        detail_url = reverse("favorites-detail", kwargs={"pk": tested_id})
        response = self.client.patch(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # favorites list should not be empty
        response = self.client.get(self.list_url)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json), 1)
        # delete from favorites
        detail_url = reverse("favorites-detail", kwargs={"pk": tested_id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # favorites list should be empty
        response = self.client.get(self.list_url)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json), 0)

    def test_favorites_remove_unauthenticated(self):
        self.client.force_authenticate(user=None)
        tested_id = 3
        detail_url = reverse("favorites-detail", kwargs={"pk": tested_id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
