from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from org.models import Team, Repository, Organization


class AssignUsersToTeamViewTestCase(APITestCase):

    def setUp(self):
        self.organization = Organization.objects.create(name='Test Organization')
        self.repository = Repository.objects.create(name='Test Repository', organization=self.organization)
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        self.superuser = User.objects.create_superuser(username='superuser', password='password')
        self.client.force_authenticate(user=self.superuser)
        self.team = Team.objects.create(repository=self.repository, name='Test Team',
                                        description='A test team description')

    def test_assign_users_to_team_success(self):
        url = reverse('assign-users-to-team', kwargs={'team_id': self.team.id})
        data = {'user_ids': [self.user1.id, self.user2.id]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user1, self.team.users.all())
        self.assertIn(self.user2, self.team.users.all())

    def test_assign_users_to_team_missing_user_ids(self):
        url = reverse('assign-users-to-team', kwargs={'team_id': self.team.id})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'User IDs not provided.')

    def test_assign_users_to_team_non_existing_users(self):
        non_existing_user_id = 9999
        url = reverse('assign-users-to-team', kwargs={'team_id': self.team.id})
        data = {'user_ids': [non_existing_user_id]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'One or more users do not exist.')

