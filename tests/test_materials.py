import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


def build_image_bytes(color: tuple[int, int, int]) -> bytes:
    image = Image.new("RGB", (640, 480), color=color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def ensure_material_seed() -> None:
    site_response = client.post(
        "/api/sites",
        json={
            "name": "MaterialSeedSite",
            "code": "material_seed_site",
            "domain": "seed.example.com",
            "enabled": True,
            "search_rule": "/search?q={keyword}",
            "parse_rule": "results[].url",
            "page_rule": "page={page}",
            "remark": "素材库测试站点",
            "crawl_method": "API接口",
        },
    )
    assert site_response.status_code in (201, 400)

    task_response = client.post(
        "/api/crawl-tasks",
        json={
            "keyword": "春日花海",
            "target_scope": "selected",
            "target_site_codes": ["material_seed_site"],
            "per_site_limit": 2,
            "max_pages": 1,
            "created_by": "pytest-material",
        },
    )
    assert task_response.status_code == 201


def test_material_library_flow():
    ensure_material_seed()

    list_response = client.get("/api/materials")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

    search_response = client.get("/api/materials", params={"query_text": "春日花海"})
    assert search_response.status_code == 200
    assert len(search_response.json()) >= 1

    upload_response = client.post(
        "/api/materials/upload",
        data={
            "title": "手动素材",
            "keywords": "本地上传 测试",
            "remark": "手动上传备注",
            "tags": "手动 测试 上传",
        },
        files=[
            ("files", ("manual-1.png", build_image_bytes((255, 0, 0)), "image/png")),
            ("files", ("manual-2.png", build_image_bytes((0, 255, 0)), "image/png")),
        ],
    )
    assert upload_response.status_code == 200
    upload_body = upload_response.json()
    assert len(upload_body["uploaded"]) == 2
    assert upload_body["duplicate_count"] == 0

    first_material_id = upload_body["uploaded"][0]["id"]
    detail_response = client.get(f"/api/materials/{first_material_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["source_type"] == "manual"

    action_response = client.post(
        f"/api/materials/{first_material_id}/actions",
        json={"action": "audit"},
    )
    assert action_response.status_code == 200
    assert action_response.json()["audit_status"] == "approved"

    tag_response = client.get("/api/materials/tags/summary")
    assert tag_response.status_code == 200
    assert any(tag["tag"] == "手动" for tag in tag_response.json())
