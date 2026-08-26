from conftest import auth_headers, login


def test_register_and_login(client):
    register = client.post(
        "/auth/register",
        data={
            "email": "new@example.com",
            "full_name": "New User",
            "password": "password123",
        },
    )
    assert register.status_code == 201
    assert register.json()["data"]["email"] == "new@example.com"

    token = login(client, "new@example.com")
    assert token


def test_login_with_wrong_password_returns_400(client):
    response = client.post(
        "/auth/login",
        data={"email": "owner@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Email hoặc mật khẩu không chính xác"


def test_protected_endpoint_requires_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401
