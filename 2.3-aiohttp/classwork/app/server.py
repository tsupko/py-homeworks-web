import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db import Session, User, close_orm, init_orm

app = web.Application()


async def orm_context(app: web.Application):
    print("START")
    await init_orm()
    yield
    await close_orm()
    print("END")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def get_error(err_cls, error_message):
    error_message = {"error": error_message}
    error_message = json.dumps(error_message)
    return err_cls(body=error_message, content_type="application/json")


class UserView(web.View):

    @property
    def user_id(self) -> int:
        return int(self.request.match_info["user_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_user(self) -> User:
        user = await self.session.get(User, self.user_id)
        if user is None:
            raise get_error(web.HTTPNotFound, "User not found")
        return user

    async def add_user(self, user: User):
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            raise get_error(web.HTTPConflict, "User already exists")

    async def delete_user(self):
        user = await self.get_user()
        await self.session.delete(user)
        await self.session.commit()

    async def get(self):
        user = await self.get_user()
        return web.json_response(user.json)

    async def post(self):
        json_data = await self.request.json()

        user = User(name=json_data["name"], password=json_data["password"])
        await self.add_user(user)
        return web.json_response(user.id_dict)

    async def patch(self):
        user = await self.get_user()
        json_data = await self.request.json()

        for field, value in json_data.items():
            setattr(user, field, value)

        await self.add_user(user)

        return web.json_response(user.id_dict)

    async def delete(self):
        await self.delete_user()
        return web.json_response({"status": "deleted"})


async def hello_world(request: web.Request):
    json_data = await request.json()
    headers = request.headers
    qs = request.query
    some_id = int(request.match_info["some_id"])

    print(f"{json_data=}")
    print(f"{headers=}")
    print(f"{qs=}")
    print(f"{some_id=}")

    return web.json_response({"hello": "world"})


app.add_routes(
    [
        web.post(r"/hello/world/{some_id:\d+}", hello_world),
        web.post("/users", UserView),
        web.get(r"/users/{user_id:\d+}", UserView),
        web.patch(r"/users/{user_id:\d+}", UserView),
        web.delete(r"/users/{user_id:\d+}", UserView),
    ]
)

web.run_app(app)
