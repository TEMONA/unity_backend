import json
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
from ...models import User
from ..api_result import ApiResult
from .user_filter import UserFilter as KaonaviUserFilter

END_POINT_URL_BASE = 'https://api.kaonavi.jp/api/v2.0'
SELF_INTRO_SHEET_ID = 20
NONE_AS_DEFAULT_VALUE = None
NAME_FIELD_ID = 284
BIRTH_PLACE_FIELD_ID = 286
JOB_DESCRIPTION_FIELD_ID = 287
CAREER_FIELD_ID = 288
HOBBY_FIELD_ID = 289
SPECIALTY_FIELD_ID = 290 # 特技
STRENGTHS_FIELD_ID = 291 # アピールポイント
MESSAGE_FIELD_ID = 292

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

    def get_self_introduction_sheet(self):
        response = requests.get(
            f"{END_POINT_URL_BASE}/sheets/{SELF_INTRO_SHEET_ID}",
            data='grant_type=client_credentials',
            headers={
                'Content-Type': 'application/json',
                'Kaonavi-Token': self.access_token
            },
        )
        return response.json()

    def get_users(self, params):
        """全社員情報取得"""
        kaonavi_users = KaonaviUserFilter(params, self.get_kaonavi_users()).call()

        if len(kaonavi_users) == 0:
            return ApiResult(success=True, data=[])
        else:
            self_intro_sheets = self.get_self_introduction_sheet()
            formatted_users = []
            for kaonavi_user in kaonavi_users:
                user = User.objects.get(kaonavi_code=kaonavi_user['code'])
                departments = kaonavi_user['department']['names']
                role = next((custom_field for custom_field in kaonavi_user['custom_fields'] if custom_field['name'] == '役職'), NONE_AS_DEFAULT_VALUE)
                my_sheet = next((sheet for sheet in self_intro_sheets['member_data'] if sheet['code'] == kaonavi_user['code']), NONE_AS_DEFAULT_VALUE)
                if my_sheet is not None:
                    job_description = next((custom_field for custom_field in my_sheet['records'][0]['custom_fields'] if custom_field['id'] == JOB_DESCRIPTION_FIELD_ID), NONE_AS_DEFAULT_VALUE)
                    job_description = job_description['values'][0] if job_description is not None else ''
                else:
                    job_description = ''

                formatted_users.append(
                    dict(
                        user_id=user.id,
                        chatwork_id=user.chatwork_id,
                        email=user.email,
                        name=kaonavi_user['name'],
                        name_kana=kaonavi_user['name_kana'],
                        headquarters=departments[0] if len(departments) >= 1 else '',
                        department=departments[1] if len(departments) >= 2 else '',
                        group=departments[2] if len(departments) >= 3 else '',
                        role=role['values'][0] if role is not None else '',
                        job_description=job_description
                    )
                )
            return ApiResult(success=True, data=formatted_users)

    def get_user(self, user_id, kaonavi_code):
        """カオナビの社員codeに紐づく社員情報取得"""
        kaonavi_user = next((kaonavi_user for kaonavi_user in self.get_kaonavi_users() if kaonavi_user['code'] == kaonavi_code), NONE_AS_DEFAULT_VALUE)
        if kaonavi_user is None:
            return ApiResult(success=False, errors=[f"id:{user_id}の社員情報の取得に失敗しました"])
        else:
            user = User.objects.get(kaonavi_code=kaonavi_user['code'])
            departments = kaonavi_user['department']['names']
            formatted_user = dict(
                overview=dict(
                    image='https//path_to_image.com',
                    email=user.email,
                    name=kaonavi_user['name'],
                    name_kana=kaonavi_user['name_kana'],
                    chatwork_id=user.chatwork_id,
                    headquarters=departments[0] if len(departments) >= 1 else '',
                    department=departments[1] if len(departments) >= 2 else '',
                    group=departments[2] if len(departments) >= 3 else '',
                ),
                tags=self.tags(kaonavi_user),
                details=self.self_introduction_info(kaonavi_user)
            )
            return ApiResult(success=True, data=formatted_user)

    def tags(self, kaonavi_user):
        years_of_service = f"勤続{kaonavi_user['years_of_service']}"
        _role = next((custom_field for custom_field in kaonavi_user['custom_fields'] if custom_field['name'] == '役職'), NONE_AS_DEFAULT_VALUE)
        role = f"役職：{_role['values'][0]}" if _role is not None else None
        _recruit_category = next((custom_field for custom_field in kaonavi_user['custom_fields'] if custom_field['name'] == '採用区分'), NONE_AS_DEFAULT_VALUE)
        recruit_category = _recruit_category['values'][0] if _recruit_category is not None else None
        gender = kaonavi_user['gender']

        _tags = dict(
            years_of_service=years_of_service,
            role=role,
            recruit_category=recruit_category,
            gender=gender
        )

        # Noneのものは返り値に含めない
        return [value for value in _tags.values() if value is not None]

    def self_introduction_info(self, kaonavi_user):
        sheets = self.get_self_introduction_sheet()
        my_sheet = next((sheet for sheet in sheets['member_data'] if sheet['code'] == kaonavi_user['code']), NONE_AS_DEFAULT_VALUE)
        data = dict(
            job_description=dict(title='業務内容、役割', value=''),
            birth_place=dict(title='出身地', value=''),
            career=dict(title='経歴、職歴', value=''),
            hobby=dict(title='趣味', value=''),
            specialty=dict(title='特技', value=''),
            strengths=dict(title='アピールポイント', value=''),
            message=dict(title='最後にひとこと', value='')
        )

        if my_sheet is None:
            return data
        else:
            custom_fields = my_sheet['records'][0]['custom_fields']
            # Pythonにswitch文無いんだ、他にいい書き方ないかな
            for custom_field in custom_fields:
                custom_field_value = custom_field['values'][0]
                if custom_field['id'] == JOB_DESCRIPTION_FIELD_ID:
                    data['job_description']['value'] = custom_field_value
                elif custom_field['id'] == BIRTH_PLACE_FIELD_ID:
                    data['birth_place']['value'] = custom_field_value
                elif custom_field['id'] == CAREER_FIELD_ID:
                    data['career']['value'] = custom_field_value
                elif custom_field['id'] == HOBBY_FIELD_ID:
                    data['hobby']['value'] = custom_field_value
                elif custom_field['id'] == SPECIALTY_FIELD_ID:
                    data['specialty']['value'] = custom_field_value
                elif custom_field['id'] == STRENGTHS_FIELD_ID:
                    data['strengths']['value'] = custom_field_value
                elif custom_field['id'] == MESSAGE_FIELD_ID:
                    data['message']['value'] = custom_field_value
            return data

    def create_or_update_self_introduction_info(self, user, params):
        sheets = self.get_self_introduction_sheet()
        my_sheet = next((sheet for sheet in sheets['member_data'] if sheet['code'] == user.kaonavi_code), NONE_AS_DEFAULT_VALUE)
        request_json = self.build_self_introduction_json(user, params)

        if my_sheet is None:
            # 自己紹介シート未作成の場合は新規作成
            method = 'POST'
            url = f"{END_POINT_URL_BASE}/sheets/{SELF_INTRO_SHEET_ID}/add"
        else:
            # 既に自己紹介シート作成済の場合は更新
            method = 'PATCH'
            url = f"{END_POINT_URL_BASE}/sheets/{SELF_INTRO_SHEET_ID}"

        response = requests.request(
            method=method,
            url=url,
            headers={
                'Content-Type': 'application/json',
                'Kaonavi-Token': self.access_token,
                # 'Dry-Run': '1' # 1はテスト
            },
            data=request_json
        )

        if response.ok:
            return ApiResult(success=True)
        else:
            errors = response.json()['errors']
            return ApiResult(success=False, errors=errors)

    def build_self_introduction_json(self, user, params):
        obj = {
            "member_data": [
                {
                    "code": user.kaonavi_code,
                    "records": [
                        {
                            "custom_fields": [
                                {"id": NAME_FIELD_ID, "values": [user.username]},
                                {"id": BIRTH_PLACE_FIELD_ID, "values": [params['birth_place']]},
                                {"id": JOB_DESCRIPTION_FIELD_ID, "values": [params['job_description']]},
                                {"id": CAREER_FIELD_ID, "values": [params['career']]},
                                {"id": HOBBY_FIELD_ID, "values": [params['hobby']]},
                                {"id": SPECIALTY_FIELD_ID, "values": [params['specialty']]},
                                {"id": STRENGTHS_FIELD_ID, "values": [params['strengths']]},
                                {"id": MESSAGE_FIELD_ID, "values": [params['message']]}
                            ]
                        }
                    ]
                }
            ]
        }
        return json.dumps(obj)