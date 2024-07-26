from rest_framework import serializers
from django.contrib.auth.models import User, Permission
from .models import Repository,Team
from django.contrib.contenttypes.models import ContentType
from .models import Organization

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
class OrganizationSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ('id', 'name', 'description', 'created_at', 'users')

    def update(self, instance, validated_data):
        users = validated_data.pop('users', [])
        instance = super().update(instance, validated_data)
        instance.users.set(users)
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Set the user as a staff member
        user.is_staff = True
        user.save()

        # Define permissions mapping
        permissions = {
            'org.organization': [
                'view_organization',
            ],
            'org.user': [
                'view_user',
            ],
            'org.repository': [
                'view_repository',
                'add_repository',
                'delete_repository',
                'change_repository',
            ],


        }

        for model_name, perms in permissions.items():
            try:
                app_label, model_name = model_name.split('.')
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                for perm_name in perms:
                    try:
                        permission = Permission.objects.get(codename=perm_name, content_type=content_type)
                        user.user_permissions.add(permission)
                    except Permission.DoesNotExist:
                        # Handle the case where the permission does not exist
                        print(f"Permission '{perm_name}' for model '{model_name}' does not exist")
            except ContentType.DoesNotExist:
                # Handle the case where the content type does not exist
                print(f"Content type for model '{model_name}' does not exist")

        # Save the user with the assigned permissions
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class TeamSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = '__all__'

class RepositorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Repository
        fields = '__all__'





class TeamUpdateSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'repository', 'users']
