from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_site(name: str, code: str, domain: str):
    response = client.post(
        "/api/sites",
        json={
            "name": name,
            "code": code,
            "domain": domain,
            "enabled": True,
            "search_rule": "/search?q={keyword}",
            "parse_rule": "results[].url",
            "page_rule": "page={page}",
            "remark": f"{name} 默认测试站点",
            "crawl_method": "API接口",
        },
    )
    assert response.status_code == 201


def test_crawl_task_flow():
    create_site("OpenVerse", "openverse", "api.openverse.org")
    create_site("Wikimedia", "wikimedia", "commons.wikimedia.org")

    create_response = client.post(
        "/api/crawl-tasks",
        json={
            "keyword": "春日花海",
            "target_scope": "selected",
            "target_site_codes": ["openverse", "wikimedia"],
            "per_site_limit": 3,
            "max_pages": 2,
            "created_by": "pytest",
        },
    )
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["status"] == "completed"
    assert body["total_count"] == 6
    assert body["success_count"] == 4
    assert body["duplicate_count"] == 2
    assert len(body["logs"]) == 2
    assert len(body["materials"]) == 4

    for material in body["materials"]:
        assert (Path("data") / material["local_file_path"]).exists()
        assert (Path("data") / material["local_thumbnail_path"]).exists()

    task_id = body["id"]
    detail_response = client.get(f"/api/crawl-tasks/{task_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == task_id

    retry_response = client.post(f"/api/crawl-tasks/{task_id}/retry", json={"site_codes": []})
    assert retry_response.status_code == 200
    retry_body = retry_response.json()
    assert retry_body["status"] == "completed"
    assert retry_body["total_count"] == 6
    assert retry_body["duplicate_count"] == 6
    assert len(retry_body["materials"]) == 4
