from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings

class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

class UserView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

# 修正前
# class ProfileViewSet(ModelViewSet):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer

#     def get_queryset(self):
#         return self.queryset.filter(user=self.request.user)

# 修正後。これでプライマリーキーを指定すれば取れるようになった。
class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        uuid = self.kwargs['pk']
        return self.queryset.filter(user=uuid)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ユーザーの削除は、一旦該当するユーザーのis_activeを管理画面からfalseに変更する運用とする
    def destroy(self, request, *args, **kwargs):
        response = {'message': 'Delete is not allowed !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

class MyProfileListView(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
