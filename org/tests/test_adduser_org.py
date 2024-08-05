from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from org.models import Organization
from django.contrib.auth.models import User
from org.views import AddUserToOrganizationAPIView

class AddUserToOrganizationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.superuser = User.objects.create_superuser(username='superuser', password='superpassword')
        self.organization = Organization.objects.create(name='Test Org', description='Test Org Description')
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.view = AddUserToOrganizationAPIView.as_view()

    def test_add_users_to_organization_success(self):
        request = self.factory.post(reverse('add-users-to-organization', kwargs={'pk': self.organization.pk}),
                                    {'user_ids': [self.user1.id, self.user2.id]}, format='json')
        force_authenticate(request, user=self.superuser)
        response = self.view(request, pk=self.organization.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.organization.users.count(), 2)

    def test_add_users_to_organization_invalid_user(self):
        invalid_user_id = 9999  # Assuming this user ID does not exist
        request = self.factory.post(reverse('add-users-to-organization', kwargs={'pk': self.organization.pk}),
                                    {'user_ids': [invalid_user_id]}, format='json')
        force_authenticate(request, user=self.superuser)
        response = self.view(request, pk=self.organization.pk)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(self.organization.users.count(), 0)

    def test_add_users_to_organization_not_superuser(self):
        request = self.factory.post(reverse('add-users-to-organization', kwargs={'pk': self.organization.pk}),
                                    {'user_ids': [self.user1.id, self.user2.id]}, format='json')
        force_authenticate(request, user=self.user1)  # Regular user, not superuser
        response = self.view(request, pk=self.organization.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.organization.users.count(), 0)