from aiohttp import web
from sqlalchemy.exc import IntegrityError

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


class UserView(web.View):

    async def get(self):
        user_id = int(self.request.match_info["user_id"])
        async with Session() as session:
            user = await session.get(User, user_id)
            if user is None:
                raise web.HTTPNotFound(
                    body='{"error": "User not found"}', content_type="application/json"
                )
            return web.json_response(user.json)

    async def post(self):
        json_data = await self.request.json()
        async with Session() as session:
            user = User(name=json_data["name"], password=json_data["password"])
            session.add(user)
            try:
                await session.commit()
            except IntegrityError:
                raise web.HTTPConflict(
                    body='{"error": "User already exists"}',
                    content_type="application/json",
                )
            return web.json_response(user.id_dict)

    async def patch(self):
        user_id = int(self.request.match_info["user_id"])
        json_data = await self.request.json()
        async with Session() as session:
            user = await session.get(User, user_id)
            if user is None:
                raise web.HTTPNotFound(
                    body='{"error": "User not found"}', content_type="application/json"
                )

            for field, value in json_data.items():
                setattr(user, field, value)

            session.add(user)
            try:
                await session.commit()
            except IntegrityError:
                raise web.HTTPConflict(
                    body='{"error": "User already exists"}',
                    content_type="application/json",
                )

            return web.json_response(user.id_dict)

    async def delete(self):
        user_id = int(self.request.match_info["user_id"])
        async with Session() as session:
            user = await session.get(User, user_id)
            if user is None:
                raise web.HTTPNotFound(
                    body='{"error": "User not found"}', content_type="application/json"
                )
            await session.delete(user)
            await session.commit()
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
