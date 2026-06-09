import base64

from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db import Session, Ad, close_orm, init_orm, verify_password, register_user
from errors import HttpError

app = web.Application()


async def orm_context(app: web.Application):
    print("START ORM")
    await init_orm()
    yield
    await close_orm()
    print("END ORM")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


@web.middleware
async def auth_middleware(request: web.Request, handler):
    """Middleware для проверки аутентификации пользователя."""
    if request.path == '/login' or (request.method == 'GET' and request.path.startswith('/ad/')):
        return await handler(request)

    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Basic '):
        return web.json_response({"error": "Требуется аутентификация"}, status=401)

    try:
        auth_bytes = base64.b64decode(auth[6:])
        auth_str = auth_bytes.decode('utf-8')
        email, password = auth_str.split(':', 1)
    except (ValueError, UnicodeDecodeError):
        return web.json_response({"error": "Неверные учетные данные"}, status=401)

    if not await verify_password(request.session, email, password):
        if request.method == 'POST' and request.path == '/login':
            try:
                await register_user(request.session, email, password)
                request.user_email = email
                return await handler(request)
            except IntegrityError:
                return web.json_response({"error": "Пользователь уже существует"}, status=409)
        return web.json_response({"error": "Неверные учетные данные"}, status=401)

    request.user_email = email
    return await handler(request)


@web.middleware
async def error_middleware(request: web.Request, handler):
    """Middleware для обработки ошибок."""
    try:
        return await handler(request)
    except HttpError as error:
        return web.json_response({"error": error.message}, status=error.status_code)
    except Exception as error:
        return web.json_response({"error": str(error)}, status=500)


app.cleanup_ctx.append(orm_context)
app.middlewares.append(error_middleware)
app.middlewares.append(session_middleware)
app.middlewares.append(auth_middleware)


class AdView(web.View):
    """View для работы с объявлениями."""

    @property
    def ad_id(self) -> int:
        return int(self.request.match_info["ad_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_ad(self, ad_id: int) -> Ad:
        """Получить объявление по ID или вызвать 404."""
        ad = await self.session.get(Ad, ad_id)
        if ad is None:
            raise HttpError(404, "Объявление не найдено")
        return ad

    async def check_owner(self, ad: Ad):
        """Проверить, что объявление принадлежит текущему пользователю."""
        if ad.owner != self.request.user_email:
            raise HttpError(403, "У вас нет прав на это объявление")

    async def add_ad(self, ad: Ad):
        self.session.add(ad)
        try:
            await self.session.commit()
        except IntegrityError:
            raise HttpError(409, "Объявление с таким заголовком уже существует")

    async def delete_ad(self, ad: Ad):
        await self.session.delete(ad)
        await self.session.commit()

    async def get(self):
        """Получить объявление по ID (общедоступно)."""
        ad = await self.get_ad(self.ad_id)
        return web.json_response(ad.dict)

    async def post(self):
        """Создать новое объявление."""
        json_data = await self.request.json()
        if not json_data:
            raise HttpError(400, "Тело запроса обязательно")

        title = json_data.get("title")
        if not title:
            raise HttpError(400, "Заголовок объявления обязателен")

        ad = Ad(
            title=title,
            description=json_data.get("description") or "",
            owner=self.request.user_email
        )
        await self.add_ad(ad)
        return web.json_response(ad.dict, status=201)

    async def patch(self):
        """Обновить объявление (требуется аутентификация и владение)."""
        json_data = await self.request.json()
        if not json_data:
            raise HttpError(400, "Тело запроса обязательно")

        ad = await self.get_ad(self.ad_id)
        await self.check_owner(ad)

        if "title" in json_data:
            ad.title = json_data["title"]
        if "description" in json_data:
            ad.description = json_data["description"]

        await self.add_ad(ad)
        return web.json_response(ad.dict)

    async def delete(self):
        """Удалить объявление (требуется аутентификация и владение)."""
        ad = await self.get_ad(self.ad_id)
        await self.check_owner(ad)
        await self.delete_ad(ad)
        return web.json_response({"deleted": self.ad_id})


async def login(request: web.Request):
    """Конечная точка для аутентификации и регистрации."""
    json_data = await request.json()
    if not json_data:
        raise HttpError(400, "Тело запроса обязательно")

    email = json_data.get("email")
    password = json_data.get("password")

    if not email or not password:
        raise HttpError(400, "Email и пароль обязательны")

    if not await verify_password(request.session, email, password):
        try:
            await register_user(request.session, email, password)
            return web.json_response({
                "message": "Пользователь зарегистрирован",
                "user": {"email": email}
            }, status=201)
        except IntegrityError:
            raise HttpError(409, "Пользователь уже существует")

    return web.json_response({
        "message": "Вход выполнен успешно",
        "user": {"email": email}
    })


app.add_routes(
    [
        web.post("/ad", AdView),
        web.get(r"/ad/{ad_id:\d+}", AdView),
        web.patch(r"/ad/{ad_id:\d+}", AdView),
        web.delete(r"/ad/{ad_id:\d+}", AdView),
        web.post("/login", login),
    ]
)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)
