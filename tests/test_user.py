from conftest import auth_headers, login


def test_get_current_user(client):
    response = client.get("/users/me", headers=auth_headers(login(client)))
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "owner@example.com"


def test_admin_can_list_users(client):
    response = client.get(
        "/users",
        headers=auth_headers(login(client, "admin@example.com")),
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 3


def test_regular_user_cannot_list_users(client):
    response = client.get("/users", headers=auth_headers(login(client)))
    assert response.status_code == 403
