from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from airport.permissions import IsAdminOrIfAuthenticatedReadOnly


class TestIsAdminOrIfAuthenticatedReadOnly(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            password="password123e"
        )
        self.permission = IsAdminOrIfAuthenticatedReadOnly()

    def test_anonymous_user(self):
        request = self.factory.get('/bad/')
        request.user = AnonymousUser()

        self.assertFalse(self.permission.has_permission(request, view=None))

    def test_user_authenticated_safe_method(self):
        self.client.force_authenticate(self.user)
        request = self.factory.get('/good/')
        request.user = self.user

        self.assertTrue(self.permission.has_permission(request, view=None))

    def test_user_authenticated_unsafe_method(self):
        self.client.force_authenticate(self.user)

        request = self.factory.post('/bad/')
        request.user = self.user

        self.assertFalse(self.permission.has_permission(request, view=None))

    def test_user_admin_authenticated_unsafe_method(self):
        admin = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            password="password123e"
        )
        self.client.force_authenticate(admin)
        request = self.factory.post('/good/')
        request.user = admin

        self.assertTrue(self.permission.has_permission(request, view=None))
