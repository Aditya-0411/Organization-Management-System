from django.db import models
from django.contrib.auth.models import User


# Create your models here.

#MODEL FOR ORGANIZATION
class Organization(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    users = models.ManyToManyField(User, related_name="organizations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def total_members(self):
        return self.users.count()



    def __str__(self):
        return self.name

#MODEL FOR REPO
class Repository(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    organization = models.ForeignKey(Organization, related_name='repositories', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

class Team(models.Model):
    repository = models.ForeignKey(Repository, related_name='teams', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    users = models.ManyToManyField(User, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)