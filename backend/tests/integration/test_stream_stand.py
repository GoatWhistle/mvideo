import json
import os

import httpx


def test_running_stand_streams_real_fields_without_a_paid_model() -> None:
    base = os.environ.get("TEST_API_URL")
    assert base, "Set TEST_API_URL to the stand started with DECISION_MODEL=lexical"
    with httpx.stream(
        "POST",
        f"{base}/api/v1/extract/stream",
        timeout=20,
        json={
            "text": "Смартфон Samsung Galaxy S26 12/256GB Black\nВес: 500 г",
        },
    ) as response:
        assert response.status_code == 200
        assert "application/jsonl" in response.headers["content-type"]
        events = [json.loads(line) for line in response.iter_lines() if line]
    assert [event["stage"] for event in events] == ["category", "rules", "complete"]
    final = events[-1]
    assert final["model_calls"] == 0
    assert final["category_id"] == 761
    fields = {field["attribute"]: field for field in final["fields"]}
    assert fields["Вес"]["value"] == "0.5 кг"
    assert fields["Оперативная память (RAM)"]["quote"] == "12/256GB"
    for field in final["fields"]:
        if field["state"] == "accepted":
            assert final["source_text"][field["start"] : field["end"]] == field["quote"]
            assert field["confidence"] is None
