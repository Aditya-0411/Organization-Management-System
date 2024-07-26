from django.contrib import admin
from django.contrib.auth.models import User
from org.models import Organization , Repository,Team

class RepositoryInline(admin.TabularInline):
    model = Repository
    extra = 1
# Register your models here.
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',"description","created_at")
    search_fields = ('name',"description","created_at")
    list_filter = ('name',"description",'created_at')

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'created_at')
    list_filter = ('organization',)



admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Repository, RepositoryAdmin)

class TeamInline(admin.TabularInline):
    model = Team
    extra = 1

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'repository', 'created_at')
    list_filter = ('repository',)
class UserAdmin(admin.ModelAdmin):
    model = User
    filter_horizontal = ('user_permissions', 'groups')
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
