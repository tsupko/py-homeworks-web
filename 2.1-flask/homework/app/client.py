import requests

# Данные для тестового объявления
test_ad = {
    "title": "Тестовое объявление",
    "description": "Это тестовое объявление"
}

# 1. Выполняем вход под тестовым пользователем
login_response = requests.post('http://127.0.0.1:5000/login',
                               json={'email': 'user1@example.com', 'password': 'password123'})
print("Вход:", login_response.status_code, login_response.json())

# 2. Создаем новое объявление
create_response = requests.post('http://127.0.0.1:5000/ad',
                                json=test_ad,
                                auth=('user1@example.com', 'password123'))
print("Создание объявления:", create_response.status_code, create_response.json())

# 3. Получаем объявление по ID
ad_id = create_response.json().get('id')
if ad_id:
    get_response = requests.get(f'http://127.0.0.1:5000/ad/{ad_id}',
                                auth=('user1@example.com', 'password123'))
    print("Получение объявления:", get_response.status_code, get_response.json())

# 4. Обновляем объявление (меняем описание)
if ad_id:
    patch_response = requests.patch(f'http://127.0.0.1:5000/ad/{ad_id}',
                                    json={'description': 'Обновленное описание'},
                                    auth=('user1@example.com', 'password123'))
    print("Обновление объявления:", patch_response.status_code, patch_response.json())

# 5. Удаляем объявление
if ad_id:
    delete_response = requests.delete(f'http://127.0.0.1:5000/ad/{ad_id}',
                                      auth=('user1@example.com', 'password123'))
    print("Удаление объявления:", delete_response.status_code, delete_response.json())
