from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import Item


def create_item(client: TestClient, name: str = "Widget", **fields: object) -> dict:
    response = client.post("/api/items", json={"name": name, **fields})
    assert response.status_code == 201, response.text
    return response.json()


def test_create_item(client: TestClient) -> None:
    item = create_item(client, "Widget", description="A useful widget")

    assert item["id"] > 0
    assert item["name"] == "Widget"
    assert item["description"] == "A useful widget"
    assert item["created_at"] and item["updated_at"]


def test_create_item_with_duplicate_name_returns_409(client: TestClient) -> None:
    create_item(client, "Widget")

    response = client.post("/api/items", json={"name": "Widget"})

    assert response.status_code == 409


def test_create_item_validates_input(client: TestClient) -> None:
    assert client.post("/api/items", json={"name": ""}).status_code == 422
    assert client.post("/api/items", json={"name": "x" * 101}).status_code == 422
    assert client.post("/api/items", json={}).status_code == 422


def test_get_item(client: TestClient) -> None:
    created = create_item(client)

    response = client.get(f"/api/items/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_item_returns_404(client: TestClient) -> None:
    assert client.get("/api/items/999999999").status_code == 404


def test_list_items_is_ordered_and_paginated(client: TestClient, db_session: Session) -> None:
    # Tests share the dev database; clear the table (rolled back after the test) so
    # existing dev rows don't affect the result.
    db_session.execute(delete(Item))
    ids = [create_item(client, f"Item {i}")["id"] for i in range(3)]

    first_page = client.get("/api/items", params={"limit": 2}).json()
    second_page = client.get("/api/items", params={"limit": 2, "offset": 2}).json()

    assert [item["id"] for item in first_page] == ids[:2]
    assert [item["id"] for item in second_page] == ids[2:]


def test_list_items_rejects_out_of_range_limit(client: TestClient) -> None:
    assert client.get("/api/items", params={"limit": 0}).status_code == 422
    assert client.get("/api/items", params={"limit": 101}).status_code == 422


def test_update_item_changes_only_sent_fields(client: TestClient) -> None:
    created = create_item(client, "Widget", description="Original")

    response = client.patch(f"/api/items/{created['id']}", json={"name": "Gadget"})

    assert response.status_code == 200
    assert response.json()["name"] == "Gadget"
    assert response.json()["description"] == "Original"


def test_update_item_can_clear_description(client: TestClient) -> None:
    created = create_item(client, "Widget", description="Original")

    response = client.patch(f"/api/items/{created['id']}", json={"description": None})

    assert response.json()["description"] is None


def test_update_item_rejects_null_name(client: TestClient) -> None:
    created = create_item(client)

    response = client.patch(f"/api/items/{created['id']}", json={"name": None})

    assert response.status_code == 422


def test_update_item_to_duplicate_name_returns_409(client: TestClient) -> None:
    create_item(client, "Widget")
    other = create_item(client, "Gadget")

    response = client.patch(f"/api/items/{other['id']}", json={"name": "Widget"})

    assert response.status_code == 409


def test_update_missing_item_returns_404(client: TestClient) -> None:
    assert client.patch("/api/items/999999999", json={"name": "x"}).status_code == 404


def test_delete_item(client: TestClient) -> None:
    created = create_item(client)

    response = client.delete(f"/api/items/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/items/{created['id']}").status_code == 404


def test_delete_missing_item_returns_404(client: TestClient) -> None:
    assert client.delete("/api/items/999999999").status_code == 404
