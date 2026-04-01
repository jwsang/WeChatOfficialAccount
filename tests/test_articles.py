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


def ensure_article_materials(seed: int = 0) -> list[dict]:
    upload_response = client.post(
        "/api/materials/upload",
        data={
            "title": f"组稿素材-{seed}",
            "keywords": f"文章生成 测试 {seed}",
            "remark": f"文章生成测试素材 {seed}",
            "tags": "文章 组稿 测试",
        },
        files=[
            ("files", (f"article-{seed}-1.png", build_image_bytes(((12 + seed) % 255, 120, 220)), "image/png")),
            ("files", (f"article-{seed}-2.png", build_image_bytes((120, (220 + seed) % 255, 12)), "image/png")),
            ("files", (f"article-{seed}-3.png", build_image_bytes((220, 120, (12 + seed) % 255)), "image/png")),
        ],
    )
    assert upload_response.status_code == 200
    uploaded = upload_response.json()["uploaded"]
    assert len(uploaded) == 3
    return uploaded


def test_article_generate_and_save_flow():
    materials = ensure_article_materials(seed=1)
    first, second, third = materials

    preview_response = client.post(
        "/api/articles/preview",
        json={
            "title": "春日花海图集",
            "summary": "适合公众号发布的纯图片欣赏内容。",
            "author_name": "Roo",
            "source_url": "https://example.com/source",
            "cover_material_id": second["id"],
            "template_code": "image_gallery",
            "auto_sort": "manual",
            "materials": [
                {"material_id": second["id"], "caption_text": "第二张作为封面"},
                {"material_id": first["id"], "caption_text": "第一张作为正文"},
                {"material_id": third["id"], "caption_text": "第三张作为结尾"},
            ],
        },
    )
    assert preview_response.status_code == 200
    preview_body = preview_response.json()
    assert preview_body["draft_status"] == "preview"
    assert preview_body["cover_material_id"] == second["id"]
    assert len(preview_body["materials"]) == 3
    assert "春日花海图集" in preview_body["content_html"]
    assert preview_body["publish_payload"]["articles"][0]["template_code"] == "image_gallery"

    before_detail = client.get(f"/api/materials/{first['id']}")
    assert before_detail.status_code == 200
    before_used_count = before_detail.json()["used_count"]

    save_response = client.post(
        "/api/articles/drafts",
        json={
            "title": "春日花海图集",
            "summary": "适合公众号发布的纯图片欣赏内容。",
            "author_name": "Roo",
            "source_url": "https://example.com/source",
            "cover_material_id": second["id"],
            "template_code": "minimal_gallery",
            "auto_sort": "created_desc",
            "materials": [
                {"material_id": first["id"], "caption_text": "第一张作为正文"},
                {"material_id": second["id"], "caption_text": "第二张作为封面"},
                {"material_id": third["id"], "caption_text": "第三张作为结尾"},
            ],
        },
    )
    assert save_response.status_code == 201
    save_body = save_response.json()
    assert save_body["id"] >= 1
    assert save_body["draft_status"] == "editing"
    assert save_body["template_code"] == "minimal_gallery"
    assert len(save_body["materials"]) == 3
    assert save_body["publish_payload"]["articles"][0]["cover_material_id"] == second["id"]

    draft_id = save_body["id"]
    detail_response = client.get(f"/api/articles/drafts/{draft_id}")
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["id"] == draft_id
    assert detail_body["article_title"] == "春日花海图集"
    assert len(detail_body["materials"]) == 3
    assert detail_body["materials"][0]["sort_index"] == 1
    assert "https://example.com/source" in detail_body["content_html"]

    after_detail = client.get(f"/api/materials/{first['id']}")
    assert after_detail.status_code == 200
    assert after_detail.json()["used_count"] == before_used_count + 1


def test_article_draft_box_management_flow(monkeypatch):
    monkeypatch.setattr("app.services.article_service.WechatApiClient.get_access_token", lambda self: "mock_access_token")
    monkeypatch.setattr(
        "app.services.article_service.WechatApiClient.upload_article_image",
        lambda self, access_token, image_path: f"https://mmbiz.qpic.cn/mock/{image_path.stem}",
    )
    monkeypatch.setattr(
        "app.services.article_service.WechatApiClient.upload_permanent_image",
        lambda self, access_token, image_path: f"mock_media_{image_path.stem}",
    )
    monkeypatch.setattr(
        "app.services.article_service.WechatApiClient.add_draft",
        lambda self, access_token, article: "mock_wechat_draft_media_id",
    )
    monkeypatch.setattr(
        "app.services.article_service.WechatApiClient.update_draft",
        lambda self, access_token, media_id, article, index=0: None,
    )
    monkeypatch.setattr(
        "app.services.article_service.WechatApiClient.submit_publish",
        lambda self, access_token, media_id: {"publish_id": "mock_publish_job_id"},
    )
    monkeypatch.setattr(
        "app.services.article_service.WechatApiClient.get_publish_status",
        lambda self, access_token, publish_id: {"publish_status": 0},
    )

    materials = ensure_article_materials(seed=2)
    first, second, third = materials

    save_response = client.post(
        "/api/articles/drafts",
        json={
            "title": "夏日湖畔图文",
            "summary": "用于验证草稿箱管理能力。",
            "author_name": "Roo",
            "source_url": "https://example.com/lake",
            "cover_material_id": first["id"],
            "template_code": "image_gallery",
            "auto_sort": "manual",
            "materials": [
                {"material_id": first["id"], "caption_text": "湖面全景"},
                {"material_id": second["id"], "caption_text": "岸边细节"},
            ],
        },
    )
    assert save_response.status_code == 201
    save_body = save_response.json()
    draft_id = save_body["id"]

    list_response = client.get("/api/articles/drafts")
    assert list_response.status_code == 200
    list_body = list_response.json()
    matched = next(item for item in list_body if item["id"] == draft_id)
    assert matched["material_count"] == 2
    assert matched["cover_material_id"] == first["id"]
    assert matched["cover_local_thumbnail_path"]

    update_response = client.put(
        f"/api/articles/drafts/{draft_id}",
        json={
            "title": "夏日湖畔图文（修订）",
            "summary": "修订后的草稿内容。",
            "author_name": "Roo",
            "source_url": "https://example.com/lake-updated",
            "cover_material_id": third["id"],
            "template_code": "mixed_graphic",
            "auto_sort": "manual",
            "draft_status": "pending_publish",
            "content_html": "<article><h1>自定义正文 HTML</h1><p>用于验证草稿编辑保留自定义内容。</p></article>",
            "materials": [
                {"material_id": third["id"], "caption_text": "修订封面"},
                {"material_id": first["id"], "caption_text": "补充全景"},
                {"material_id": second["id"], "caption_text": "补充细节"},
            ],
        },
    )
    assert update_response.status_code == 200
    update_body = update_response.json()
    assert update_body["article_title"] == "夏日湖畔图文（修订）"
    assert update_body["draft_status"] == "pending_publish"
    assert update_body["template_code"] == "mixed_graphic"
    assert update_body["materials"][0]["material_id"] == third["id"]
    assert "自定义正文 HTML" in update_body["content_html"]
    assert update_body["publish_payload"]["articles"][0]["title"] == "夏日湖畔图文（修订）"

    config_response = client.put(
        "/api/articles/wechat/config",
        json={
            "app_id": "wx_test_appid_123456",
            "app_secret": "wx_test_secret_abcdef",
        },
    )
    assert config_response.status_code == 200
    assert config_response.json()["auth_ready"] is True

    sync_status_response = client.get("/api/articles/wechat/config-status")
    assert sync_status_response.status_code == 200
    assert sync_status_response.json()["auth_ready"] is True

    sync_response = client.post(f"/api/articles/drafts/{draft_id}/sync")
    assert sync_response.status_code == 200
    sync_body = sync_response.json()
    assert sync_body["action"] == "sync"
    assert sync_body["draft"]["wx_draft_id"]
    assert sync_body["draft"]["draft_status"] == "pending_publish"
    assert sync_body["uploaded_material_count"] == 3
    assert sync_body["draft"]["publish_payload"]["articles"][0]["thumb_media_material_id"]

    publish_response = client.post(f"/api/articles/drafts/{draft_id}/publish")
    assert publish_response.status_code == 200
    publish_body = publish_response.json()
    assert publish_body["action"] == "publish"
    assert publish_body["draft"]["wx_draft_id"]
    assert publish_body["draft"]["wx_publish_id"]
    assert publish_body["draft"]["draft_status"] == "published"
    assert publish_body["draft"]["publish_payload"]["wechat_publish_result"]["publish_status"] == "success"

    duplicate_response = client.post(f"/api/articles/drafts/{draft_id}/duplicate")
    assert duplicate_response.status_code == 201
    duplicate_body = duplicate_response.json()
    assert duplicate_body["article_title"].endswith("（副本）")
    assert duplicate_body["draft_status"] == "editing"
    assert len(duplicate_body["materials"]) == 3

    delete_response = client.delete(f"/api/articles/drafts/{draft_id}")
    assert delete_response.status_code == 204

    deleted_detail = client.get(f"/api/articles/drafts/{draft_id}")
    assert deleted_detail.status_code == 404

    final_list_response = client.get("/api/articles/drafts")
    assert final_list_response.status_code == 200
    final_ids = [item["id"] for item in final_list_response.json()]
    assert draft_id not in final_ids
    assert duplicate_body["id"] in final_ids
