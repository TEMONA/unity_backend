from django.urls import path
from kaonaviapi import views

app_name = 'kaonaviapi'
urlpatterns = [
    path('members', views.AllMembers.as_view(), name='members'),
    path('members/<str:code>', views.Member.as_view(), name='member'),
]