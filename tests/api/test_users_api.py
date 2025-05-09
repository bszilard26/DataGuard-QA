import requests

def test_list_users():
    response = requests.get("https://jsonplaceholder.typicode.com/users")
    assert response.status_code == 200
    assert len(response.json()) > 0
