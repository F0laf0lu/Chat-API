from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import force_authenticate
from rest_framework.test import APITestCase
from users.serializers import RegisterSerializer
from users.views import RegisterView


class UserViewSetTest(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(username='adminuser', password='adminuser')
        self.user = get_user_model().objects.create_user(username='testuser', password='user')

    def test_get_all_users(self):
        '''
        Only Admin user can view all the users
        '''
        url = reverse('user-list')
        self.client.force_authenticate(self.admin)
        response1 = self.client.get(url)

        self.client.force_authenticate(self.user)
        response2 = self.client.get(url)

        self.assertEqual(url, '/api/v1/users/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_details(self):
        '''
        only Authenticated users can retrieve a user details
        '''
        url = reverse('user-detail', kwargs={'pk':self.user.pk})
        self.assertEqual(url, f'/api/v1/users/{self.user.pk}/')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response1 = self.client.get(url)
        self.assertEqual(f'{self.user.username}', response1.data['username'])
        self.assertEqual(response1.status_code, status.HTTP_200_OK)


    def test_update_user_detail(self):
        url = reverse('user-detail', kwargs={'pk':self.user.pk})
        data  = {
            'first_name':'test',
            'last_name':'user'
        }
        anon_user_response = self.client.patch(url)
        self.assertEqual(anon_user_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.admin)
        wrong_owner_response = self.client.patch(url)
        self.assertEqual(wrong_owner_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.user)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RegisterUserTests(APITestCase):
    url = reverse('user-list')

    def test_correct_register_url(self):
        self.assertEqual(self.url, '/api/v1/users/')

    def test_register_user_and_correct_serializer_used(self):
        data = {
            'username':'testuser',
            'password':'12345678',
            'first_name':'test',
            'last_name':'user'
        }
        response = self.client.post(self.url, data, format='json')
        view = resolve(self.url).func.cls()
        view.action = 'create'
        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, RegisterSerializer)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_wth_existing_username(self):
        get_user_model().objects.create_user(username='testuser', password='password123')
        data = {
            'username':'testuser',
            'password':'12345678',
            'first_name':'test',
            'last_name':'user'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_username_or_password(self):
        data1 = {
            'password':'12345678'
        }
        data2 = {
            'username':'testuser'
        }
        response1 = self.client.post(self.url, data1, format='json')
        response2 = self.client.post(self.url, data2, format='json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)


class LoginView(APITestCase):
    def setUp(self):
        get_user_model().objects.create_user(username='testuser', password='12345678')

    def test_user_login(self):
        url = reverse('user-login')
        data = {
            'username':'testuser',
            'password': '12345678'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)