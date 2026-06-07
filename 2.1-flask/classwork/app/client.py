import requests

response = requests.post("http://127.0.0.1:5000/users",
                         json={"name": "user_4", "password": "123fasdfasdfasdf4"},
                         )

print(response.status_code)
print(response.text)

response = requests.get("http://127.0.0.1:5000/users/1",
                        )

print(response.status_code)
print(response.text)

# response = requests.patch("http://127.0.0.1:5000/users/4",
#                           json={"name": "new_name3"},)
#
# print(response.status_code)
# print(response.text)

# response = requests.delete(
#     "http://127.0.0.1:5000/users/4",
# )

# print(response.status_code)
# print(response.text)
