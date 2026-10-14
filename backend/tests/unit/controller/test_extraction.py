import json

from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


def test_stream_extracts_without_a_key_and_preserves_quotes() -> None:
    with TestClient(create_app(Settings())) as client:
        response = client.post(
            "/api/v1/extract/stream",
            json={
                "text": "Смартфон Samsung Galaxy S26 Black\nВес: 500 г",
            },
        )
    assert response.status_code == 200
    events = [json.loads(line) for line in response.text.splitlines()]
    assert [e["stage"] for e in events] == ["category", "rules", "complete"]
    assert events[-1]["category_id"] == 761
    weight = next(f for f in events[-1]["fields"] if f["attribute"] == "Вес")
    assert weight["value"] == "0.5 кг"
    assert weight["quote"] == "500 г"


def test_empty_card_is_rejected_before_streaming() -> None:
    with TestClient(create_app(Settings())) as client:
        response = client.post("/api/v1/extract/stream", json={"text": "   "})
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
