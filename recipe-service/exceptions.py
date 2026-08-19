class AppError(Exception):
    status_code: int = 500

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)

class NotFoundError(AppError):
    status_code: int = 404

class ForbiddenError(AppError):
    status_code: int = 403
