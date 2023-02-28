from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
from ..models import User
from .api_result import ApiResult

END_POINT_URL_BASE = 'https://api.kaonavi.jp/api/v2.0'
SELF_INTRO_SHEET_ID = 20

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

    def get_kaonavi_users(self):
        response = requests.get(
            f"{END_POINT_URL_BASE}/members",
            data='grant_type=client_credentials',
            headers={
                'Content-Type': 'application/json',
                'Kaonavi-Token': self.access_token
            },
        )
        return response.json()['member_data']

    def get_users(self):
        """全社員情報取得"""
        kaonavi_users = self.get_kaonavi_users()
        if len(kaonavi_users) >= 1:
            formatted_users = []

            for kaonavi_user in kaonavi_users:
                user = User.objects.get(kaonavi_code=kaonavi_user['code'])
                departments = kaonavi_user['department']['names']
                role_list = list(filter(lambda custom_field : custom_field['name'] == '役職', kaonavi_user['custom_fields']))
                formatted_users.append(
                    dict(
                        user_id=user.id,
                        name=kaonavi_user['name'],
                        name_kana=kaonavi_user['name_kana'],
                        headquarters=departments[0] if len(departments) >= 1 else '',
                        department=departments[1] if len(departments) >= 2 else '',
                        group=departments[2] if len(departments) >= 3 else '',
                        role=role_list[0]['values'][0] if role_list else '',
                        # 未実装だからコメントアウト
                        # details=self.self_introduction_info(kaonavi_user['code'])
                    )
                )
            return ApiResult(success=True, data=formatted_users)
        else:
            return ApiResult(success=False, errors=['社員情報の取得に失敗しました'])

    def get_user(self, user_id, kaonavi_code):
        """カオナビの社員codeに紐づく社員情報取得"""
        kaonavi_user_list = list(filter(lambda user : user['code'] == kaonavi_code, self.get_kaonavi_users()))

        if len(kaonavi_user_list) == 1:
            kaonavi_user = kaonavi_user_list[0]
            departments = kaonavi_user['department']['names']
            formatted_user = dict(
                overview=dict(
                    image='https//path_to_image.com',
                    name=kaonavi_user['name'],
                    name_kana=kaonavi_user['name_kana'],
                    headquarters=departments[0] if len(departments) >= 1 else '',
                    department=departments[1] if len(departments) >= 2 else '',
                    group=departments[2] if len(departments) >= 3 else '',
                ),
                tags=self.tags(kaonavi_user),
                details=self.self_introduction_info(kaonavi_user['code'])
            )
            return ApiResult(success=True, data=formatted_user)
        else:
            return ApiResult(success=False, errors=[f"id:{user_id}の社員情報の取得に失敗しました"])

    def tags(self, kaonavi_user):
        # 職種、勤続年数、グレード、出社曜日、出身地、採用区分
        # 職種はカオナビ側で持ってないからtagsに含めない
        years_of_service = kaonavi_user['years_of_service']
        # グレードはカオナビ側で持ってない。なので役職(ex.グループ長)を代わりに使う
        role_list = list(filter(lambda custom_field : custom_field['name'] == '役職', kaonavi_user['custom_fields']))
        role = '' if len(role_list) == 0 else role_list[0]['values'][0]
        birth_place = '出身地'
        recruit_category_list = list(filter(lambda custom_field : custom_field['name'] == '採用区分', kaonavi_user['custom_fields']))
        recruit_category = recruit_category_list[0]['values'][0] if recruit_category_list else ''

        return [
            years_of_service,
            role,
            birth_place,
            recruit_category
        ]

    def self_introduction_info(self, kaonavi_code):
        sheets = requests.get(
            f"{END_POINT_URL_BASE}/sheets/{SELF_INTRO_SHEET_ID}",
            data='grant_type=client_credentials',
            headers={
                'Content-Type': 'application/json',
                'Kaonavi-Token': self.access_token
            },
        )
        # ここでkaonavi_codeと一致するデータを取得する

        return sheets.json()