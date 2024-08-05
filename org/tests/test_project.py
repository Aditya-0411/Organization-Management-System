from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from org.models import Repository, Organization, Team, Project
from django.test import TestCase

class ProjectAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user.save()

        # Generate token for the user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create an organization instance
        self.organization = Organization.objects.create(name='Test Organization', description='Test Description')

        # Create a repository instance and associate it with the created organization
        self.repository = Repository.objects.create(
            name='Test Repository',
            description='Test Repository Description',
            organization=self.organization
        )

        # Create a team instance and associate it with the created repository
        self.team = Team.objects.create(name='Test Team', description='Test Team Description', repository=self.repository)

        # Add the user to the team
        self.team.users.set([self.user])
        self.team.save()

        # Create a project instance
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Project Description',
            repository=self.repository,
            team=self.team
        )
        self.project.users.set([self.user])
        self.project.save()

    def test_create_project(self):
        data = {
            'name': 'New Project',
            'description': 'New Project Description',
            'repository': self.repository.id,
            'team': self.team.id,
            'users': [self.user.id]
        }
        response = self.client.post('/api/projects/', data, format='json')
        print(response.content)  # Print the response content for debugging
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'New Project')
        self.assertEqual(response.data['description'], 'New Project Description')
        self.assertEqual(response.data['repository'], self.repository.id)
        self.assertEqual(response.data['team'], self.team.id)
        self.assertEqual(response.data['users'], [self.user.id])

    def test_get_projects(self):
        response = self.client.get('/api/projects/')
        print(response.content)  # Print the response content for debugging
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Project')
        self.assertEqual(response.data[0]['description'], 'Test Project Description')
        self.assertEqual(response.data[0]['repository'], self.repository.id)
        self.assertEqual(response.data[0]['team'], self.team.id)
        self.assertEqual(response.data[0]['users'], [self.user.id])