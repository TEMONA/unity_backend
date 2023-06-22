import json
from django.conf import settings
import requests
from botocore.exceptions import ClientError
from requests.auth import HTTPBasicAuth
from django.core.paginator import EmptyPage, Paginator
from ...models import User
from ..api_result import ApiResult
from .user_filter import UserFilter as KaonaviUserFilter

END_POINT_URL_BASE = 'https://api.kaonavi.jp/api/v2.0'
SELF_INTRO_SHEET_ID = 20
NONE_AS_DEFAULT_VALUE = None
BIRTH_PLACE_FIELD_ID = 286
JOB_DESCRIPTION_FIELD_ID = 287
CAREER_FIELD_ID = 288
HOBBY_FIELD_ID = 289
SPECIALTY_FIELD_ID = 290 # 特技
STRENGTHS_FIELD_ID = 291 # アピールポイント
MESSAGE_FIELD_ID = 292

DEFAULT_PER_PAGE = 30
DEFAULT_PAGE = 1

class KaonaviConnector:
    def __init__(self):
        self.access_token = self.get_access_token()

    def get_access_token(self):
        '''
        カオナビAPIのアクセストークンを取得する
        カオナビAPIにアクセスするには毎回このトークンをリクエストヘッダーに含める必要がある
        [POST] /token
        '''
        response = requests.post(
            f"{END_POINT_URL_BASE}/token",
            auth=HTTPBasicAuth(
                settings.KAONAVI_API_KEY,
                settings.KAONAVI_API_SECRET,
            ),
            data='grant_type=client_credentials',
            headers={'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
        )
        return response.json()['access_token']

    def get_kaonavi_users(self):
        '''
        カオナビに登録されている社員情報一覧を取得する
        [GET] /members
        '''
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
        '''
        カオナビに登録されている自己紹介シートを取得する
        [GET] /sheets/:sheet_id
        '''
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
        '''
        カオナビ上に登録されている社員情報一覧を取得したのちに、
        djangoアプリ上のDBに保存されているユーザーと突合させてカオナビ上にある社員情報とDBに保存しているユーザー(社員)情報を併せて返却する
        kaonavi_user → カオナビ上の社員データ
        以下のようにgetでDBに問い合わせしているため、
        user = User.objects.get(kaonavi_code=kaonavi_user['code'])
        カオナビ上に存在するが、djangoのDBに存在しないという場合にはエラーになる
        どちらにも存在する前提としている
        処理の最後でページネーションの処理があり、per_pageとpageをフロントから受け取る
        '''
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
                        image=self.get_profile_image_path(user.username),
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

            selected_per_page = int(params['per_page']) if params.get('per_page') is not None else DEFAULT_PER_PAGE
            selected_page = int(params['page']) if params.get('page') is not None else DEFAULT_PAGE

            paginator = Paginator(formatted_users, selected_per_page)

            try:
                page = paginator.page(selected_page)
                data = dict(
                    records=page.object_list,
                    meta=dict(
                        limit=selected_per_page,
                        total_pages=paginator.num_pages,
                        total_count=paginator.count,
                        current_page=selected_page,
                        has_next_page=page.has_next(),
                        next_page=page.next_page_number() if page.has_next() else None,
                        has_previous_page=page.has_previous(),
                        previous_page=page.previous_page_number() if page.has_previous() else None
                    )
                )

                return ApiResult(success=True, data=data)
            except EmptyPage:
                return ApiResult(success=False, errors=['指定されたページは存在しません'])

    def get_user(self, user_id, kaonavi_code):
        '''
        引数で受け取るUser.kaonavi_codeを元にカオナビ上の社員情報一覧から、該当の社員情報を取得する
        引数のkaonavi_codeの社員情報がカオナビ上に存在しない場合は500エラーを返す(存在する前提)
        タグや自己紹介シートの値などもカオナビ上から取得してレスポンスに含めてる
        '''
        kaonavi_user = next((kaonavi_user for kaonavi_user in self.get_kaonavi_users() if kaonavi_user['code'] == kaonavi_code), NONE_AS_DEFAULT_VALUE)
        if kaonavi_user is None:
            return ApiResult(success=False, errors=[f"id:{user_id}の社員情報の取得に失敗しました"])
        else:
            user = User.objects.get(kaonavi_code=kaonavi_user['code'])
            departments = kaonavi_user['department']['names']
            formatted_user = dict(
                overview=dict(
                    image=self.get_profile_image_path(user.username),
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

    def get_profile_image_path(self, username):
        '''
        S3に格納されたその社員のプロフィール画像の絶対パス(https:xxx.jpg)を返す
        S3にその社員のプロフィール画像が存在しない場合はno-image画像の絶対パスを返す
        '''
        s3_client = settings.STORAGE_CLIENT
        params={
            'Bucket': settings.AWS_S3_BUCKET_NAME,
            'Key': f"all-profile-images/{username}.jpg"
        }

        if self.is_profile_image_exist(s3_client, params) == False:
            params['Key'] = 'all-profile-images/no-image.jpg'

        image_url = s3_client.generate_presigned_url('get_object',
            Params=params,
            ExpiresIn=settings.AWS_S3_EXPIRES_IN)

        return image_url

    def is_profile_image_exist(self, s3_client, params):
        '''
        S3にその社員のプロフィール画像が存在するかを確認する
        存在している場合はTrue、存在しない場合はFalseを返す
        '''
        try:
            s3_client.head_object(Bucket=params['Bucket'], Key=params['Key'])
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False

    def tags(self, kaonavi_user):
        '''
        勤続年数などの値を配列で返す
        フロントでタグとして表示させることを目的としている
        役職(role)など人によって空白となる項目に関しては、空白(None)の場合は返り値に含めずに、
        存在する値のみレスポンスする
        '''
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
        '''
        カオナビ上に保存されている自己紹介シート(カスタムフォーム)を取得し、フォーマットして返却する
        各社員がカオナビ上で自由に編集できるシートになっているため、データが存在しない場合もある
        データが存在しない場合は各項目のvalueを空文字として返却する
        '''
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
        '''
        カオナビ上の自己紹介シート(カスタムフォーム)の作成/編集をする
        このメソッドへのエンドポイントは[PATCH] /users/:user_id だが、
        このメソッド内でのカオナビへのリクエストエンドポイントは以下のように分岐する
        ↓
        該当社員の自己紹介シートが未作成の場合：[POST] /sheets/:sheet_id/add に対してリクエストし、新規作成
        該当社員の自己紹介シートが存在する場合：[PATCH] /sheets/:sheet_id に対してリクエストし、更新
        '''
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
        '''
        create_or_update_self_introduction_infoメソッドにて自己紹介シートを作成/更新する際の項目をjsonで返却する
        以下カオナビAPIの「シート情報」の仕様に基づいてる
        https://developer.kaonavi.jp/api/v2.0/index.html#tag/%E3%82%B7%E3%83%BC%E3%83%88%E6%83%85%E5%A0%B1/paths/~1sheets~1%7Bsheet_id%7D/patch
        '''
        obj = {
            "member_data": [
                {
                    "code": user.kaonavi_code,
                    "records": [
                        {
                            "custom_fields": [
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