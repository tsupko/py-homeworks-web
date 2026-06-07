class HttpError(Exception):
    """Исключение для обработки HTTP ошибок в приложении.
    
    Используется для унифицированной обработки ошибок API.
    Применяется совместно с обработчиком error_handler в server.py.
    
    Attributes:
        status_code: HTTP код ошибки (например, 400, 401, 404, 403)
        message: Сообщение об ошибке (строка, словарь или список)
    """
    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message
