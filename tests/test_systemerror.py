from conftest import auth_headers, login


def test_invalid_access_token_returns_401(client):
    response = client.get(
        "/users/me",
        headers=auth_headers("invalid-token"),
    )
    assert response.status_code == 401
    assert response.json()["message"] == "Token Invalid Or Expired"


def test_missing_club_returns_404(client):
    response = client.get("/clubs/999", headers=auth_headers(login(client)))
    assert response.status_code == 404
    assert response.json()["message"] == "Clb không tồn tại!"
