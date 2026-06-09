import asyncio

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        # 1. Регистрация нового пользователя
        async with session.post(
                "http://127.0.0.1:8080/login",
                json={"email": "newuser@example.com", "password": "newpass123"},
        ) as response:
            print("Регистрация:", response.status, await response.json())

        # 2. Вход с зарегистрированным пользователем
        async with session.post(
                "http://127.0.0.1:8080/login",
                json={"email": "newuser@example.com", "password": "newpass123"},
        ) as response:
            print("Вход:", response.status, await response.json())

        # 3. Создание объявления (требует аутентификацию)
        import base64
        auth_str = "newuser@example.com:newpass123"
        auth_bytes = base64.b64encode(auth_str.encode('utf-8'))
        auth_header = f"Basic {auth_bytes.decode('utf-8')}"

        async with session.post(
                "http://127.0.0.1:8080/ad",
                json={"title": "Test ad", "description": "Test description"},
                headers={"Authorization": auth_header},
        ) as response:
            print("Создание объявления:", response.status)
            ad_data = await response.json()
            print(ad_data)
            ad_id = ad_data.get("id")

        # 4. Получение объявления (общедоступно)
        if ad_id:
            async with session.get(f"http://127.0.0.1:8080/ad/{ad_id}") as response:
                print("Получение объявления:", response.status, await response.json())

        # 5. Обновление объявления
        if ad_id:
            async with session.patch(
                    f"http://127.0.0.1:8080/ad/{ad_id}",
                    json={"description": "Updated"},
                    headers={"Authorization": auth_header},
            ) as response:
                print("Обновление объявления:", response.status, await response.json())

        # 6. Удаление объявления
        if ad_id:
            async with session.delete(f"http://127.0.0.1:8080/ad/{ad_id}",
                                      headers={"Authorization": auth_header}) as response:
                print("Удаление объявления:", response.status, await response.json())


asyncio.run(main())
