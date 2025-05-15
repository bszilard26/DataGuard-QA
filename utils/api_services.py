import requests

class UserService:
    BASE_URL = "https://jsonplaceholder.typicode.com"

    def list_users(self):
        return requests.get(f"{self.BASE_URL}/users")
