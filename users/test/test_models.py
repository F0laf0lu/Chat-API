from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import CustomUser

class CustomUserManagerTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username='testuser1', password='password123')

        self.assertEqual(user.username, 'testuser1')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(username='adminuser', password='adminpassword')

        self.assertEqual(admin_user.username, 'adminuser')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_create_user_missing_username(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', password='password123')

    def test_create_superuser_not_staff(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_superuser(username='adminuser', password='superpassword', is_staff=False)

    def test_create_superuser_not_superuser(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_superuser(username='adminuser', password='superpassword', is_superuser=False)

class CustomUserModelTests(TestCase):
    def test_user_str_method(self):
        user = CustomUser(username='testuser')
        self.assertEqual(str(user), 'testuser')

    def test_user_username_is_unique(self):
            user1 = CustomUser.objects.create_user(username='testuser', password='password123')

            with self.assertRaises(IntegrityError):
                user2 = CustomUser.objects.create_user(username='testuser', password='password123')