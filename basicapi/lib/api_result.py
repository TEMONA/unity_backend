class ApiResult:
    def __init__(self, success, data=None, errors=[],):
        self.success = success
        self.data = data
        self.errors = errors

    def is_success(self):
        return self.success

    def error_messages(self):
        return list(map(str, self.errors))