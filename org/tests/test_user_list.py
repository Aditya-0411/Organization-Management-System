
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User


class UserListTests(APITestCase):
    def setUp(self):
        # Create some users to test the list view
        self.user1 = User.objects.create_user(username='testuser1', password='password1')
        self.user2 = User.objects.create_user(username='testuser2', password='password2')
        self.url = reverse('user-list')  # Ensure this matches your URL pattern name

    def test_user_list_success(self):
        # Authenticate if needed, in this case it's AllowAny so it's not required
        # self.client.login(username='testuser1', password='password1')

        response = self.client.get(self.url)

        # Check that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response data contains the users
        response_data = response.json()
        self.assertEqual(len(response_data), 2)  # Check that the response contains 2 users
        self.assertIn('testuser1', [user['username'] for user in response_data])
        self.assertIn('testuser2', [user['username'] for user in response_data])

    def test_user_list_no_users(self):
        # Delete all users to test an empty list scenario
        User.objects.all().delete()

        response = self.client.get(self.url)

        # Check that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response data is an empty list
        response_data = response.json()
        self.assertEqual(response_data, [])
