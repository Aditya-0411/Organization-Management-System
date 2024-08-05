
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from org.models import Organization, Repository
from django.contrib.auth.models import User

class OrganizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.create_url = reverse('organization-create')
        self.update_delete_url = lambda pk: reverse('organization-detail', args=[pk])

        # Create a superuser
        self.user = User.objects.create_superuser(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)  # Authenticate the client

        # Create an organization to use for update and delete tests
        self.organization = Organization.objects.create(
            name='Initial Organization',
            description='Initial description.'
        )

    def test_create_organization(self):
        data = {
            'name': 'Test Organization',
            'description': 'This is a test organization.',
        }
        response = self.client.post(self.create_url, data, format='json')

        # Print response content for debugging
        print(response.content)

        # Check that the response status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the organization was created in the database
        organization = Organization.objects.get(name='Test Organization')
        self.assertEqual(organization.description, 'This is a test organization.')

    def test_update_organization(self):
        data = {
            'name': 'Updated Organization',
            'description': 'Updated description.',
        }
        response = self.client.put(self.update_delete_url(self.organization.pk), data, format='json')

        # Print response content for debugging
        print(response.content)

        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the organization was updated in the database
        organization = Organization.objects.get(pk=self.organization.pk)
        self.assertEqual(organization.name, 'Updated Organization')
        self.assertEqual(organization.description, 'Updated description.')

    def test_delete_organization(self):
        response = self.client.delete(self.update_delete_url(self.organization.pk))

        # Print response content for debugging
        print(response.content)

        # Check that the response status code is 204 No Content
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the organization was deleted from the database
        with self.assertRaises(Organization.DoesNotExist):
            Organization.objects.get(pk=self.organization.pk)


