from utils.api_services import UserService

def test_list_users():
    service = UserService()
    response = service.list_users()

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
