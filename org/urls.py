
from django.urls import path
from .views import OrganizationAPIView ,RegisterAPIView, LoginView,TeamView,AssignUsersToTeamView,TeamAPIView, UserListAPIView,AddUserToOrganizationAPIView, RepositoryAPIView,OrganizationView
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



urlpatterns = [
    #TOKEN AUTH
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #TO CREATE AND VIEW ORGANIZATIONS
    path('organizations/', OrganizationView.as_view(), name='organization-list'),
    path('orgcreate/', OrganizationAPIView.as_view(), name='organization-create'),
    path('organizations/<int:pk>/', OrganizationAPIView.as_view(), name='organization-detail'),

    #USER REGISTER AND LOGIN
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    #SEE USERS
    path('users/', UserListAPIView.as_view()),

    #TO ADD USERS TO ORG
    path('organizations/<int:pk>/add-users/', AddUserToOrganizationAPIView.as_view(), name='add-users-to-organization'),

    #CRUD in REPO
    path('organizations/<int:org_pk>/repositories/', RepositoryAPIView.as_view(), name='repository-list-create'),
    path('organizations/<int:org_pk>/repositories/<int:repo_pk>/', RepositoryAPIView.as_view(),
         name='repository-detail'),

    #TO ACCESS TEAM APIs
    path('teams/', TeamView.as_view(), name='team-list'),
    path('teams_create/', TeamAPIView.as_view(), name='team-list-create'),
    path('teams/<int:team_id>/', TeamAPIView.as_view(), name='team-detail'),
    path('teams/<int:team_id>/assign-users/', AssignUsersToTeamView.as_view(), name='assign-users-to-team'),]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

