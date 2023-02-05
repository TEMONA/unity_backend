from django.http import HttpResponse
from .modules.connector import Connector
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

# UUIDだとバグる問題のパッチ
# from uuid import UUID
# from json import JSONEncoder
# https://github.com/jazzband/django-push-notifications/issues/586
# old_default = JSONEncoder.default
# def new_default(self, obj):
#     if isinstance(obj, UUID):
#         return str(obj)
#     return old_default(self, obj)

# JSONEncoder.default = new_default

class AllMembers(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = (AllowAny,)

    """カオナビの社員一覧を取得"""
    def get(self, request):
        response = Connector().get_members()
        if response.is_success():
            return Response(response.data, status=status.HTTP_200_OK)
        else:
            return Response(response.error_messages(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Member(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = (AllowAny,)

    """カオナビの社員1名を取得"""
    def get(self, request, code):
        response = Connector().get_member(code)
        if response.is_success():
            return Response(response.data, status=status.HTTP_200_OK)
        else:
            return Response(response.error_messages(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

