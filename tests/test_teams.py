from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from org.models import Team, Repository,Organization


class TeamViewTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.organization = Organization.objects.create(name='Test Organization')
        self.repository = Repository.objects.create(
            organization=self.organization,
            name='Test Repository'
        )
        self.team1 = Team.objects.create(repository=self.repository, name='Team 1', description='Description 1')
        self.team2 = Team.objects.create(repository=self.repository, name='Team 2', description='Description 2')

    def test_get_all_teams(self):
        url = reverse('team-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Team 1')
        self.assertEqual(response.data[1]['name'], 'Team 2')



class TeamAPIViewTestCase(APITestCase):

    def setUp(self):
        self.organization = Organization.objects.create(name='Test Organization')
        self.repository = Repository.objects.create(name='Test Repository', organization=self.organization)
        self.user = User.objects.create_user(username='testuser', password='password')
        self.superuser = User.objects.create_superuser(username='superuser', password='password')
        self.client.force_authenticate(user=self.superuser)
        self.team_data = {
            'repository': self.repository.id,
            'name': 'Test Team',
            'description': 'A test team description',
            'users': [self.user.id],
        }
        self.team = Team.objects.create(repository=self.repository, name='Existing Team', description='Existing description')
        self.team.users.set([self.user])

    def test_create_team(self):
        response = self.client.post(reverse('team-list-create'), self.team_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Test Team')

    def test_update_team(self):
        update_data = {
            'name': 'Updated Team',
            'description': 'Updated description'
        }
        response = self.client.put(reverse('team-detail', kwargs={'team_id': self.team.id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.name, 'Updated Team')
        self.assertEqual(self.team.description, 'Updated description')

    def test_delete_team(self):
        response = self.client.delete(reverse('team-detail', kwargs={'team_id': self.team.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.count(), 0)

    def test_create_team_invalid_data(self):
        invalid_data = {
            'repository': '',
            'name': '',
            'description': 'Invalid data test'
        }
        response = self.client.post(reverse('team-list-create'), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_team_invalid_data(self):
        invalid_data = {
            'name': ''
        }
        response = self.client.put(reverse('team-detail', kwargs={'team_id': self.team.id}), invalid_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
