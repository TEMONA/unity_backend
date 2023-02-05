from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
from .api_result import ApiResult

END_POINT_URL_BASE = 'https://api.kaonavi.jp/api/v2.0'

class Connector:
    def __init__(self):
        self.access_token = self.get_access_token()

    def get_access_token(self):
        response = requests.post(
            f"{END_POINT_URL_BASE}/token",
            auth=HTTPBasicAuth(
                getattr(settings, 'KAONAVI_API_KEY', None),
                getattr(settings, 'KAONAVI_API_SECRET', None),
            ),
            data='grant_type=client_credentials',
            headers={'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
        )
        return response.json()['access_token']

    def format_member_data(self, member):
        return dict(
            code=member['code'],
            name=member['name'],
            name_kana=member['name_kana'],
            mail=member['mail'],
            entered_date=member['entered_date'],
            gender=member['gender'],
            birthday=member['birthday'],
            age=member['age'],
            years_of_service=member['years_of_service'],
            department=member['department']['name'],
            # 現状sub_departmentsのある社員データが存在しないため考慮しない
            # sub_department=member['sub_departments']['name'],
            custom_fields=member['custom_fields']
        )

    def get_members(self):
        """全社員情報取得"""

        response = requests.get(
            f"{END_POINT_URL_BASE}/members",
            data='grant_type=client_credentials',
            headers={
                'Content-Type': 'application/json',
                'Kaonavi-Token': self.access_token
            },
        )

        member_data = response.json()['member_data']
        if len(member_data) >= 1:
            formatted_members = []
            for member in member_data:
                formatted_member = self.format_member_data(member)
                formatted_members.append(formatted_member)

            return ApiResult(success=True, data=formatted_members)
        else:
            return ApiResult(success=False, errors=['社員情報の取得に失敗しました'])

    def get_member(self, code):
        """リクエストパラメータのcodeに紐づく社員情報取得"""

        all_members = self.get_members().data
        member = list(filter(lambda member : member['code'] == code, all_members))

        if len(member) == 1:
            return ApiResult(success=True, data=member)
        else:
            return ApiResult(success=False, errors=[f"code:{code}の社員情報の取得に失敗しました"])