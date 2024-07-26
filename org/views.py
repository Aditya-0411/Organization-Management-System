# views.py

from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Organization , Repository , Team
from .serializers import OrganizationSerializer ,RegisterSerializer, LoginSerializer, UserSerializer ,RepositorySerializer ,TeamSerializer,TeamUpdateSerializer
from rest_framework import generics
from django.contrib.auth.models import User,Permission
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from .permissions import IsSuperUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken



#USER REGISTRATION
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#USER LOGIN
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Retrieve username and password from the validated data
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')

            # Authenticate the user
            user = authenticate(username=username, password=password)

            if user:
                # Login the user
                login(request, user)

                # Generate tokens
                refresh = RefreshToken.for_user(user)

                # Return the response
                return Response({
                    "status": "success",
                    "data": {
                        "user": UserSerializer(user).data,
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh)
                    }
                }, status=status.HTTP_200_OK)

            # If authentication fails
            return Response({"status": "error", "data": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            # If serializer validation fails
        return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


#SEE ALL USERS
class UserListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



#CRUD FOR ORGANIZATION
class OrganizationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        if pk:
            # Retrieve a single organization
            try:
                organization = Organization.objects.get(pk=pk)
            except Organization.DoesNotExist:
                return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = OrganizationSerializer(organization)
            return Response(serializer.data)
        else:
            # List all organizations
            organizations = Organization.objects.all()
            serializer = OrganizationSerializer(organizations, many=True)
            return Response(serializer.data)

class OrganizationAPIView(APIView):
    permission_classes = [IsSuperUser]
    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        organization = get_object_or_404(Organization, pk=pk)
        serializer = OrganizationSerializer(organization, data=request.data, partial=True)
        if serializer.is_valid():
            organization = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({'error': 'Organization ID is required for deletion'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



#ADD USERS TO ORGANIZATION
class AddUserToOrganizationAPIView(APIView):
    permission_classes = [IsSuperUser]
    def post(self, request, pk):
        organization = get_object_or_404(Organization, pk=pk)
        user_ids = request.data.get('user_ids', [])
        users = User.objects.filter(id__in=user_ids)

        if not users.exists():
            return Response({'error': 'One or more users do not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        organization.users.add(*users)
        return Response({'status': 'Users added successfully'}, status=status.HTTP_200_OK)


#CRUD IN REPO
class RepositoryAPIView(APIView):
    def get(self, request, org_pk, repo_pk=None):
        organization = get_object_or_404(Organization, pk=org_pk)
        if repo_pk:
            repository = get_object_or_404(Repository, pk=repo_pk, organization=organization)
            serializer = RepositorySerializer(repository)
            return Response(serializer.data)
        else:
            repositories = Repository.objects.filter(organization=organization)
            serializer = RepositorySerializer(repositories, many=True)
            return Response(serializer.data)

    def post(self, request, org_pk):
        organization = get_object_or_404(Organization, pk=org_pk)
        serializer = RepositorySerializer(data=request.data)
        if serializer.is_valid():
            repository = serializer.save(organization=organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, org_pk, repo_pk):
        organization = get_object_or_404(Organization, pk=org_pk)
        repository = get_object_or_404(Repository, pk=repo_pk, organization=organization)
        serializer = RepositorySerializer(repository, data=request.data, partial=True)
        if serializer.is_valid():
            repository = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, org_pk, repo_pk):
        organization = get_object_or_404(Organization, pk=org_pk)
        repository = get_object_or_404(Repository, pk=repo_pk, organization=organization)
        repository.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#TEAM CREATION
class TeamView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, team_id=None):
        if team_id:
            team = get_object_or_404(Team, id=team_id)
            serializer = TeamSerializer(team)
        else:
            teams = Team.objects.all()
            serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

class TeamAPIView(APIView):
    permission_classes = [IsSuperUser]
    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)
        serializer = TeamSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#TO ASSIGN USERS TO TEAM
class AssignUsersToTeamView(APIView):
    permission_classes = [IsSuperUser]
    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)
        user_ids = request.data.get('user_ids', [])

        if not user_ids:
            return Response({'error': 'User IDs not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(id__in=user_ids)

        if not users.exists():
            return Response({'error': 'One or more users do not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Debugging information
        existing_user_ids = users.values_list('id', flat=True)
        missing_user_ids = set(user_ids) - set(existing_user_ids)

        if missing_user_ids:
            return Response({'error': f'User IDs not found: {list(missing_user_ids)}'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Add users to the team
        for user in users:
            team.users.add(user)

        team.save()

        return Response({'status': 'users added'}, status=status.HTTP_200_OK)