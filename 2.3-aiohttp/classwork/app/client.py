import asyncio

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(
                "http://127.0.0.1:8080/users",
                json={"name": "user_3", "password": "1234"},
        ) as response:
            print(response.status)
            print(await response.json())

        async with session.patch(
                "http://127.0.0.1:8080/users/15",
                json={"name": "new_user_name_2"},
        ) as response:
            print(response.status)
            print(await response.json())

        async with session.get("http://127.0.0.1:8080/users/15") as response:
            print(response.status)
            print(await response.json())

        async with session.delete("http://127.0.0.1:8080/users/15") as response:
            print(response.status)
            print(await response.json())

        async with session.get("http://127.0.0.1:8080/users/15") as response:
            print(response.status)
            print(await response.json())


asyncio.run(main())
