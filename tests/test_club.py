from conftest import auth_headers, login


def create_club(client, token):
    response = client.post(
        "/clubs",
        headers=auth_headers(token),
        data={"name": "Test Club", "description": "Club for tests"},
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def test_owner_can_create_and_list_club(client):
    token = login(client)
    club_id = create_club(client, token)

    response = client.get("/clubs", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == club_id


def test_non_member_cannot_view_club(client):
    owner_token = login(client)
    club_id = create_club(client, owner_token)
    member_token = login(client, "member@example.com")

    response = client.get(f"/clubs/{club_id}", headers=auth_headers(member_token))
    assert response.status_code == 403
