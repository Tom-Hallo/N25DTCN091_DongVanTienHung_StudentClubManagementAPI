from conftest import auth_headers, login
from app.models.activity import ClubActivity
from test_club import create_club


def test_owner_can_add_and_remove_member(client):
    token = login(client)
    club_id = create_club(client, token)

    add_response = client.post(
        f"/clubs/{club_id}/members",
        headers=auth_headers(token),
        data={"user_id": 2},
    )
    assert add_response.status_code == 201

    remove_response = client.delete(
        f"/clubs/{club_id}/members/2",
        headers=auth_headers(token),
    )
    assert remove_response.status_code == 200


def test_invalid_member_id_returns_validation_error(client):
    token = login(client)
    club_id = create_club(client, token)

    response = client.post(
        f"/clubs/{club_id}/members",
        headers=auth_headers(token),
        data={"user_id": 0},
    )
    assert response.status_code == 422
    assert "greater than or equal to 1" in response.json()["message"]


def test_remove_assignee_keeps_activity_and_unassigns_member(client, db_session):
    owner_token = login(client)
    club_id = create_club(client, owner_token)
    client.post(
        f"/clubs/{club_id}/members",
        headers=auth_headers(owner_token),
        data={"user_id": 2},
    )
    activity = client.post(
        f"/clubs/{club_id}/activities",
        headers=auth_headers(owner_token),
        data={"title": "Assigned activity", "assignee_id": 2},
    )
    assert activity.status_code == 201
    activity_id = activity.json()["data"]["id"]

    response = client.delete(
        f"/clubs/{club_id}/members/2",
        headers=auth_headers(owner_token),
    )
    assert response.status_code == 200

    activity_row = db_session.get(ClubActivity, activity_id)
    assert activity_row is not None
    assert activity_row.assignee_id is None
