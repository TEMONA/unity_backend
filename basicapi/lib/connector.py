from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
from ..models import User
from .api_result import ApiResult

END_POINT_URL_BASE = 'https://api.kaonavi.jp/api/v2.0'

class KaonaviConnector:
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

    def get_users(self):
        """全社員情報取得"""

        response = requests.get(
            f"{END_POINT_URL_BASE}/members",
            data='grant_type=client_credentials',
            headers={
                'Content-Type': 'application/json',
                'Kaonavi-Token': self.access_token
            },
        )

        kaonavi_users = response.json()['member_data']
        if len(kaonavi_users) >= 1:
            formatted_users = []
            for kaonavi_user in kaonavi_users:
                formatted_user = self.format_user_data(kaonavi_user)
                formatted_users.append(formatted_user)

            return ApiResult(success=True, data=formatted_users)
        else:
            return ApiResult(success=False, errors=['社員情報の取得に失敗しました'])

    def get_user(self, user_id, kaonavi_code):
        """カオナビの社員codeに紐づく社員情報取得"""

        kaonavi_users = self.get_users().data
        user = list(filter(lambda user : user['code'] == kaonavi_code, kaonavi_users))

        if len(user) == 1:
            return ApiResult(success=True, data=user)
        else:
            return ApiResult(success=False, errors=[f"id:{user_id}の社員情報の取得に失敗しました"])

    def format_user_data(self, kaonavi_user):
        user = User.objects.get(kaonavi_code=kaonavi_user['code'])
        # 以下の感じでカスタムフィールドの値を取得できる(下手くそ)
        recruit_category = list(filter(lambda custom_field : custom_field['name'] == '採用区分', kaonavi_user['custom_fields']))[0]['values'][0]

        return dict(
            user_id=user.id,
            code=kaonavi_user['code'],
            name=kaonavi_user['name'],
            name_kana=kaonavi_user['name_kana'],
            mail=kaonavi_user['mail'],
            entered_date=kaonavi_user['entered_date'],
            gender=kaonavi_user['gender'],
            birthday=kaonavi_user['birthday'],
            age=kaonavi_user['age'],
            years_of_service=kaonavi_user['years_of_service'],
            department=kaonavi_user['department'],
            recruit_category=recruit_category,
            # 現状sub_departmentsのある社員データが存在しないため考慮しない
            # sub_department=user['sub_departments']['name'],
        )