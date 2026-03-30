from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image, ImageStat

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


def assert_image_has_visual_content(image_path: Path) -> None:
    with Image.open(image_path) as image:
        rgb_image = image.convert("RGB")
        stat = ImageStat.Stat(rgb_image)
        assert any(value > 20 for value in stat.var), f"图片纹理过于单一：{image_path}"

        width, height = rgb_image.size
        sample_points = [
            (width // 6, height // 6),
            (width // 2, height // 2),
            (width * 5 // 6, height * 5 // 6),
            (width // 3, height * 2 // 3),
        ]
        sampled_colors = {rgb_image.getpixel(point) for point in sample_points}
        assert len(sampled_colors) >= 2, f"图片采样颜色未形成变化：{image_path}"


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
        image_path = Path("data") / material["local_file_path"]
        thumbnail_path = Path("data") / material["local_thumbnail_path"]
        assert image_path.exists()
        assert thumbnail_path.exists()
        assert_image_has_visual_content(image_path)
        assert_image_has_visual_content(thumbnail_path)

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
