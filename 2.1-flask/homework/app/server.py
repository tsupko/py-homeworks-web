from functools import wraps

from flask import Flask, request, jsonify, g
from flask.views import MethodView

from db import Session, Ad, verify_password
from errors import HttpError

app = Flask('app')


def auth_required(func):
    """Декоратор для проверки аутентификации пользователя.
    
    Декоратор проверяет наличие учетных данных в заголовке Authorization.
    Если аутентификация не удалась, выбрасывает HttpError с кодом 401.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth:
            raise HttpError(401, "Требуется аутентификация")

        if not verify_password(auth.username, auth.password):
            raise HttpError(401, "Неверные учетные данные")

        # Сохраняем email пользователя в объекте g Flask
        g.user_email = auth.username
        return func(*args, **kwargs)

    return wrapper


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    """Обработчик ошибок HttpError для возврата JSON-ответа."""
    response = jsonify({"error": error.message})
    response.status_code = error.status_code
    return response


class AdView(MethodView):
    """View для работы с объявлениями (CRUD операции).
    
    Все методы защищены декоратором auth_required, требуется аутентификация.
    Пользователь может редактировать и удалять только свои объявления.
    """
    decorators = [auth_required]

    def _get_ad(self, session, ad_id):
        """Вспомогательный метод для получения объявления и проверки прав доступа.
        
        Args:
            session: Сессия SQLAlchemy
            ad_id: Идентификатор объявления
            
        Returns:
            Объект Ad
            
        Raises:
            HttpError(404): Если объявление не найдено
            HttpError(403): Если объявление не принадлежит текущему пользователю
        """
        ad = session.get(Ad, ad_id)
        if ad is None:
            raise HttpError(404, "Объявление не найдено")
        
        if ad.owner != g.user_email:
            raise HttpError(403, "У вас нет прав на это объявление")
        
        return ad

    def post(self):
        """Создает новое объявление.
        
        Ожидает JSON с полями:
        - title (обязательное): заголовок объявления
        - description: описание объявления (необязательное)
        
        Возвращает созданный объект объявления с кодом 201.
        """
        body = request.json
        if not body:
            raise HttpError(400, "Тело запроса обязательно")

        title = body.get("title")
        description = body.get("description")

        if not title:
            raise HttpError(400, "Заголовок объявления обязателен")

        with Session() as session:
            ad = Ad(
                title=title,
                description=description or "",
                owner=g.user_email
            )
            session.add(ad)
            session.commit()

            return jsonify(ad.dict), 201

    def get(self, id: int):
        """Получает объявление по его идентификатору.
        
        Возвращает объект объявления или 404, если не найдено.
        Для GET нет проверки ownership, так как объявления могут быть публичными.
        """
        with Session() as session:
            ad = session.get(Ad, id)
            if ad is None:
                raise HttpError(404, "Объявление не найдено")
            return jsonify(ad.dict)

    def patch(self, id: int):
        """Редактирует существующее объявление.
        
        Допустимые поля для обновления:
        - title: новый заголовок (необязательное)
        - description: новое описание (необязательное)
        
        Проверяет, что объявление принадлежит текущему пользователю.
        """
        body = request.json
        if not body:
            raise HttpError(400, "Тело запроса обязательно")

        with Session() as session:
            ad = self._get_ad(session, id)

            if "title" in body:
                ad.title = body["title"]
            if "description" in body:
                ad.description = body["description"]

            session.commit()
            return jsonify(ad.dict)

    def delete(self, id: int):
        """Удаляет объявление по его идентификатору.
        
        Проверяет, что объявление принадлежит текущему пользователю.
        Возвращает идентификатор удаленного объявления.
        """
        with Session() as session:
            ad = self._get_ad(session, id)
            session.delete(ad)
            session.commit()

            return jsonify({"deleted": id})


ad_view = AdView.as_view('ad_view')

app.add_url_rule('/ad', view_func=ad_view, methods=['POST'])
app.add_url_rule('/ad/<int:id>', view_func=ad_view, methods=['GET', 'PATCH', 'DELETE'])


@app.route('/login', methods=['POST'])
def login():
    """Эндпоинт для входа тестовых пользователей.
    
    Ожидает JSON с полями:
    - email: email пользователя
    - password: пароль пользователя
    
    Возвращает сообщение об успешном входе и информацию о пользователе.
    Доступно только для предопределенных тестовых пользователей.
    """
    body = request.json
    if not body:
        raise HttpError(400, "Тело запроса обязательно")

    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HttpError(400, "Email и пароль обязательны")

    if not verify_password(email, password):
        raise HttpError(401, "Неверные учетные данные")

    return jsonify({
        "message": "Вход выполнен успешно",
        "user": {"email": email}
    })


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
