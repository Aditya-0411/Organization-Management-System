from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from org.models import Organization, Repository
from org.serializers import RepositorySerializer


class RepositoryAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.organization = Organization.objects.create(name='Test Org', description='Test Org Description')

    def test_get_repositories(self):
        Repository.objects.create(name='Repo1', description='Repo1 Description', organization=self.organization)
        Repository.objects.create(name='Repo2', description='Repo2 Description', organization=self.organization)

        url = reverse('repository-list-create', kwargs={'org_pk': self.organization.pk})
        response = self.client.get(url)

        repositories = Repository.objects.filter(organization=self.organization)
        serializer = RepositorySerializer(repositories, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_repository(self):
        url = reverse('repository-list-create', kwargs={'org_pk': self.organization.pk})
        data = {
            'name': 'New Repo',
            'description': 'New Repo Description',
            'organization': self.organization.pk
        }

        response = self.client.post(url, data, format='json')
        print("Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Repository.objects.count(), 1)
        self.assertEqual(Repository.objects.get().name, 'New Repo')

    def test_get_single_repository(self):
        repository = Repository.objects.create(name='Repo1', description='Repo1 Description', organization=self.organization)

        url = reverse('repository-detail', kwargs={'org_pk': self.organization.pk, 'repo_pk': repository.pk})
        response = self.client.get(url)

        serializer = RepositorySerializer(repository)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_single_repository(self):
        repository = Repository.objects.create(name='Repo1', description='Repo1 Description',
                                               organization=self.organization)

        url = reverse('repository-detail', kwargs={'org_pk': self.organization.pk, 'repo_pk': repository.pk})
        data = {
            'name': 'Updated Repo',
            'description': 'Updated Repo Description'
        }

        response = self.client.put(url, data, format='json')

        repository.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(repository.name, 'Updated Repo')
        self.assertEqual(repository.description, 'Updated Repo Description')

    def test_delete_single_repository(self):
        repository = Repository.objects.create(name='Repo1', description='Repo1 Description',
                                               organization=self.organization)

        url = reverse('repository-detail', kwargs={'org_pk': self.organization.pk, 'repo_pk': repository.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Repository.objects.count(), 0)