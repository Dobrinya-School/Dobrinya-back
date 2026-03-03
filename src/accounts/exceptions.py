from rest_framework.exceptions import APIException

class RPCPermissionDenied(APIException):
    status_code = 403
    default_detail = "Нет доступа к ресурсу"
    default_code = "permission_denied"

    def __init__(self, detail=None, status_code=None):
        if detail:
            self.detail = {"status": "error", "detail": detail}
        else:
            self.detail = {"status": "error", "detail": self.default_detail}

        if status_code:
            self.status_code = status_code

class RPCNotFound(APIException):
    status_code = 404
    default_detail = "Ресурс не найден"
    default_code = "not_found"

    def __init__(self, detail=None, status_code=None):
        if detail:
            self.detail = {"status": "error", "detail": detail}
        else:
            self.detail = {"status": "error", "detail": self.default_detail}

        if status_code:
            self.status_code = status_code