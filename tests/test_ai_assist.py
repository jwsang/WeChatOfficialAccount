import io
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import DATA_DIR
from app.main import app


client = TestClient(app)


def build_image_bytes(color: tuple[int, int, int]) -> bytes:
    image = Image.new("RGB", (640, 480), color=color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def ensure_ai_config() -> None:
    response = client.put(
        "/api/ai-assist/config",
        json={
            "base_url": "https://mock.ai.local/v1",
            "model": "gpt-image-test",
            "default_size": "1024x1024",
            "default_quality": "standard",
            "default_style": "vivid",
            "default_count": 4,
            "timeout_seconds": 120,
            "default_negative_prompt": "",
            "api_key": "sk-test-ai-assist-key",
        },
    )
    assert response.status_code == 200


def test_ai_assist_config_and_generate_material_flow(monkeypatch):
    ensure_ai_config()

    config_response = client.get("/api/ai-assist/config")
    assert config_response.status_code == 200
    config_body = config_response.json()
    assert config_body["model"] == "gpt-image-test"
    assert config_body["has_api_key"] is True
    assert "*" in config_body["api_key_masked"]

    async def fake_call_image_api(self, **kwargs):
        return [build_image_bytes((255, 0, 0)), build_image_bytes((0, 255, 0))]

    monkeypatch.setattr(
        "app.services.ai_assist_service.AiAssistService._call_image_api",
        fake_call_image_api,
    )

    generate_response = client.post(
        "/api/ai-assist/generate",
        data={
            "prompt": "清新风格海报",
            "negative_prompt": "低清晰度",
            "count": "2",
            "size": "1024x1024",
            "quality": "standard",
            "style": "vivid",
        },
    )
    assert generate_response.status_code == 200
    generated = generate_response.json()["generated"]
    assert len(generated) == 2

    temp_ids = [item["temp_id"] for item in generated]
    for item in generated:
        local_path = Path(DATA_DIR / item["local_file_path"])
        assert local_path.exists()

    add_material_response = client.post(
        "/api/ai-assist/materials",
        json={
            "temp_ids": temp_ids,
            "title_prefix": "AI测试素材",
            "keywords": "AI 测试",
            "tags": "AI|测试",
            "remark": "pytest 自动入库",
        },
    )
    assert add_material_response.status_code == 200
    material_body = add_material_response.json()
    assert len(material_body["uploaded"]) == 2
    assert material_body["duplicate_count"] == 0
    assert material_body["missing_count"] == 0
    assert all(item["source_type"] == "ai" for item in material_body["uploaded"])
    assert all(item["audit_status"] == "approved" for item in material_body["uploaded"])


def test_ai_assist_generate_with_reference_image(monkeypatch):
    ensure_ai_config()
    tracker = {"has_reference": False}

    async def fake_call_image_api(self, **kwargs):
        tracker["has_reference"] = bool(kwargs.get("reference_image_bytes"))
        return [build_image_bytes((10, 20, 30))]

    monkeypatch.setattr(
        "app.services.ai_assist_service.AiAssistService._call_image_api",
        fake_call_image_api,
    )

    response = client.post(
        "/api/ai-assist/generate",
        data={
            "prompt": "参考图重绘",
            "negative_prompt": "",
            "count": "1",
            "size": "1024x1024",
            "quality": "standard",
            "style": "vivid",
        },
        files={
            "reference_image": ("reference.png", build_image_bytes((100, 100, 220)), "image/png"),
        },
    )
    assert response.status_code == 200
    assert len(response.json()["generated"]) == 1
    assert tracker["has_reference"] is True
