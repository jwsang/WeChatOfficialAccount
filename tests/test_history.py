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


def ensure_history_site() -> None:
    response = client.post(
        "/api/sites",
        json={
            "name": "HistorySeedSite",
            "code": "history_seed_site",
            "domain": "history.example.com",
            "enabled": True,
            "search_rule": "/search?q={keyword}",
            "parse_rule": "results[].url",
            "page_rule": "page={page}",
            "remark": "历史统计测试站点",
            "crawl_method": "API接口",
        },
    )
    assert response.status_code in (201, 400)


def upload_history_materials() -> list[dict]:
    response = client.post(
        "/api/materials/upload",
        data={
            "title": "历史统计素材",
            "keywords": "历史 统计 发布",
            "remark": "用于历史统计测试",
            "tags": "历史 统计 发布",
        },
        files=[
            ("files", ("history-1.png", build_image_bytes((180, 30, 30)), "image/png")),
            ("files", ("history-2.png", build_image_bytes((30, 180, 30)), "image/png")),
            ("files", ("history-3.png", build_image_bytes((30, 30, 180)), "image/png")),
        ],
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["uploaded"]) == 3
    return body["uploaded"]


def test_history_overview_flow():
    ensure_history_site()

    crawl_response = client.post(
        "/api/crawl-tasks",
        json={
            "keyword": "历史统计专题",
            "target_scope": "selected",
            "target_site_codes": ["history_seed_site"],
            "per_site_limit": 2,
            "max_pages": 1,
            "created_by": "pytest-history",
        },
    )
    assert crawl_response.status_code == 201
    crawl_body = crawl_response.json()
    assert crawl_body["status"] == "completed"
    assert crawl_body["success_count"] >= 1
    assert len(crawl_body["logs"]) >= 1

    materials = upload_history_materials()
    first, second, third = materials

    save_response = client.post(
        "/api/articles/drafts",
        json={
            "title": "历史统计发布样例",
            "summary": "用于验证统计总览与发布记录。",
            "author_name": "Roo",
            "source_url": "https://example.com/history",
            "cover_material_id": first["id"],
            "template_code": "image_gallery",
            "auto_sort": "manual",
            "materials": [
                {"material_id": first["id"], "caption_text": "历史封面"},
                {"material_id": second["id"], "caption_text": "历史正文 1"},
                {"material_id": third["id"], "caption_text": "历史正文 2"},
            ],
        },
    )
    assert save_response.status_code == 201
    draft_id = save_response.json()["id"]

    sync_response = client.post(f"/api/articles/drafts/{draft_id}/sync")
    assert sync_response.status_code == 200
    publish_response = client.post(f"/api/articles/drafts/{draft_id}/publish")
    assert publish_response.status_code == 200

    overview_response = client.get("/api/history/overview")
    assert overview_response.status_code == 200
    overview = overview_response.json()

    assert overview["article_summary"]["total_generated"] >= 1
    assert overview["article_summary"]["total_published"] >= 1
    assert overview["article_summary"]["total_drafts"] >= 0

    assert overview["material_summary"]["total_materials"] >= 4
    assert overview["material_summary"]["unused_materials"] >= 1
    assert overview["material_summary"]["reused_materials"] >= 3
    assert overview["material_summary"]["total_reuse_count"] >= 3

    assert any(item["keyword"] == "历史统计专题" for item in overview["crawl_history"])
    assert any(item["source_site_code"] == "history_seed_site" for item in overview["material_site_stats"])
    assert any(item["tag"] == "历史" for item in overview["material_hot_tags"])
    assert any(item["tag_category_count"] >= 1 for item in overview["material_daily_tags"])

    publish_record = next(item for item in overview["recent_publish_records"] if item["draft_id"] == draft_id)
    assert publish_record["publish_status"] == "success"
    assert publish_record["draft_title"] == "历史统计发布样例"
    assert publish_record["wx_result"]["publish_status"] == "success"

    assert any(item["log_type"] == "crawl" and item["related_id"] == crawl_body["id"] for item in overview["log_center"])
    assert any(item["log_type"] == "publish" and item["related_id"] == draft_id for item in overview["log_center"])
