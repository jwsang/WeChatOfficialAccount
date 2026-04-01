from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def ensure_ai_config() -> None:
    response = client.put(
        "/api/ai-assist/config",
        json={
            "base_url": "https://mock.ai.local/v1",
            "model": "gpt-site-prefill-test",
            "default_size": "1024x1024",
            "default_quality": "standard",
            "default_style": "vivid",
            "default_count": 2,
            "timeout_seconds": 120,
            "default_negative_prompt": "",
            "api_key": "sk-test-site-prefill-key",
        },
    )
    assert response.status_code == 200


def test_site_crud_flow():
    create_response = client.post(
        "/api/sites",
        json={
            "name": "OpenVerse CRUD",
            "code": "openverse_crud",
            "domain": "api.openverse.org",
            "enabled": True,
            "search_rule": "/v1/images?q={keyword}",
            "parse_rule": "results[].url",
            "page_rule": "page={page}",
            "remark": "默认开放图片站点",
            "crawl_method": "API接口",
            "rule_config": {
                "search_url_template": "/v1/images?q={keyword}&page={page}",
                "result_container_path": "results",
                "image_url_path": "url",
                "source_page_url_path": "foreign_landing_url",
                "title_path": "title",
                "pagination_param": "page",
                "pagination_start": 2,
                "pagination_size_param": "page_size",
                "request_method": "GET",
                "request_headers": {"X-Test": "site"},
                "request_query_template": {"lang": "zh"},
                "extra_notes": "开放图片接口",
            },
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    site_id = created["id"]
    assert created["rule_config"]["search_url_template"] == "/v1/images?q={keyword}&page={page}"
    assert created["rule_config"]["pagination_start"] == 2
    assert created["rule_config"]["request_headers"]["X-Test"] == "site"

    list_response = client.get("/api/sites")
    assert list_response.status_code == 200
    assert any(site["code"] == "openverse_crud" for site in list_response.json())

    update_response = client.put(
        f"/api/sites/{site_id}",
        json={
            "remark": "已更新",
            "enabled": False,
            "rule_config": {
                "search_url_template": "/api/search?kw={keyword}&p={page}",
                "result_container_path": "data.items",
                "image_url_path": "image.url",
                "source_page_url_path": "detail.url",
                "title_path": "meta.title",
                "pagination_param": "p",
                "pagination_start": 1,
                "pagination_size_param": "limit",
                "request_method": "POST",
                "request_headers": {"Authorization": "Bearer demo-token"},
                "request_query_template": {"source": "api"},
                "extra_notes": "已切换为 POST 规则",
            },
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["remark"] == "已更新"
    assert updated["enabled"] is False
    assert updated["rule_config"]["request_method"] == "POST"
    assert updated["rule_config"]["pagination_param"] == "p"
    assert updated["rule_config"]["request_headers"]["Authorization"] == "Bearer demo-token"

    test_response = client.post(
        f"/api/sites/{site_id}/test",
        json={"keyword": "春日花海"},
    )
    assert test_response.status_code == 200
    test_result = test_response.json()
    assert test_result["success"] is True
    assert len(test_result["preview_results"]) == 2
    assert test_result["applied_rule_config"]["request_method"] == "POST"
    assert test_result["applied_rule_config"]["pagination_param"] == "p"
    assert test_result["preview_results"][0]["source_page_url"] == "https://api.openverse.org/api/search?kw=春日花海&p=1"
    assert test_result["preview_results"][1]["source_page_url"] == "https://api.openverse.org/api/search?kw=春日花海&p=2"

    delete_response = client.delete(f"/api/sites/{site_id}")
    assert delete_response.status_code == 204


def test_site_ai_prefill_success(monkeypatch):
    ensure_ai_config()

    def fake_call_ai_site_prefill(self, **kwargs):
        assert kwargs["domain"] == "api.openverse.org"
        return {
            "name": "Openverse 图片",
            "code": "openverse",
            "domain": "api.openverse.org",
            "enabled": "false",
            "search_rule": "",
            "parse_rule": "",
            "page_rule": "",
            "remark": "",
            "crawl_method": "API接口",
            "rule_config": {
                "search_url_template": "/v1/images?q={keyword}&page={page}",
                "result_container_path": "results",
                "image_url_path": "url",
                "source_page_url_path": "foreign_landing_url",
                "title_path": "title",
                "pagination_param": "page",
                "pagination_start": 1,
                "pagination_size_param": "page_size",
                "request_method": "GET",
                "request_headers": {"Accept": "application/json"},
                "request_query_template": {"lang": "zh"},
                "extra_notes": "由测试桩生成",
            },
        }

    monkeypatch.setattr(
        "app.services.site_service.SiteService._call_ai_site_prefill",
        fake_call_ai_site_prefill,
    )

    response = client.post(
        "/api/sites/ai-prefill",
        json={"domain": "https://api.openverse.org/images"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["domain"] == "api.openverse.org"
    assert "人工确认后保存" in body["message"]
    assert body["suggestion"]["domain"] == "api.openverse.org"
    assert body["suggestion"]["enabled"] is False
    assert body["suggestion"]["crawl_method"] == "API接口"
    assert body["suggestion"]["code"].startswith("openverse")
    assert body["suggestion"]["search_rule"] == "GET /v1/images?q={keyword}&page={page}"
    assert body["suggestion"]["parse_rule"].startswith("结果容器: results")
    assert "页码参数: page" in body["suggestion"]["page_rule"]
    assert body["suggestion"]["rule_config"]["request_headers"]["Accept"] == "application/json"


def test_site_ai_prefill_invalid_domain():
    response = client.post(
        "/api/sites/ai-prefill",
        json={"domain": "localhost"},
    )
    assert response.status_code == 400
    assert "有效域名" in response.json()["detail"]
