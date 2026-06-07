import requests

# Test data
test_ad = {
    "title": "Test Advertisement",
    "description": "This is a test ad"
}

# Login first
login_response = requests.post('http://127.0.0.1:5000/login',
                               json={'email': 'user1@example.com', 'password': 'password123'})
print("Login:", login_response.status_code, login_response.json())

# Create ad
create_response = requests.post('http://127.0.0.1:5000/ad',
                                json=test_ad,
                                auth=('user1@example.com', 'password123'))
print("Create Ad:", create_response.status_code, create_response.json())

# Get ad
ad_id = create_response.json().get('id')
if ad_id:
    get_response = requests.get(f'http://127.0.0.1:5000/ad/{ad_id}',
                                auth=('user1@example.com', 'password123'))
    print("Get Ad:", get_response.status_code, get_response.json())

# Update ad
if ad_id:
    patch_response = requests.patch(f'http://127.0.0.1:5000/ad/{ad_id}',
                                    json={'description': 'Updated description'},
                                    auth=('user1@example.com', 'password123'))
    print("Update Ad:", patch_response.status_code, patch_response.json())

# Delete ad
if ad_id:
    delete_response = requests.delete(f'http://127.0.0.1:5000/ad/{ad_id}',
                                      auth=('user1@example.com', 'password123'))
    print("Delete Ad:", delete_response.status_code, delete_response.json())
