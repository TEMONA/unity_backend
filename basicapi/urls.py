from rest_framework.routers import DefaultRouter
from django.urls import path
from django.conf.urls import include
from .views import CreateUserView
from .views import UsersView, UserView
from .views import ProfileViewSet
from .views import MyProfileListView
# from .views import ProfileListView

app_name = 'basicapi'

router = DefaultRouter()
router.register('profiles', ProfileViewSet)

urlpatterns = [
    path('users/create/', CreateUserView.as_view(), name='users-create'),
    path('users/', UsersView.as_view(), name='users'),
    path('users/<uuid:pk>/', UserView.as_view(), name='user'),
    path('users/profile/<uuid:pk>/', MyProfileListView.as_view(), name='users-myprofile'),
    # path('users/profile/<uuid:pk>/', ProfileListView.as_view(), name='users-profile'),
    path('', include(router.urls)),
]
