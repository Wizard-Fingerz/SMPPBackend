from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static
from .views import *

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'user-profiles', UserProfileViewSet)
# router.register(r'business-categories', BusinessCategoryViewSet)
# router.register(r'password-change', PasswordChangeViewSet,
                # basename='password-change')



urlpatterns = [
    path('api/', include(router.urls)),

    #     Authentication urls
    path('register/', create_user, name='user_register'),
    path('login/', login_view, name='api_token'),
    path('logout/', logout_view, name='api_token'),
    path('', UserAPIView.as_view(), name='user_detail'),
    path('profile/update-status/', UserProfileHasUpdatedProfileView.as_view(), name='user-profile-update-status'),
    path('update-profile/', update_user_profile, name='update_user_profile'),
    path('user-profile/update/', UserProfileViewSet.as_view({'put': 'update'}), name='user-profile-update'),
    path('search-user/', UserSearchAPIView.as_view(), name='search_user'),
    path('delete-account/', delete_account, name='delete_account'),
    path('delete-user/<str:username>/', delete_account_by_username,
         name='delete_account_by_username'),
    path('delete-user-by-id/<int:user_id>/',
         delete_account_by_id, name='delete_account_by_id'),
    path('delete-user-by-username-or-id/', delete_user_by_username_or_id,
         name='delete_user_by_username_or_id'),
    path('block/', block_user, name='block-user'),
    path('blocked-users/', list_blocked_users, name='list-blocked-users'),
    path('users/', UserListView.as_view(), name='list-users'),
    path('user-details/', UserDetailsView.as_view(), name='user-details'),


]