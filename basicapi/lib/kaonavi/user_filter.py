class UserFilter:
    def __init__(self, params, kaonavi_users):
        self.kaonavi_users = kaonavi_users
        self.name = params.get('name')
        self.headquarters = params.get('headquarters')
        self.department = params.get('department')
        self.group = params.get('group')
        self.gender = params.get('gender')
        # self.years_of_service = params.get('years_of_service')

    def call(self):
        records = self.kaonavi_users

        if self.name:
            records = self.filter_list(lambda user: self.name in user['name'], records)

        if self.headquarters:
            records = self.filter_list(lambda user: self.headquarters in user['department']['name'], records)

        if self.department:
            records = self.filter_list(lambda user: self.department in user['department']['name'], records)

        if self.group:
            records = self.filter_list(lambda user: self.group in user['department']['name'], records)

        if self.gender: # 男性 or 女性
            records = self.filter_list(lambda user: self.gender in user['gender'], records)

        # if self.years_of_service:
            # 「x年以上」「x年以下」「x年台」なのか
        return records

    # イテラブルから条件に合う要素を抽出してリストで返す
    def filter_list(self, func, iterable):
        result = filter(func, iterable)
        return list(result)