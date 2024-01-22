from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import User, Profile, LunchRequests
from .serializers import UserSerializer, ProfileSerializer, LunchRequestsSerializer
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings
from .lib.kaonavi.connector import KaonaviConnector


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

class UsersView(APIView):
    def get(self, request):
        response = KaonaviConnector().get_users(request.query_params)
        if response.is_success():
            return Response(response.data, status=status.HTTP_200_OK)
        else:
            return Response(response.error_messages(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserView(APIView):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        kaonavi_code = user.kaonavi_code
        response = KaonaviConnector().get_user(user.id, kaonavi_code)
        if response.is_success():
            return Response(response.data, status=status.HTTP_200_OK)
        else:
            return Response(response.error_messages(), status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = User.objects.get(pk=pk)
        params = request.data
        response = KaonaviConnector().create_or_update_self_introduction_info(user, params['contents'])

        if response.is_success():
            data = dict(user_id=user.id, success=True)
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = dict(user_id=user.id, success=False, errors=response.errors)
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

class LunchRequestsViewSet(ModelViewSet):
    queryset = LunchRequests.objects.all()
    serializer_class = LunchRequestsSerializer

    def get_queryset(self):
        return self.queryset

    def perform_create(self, serializer):
        serializer.save()

class MyLunchRequestsListView(RetrieveUpdateAPIView):
    queryset = LunchRequests.objects.all()
    serializer_class = LunchRequestsSerializer

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return self.queryset.filter(applicant=user_id)
