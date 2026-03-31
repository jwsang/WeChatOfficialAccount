from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


DEFAULT_PASSWORD = "123456"
TEMP_PASSWORD = "Temp@1234"
ALT_PASSWORD = "Admin@1234"
PROTECTED_PAGES = (
    "/",
    "/sites",
    "/crawl",
    "/materials",
    "/articles",
    "/drafts",
    "/history",
    "/account",
)


def login(password: str):
    return client.post(
        "/api/auth/login",
        json={"username": "admin", "password": password},
    )


def ensure_admin_logged_in() -> str:
    for candidate in (DEFAULT_PASSWORD, TEMP_PASSWORD, ALT_PASSWORD):
        response = login(candidate)
        if response.status_code == 200:
            return candidate
    raise AssertionError("无法使用预置密码登录 admin 账号")


def test_auth_login_profile_password_and_pages_flow():
    for path in PROTECTED_PAGES:
        redirect = client.get(path, follow_redirects=False)
        assert redirect.status_code == 303
        assert redirect.headers.get("location") == "/login"

    login_page = client.get("/login")
    assert login_page.status_code == 200
    assert "账号登录" in login_page.text
    assert "login-hero" in login_page.text
    assert 'id="topbar-user-name"' not in login_page.text

    unauthorized_me = client.get("/api/auth/me")
    assert unauthorized_me.status_code == 401

    current_password = ensure_admin_logged_in()

    login_redirect_when_authenticated = client.get("/login", follow_redirects=False)
    assert login_redirect_when_authenticated.status_code == 303
    assert login_redirect_when_authenticated.headers.get("location") == "/"

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    profile = me.json()
    assert profile["username"] == "admin"

    account_page = client.get("/account")
    assert account_page.status_code == 200
    assert "账号设置" in account_page.text

    for path in PROTECTED_PAGES:
        page = client.get(path)
        assert page.status_code == 200
        assert 'id="topbar-user-trigger"' in page.text
        assert 'id="topbar-user-menu"' in page.text
        assert 'id="topbar-logout-button"' in page.text
        assert 'id="sidebar-user-name"' not in page.text
        assert 'id="sidebar-login-link"' not in page.text
        assert 'id="sidebar-logout-button"' not in page.text

    profile_update = client.put(
        "/api/auth/profile",
        json={"username": "admin", "display_name": "系统管理员测试"},
    )
    assert profile_update.status_code == 200
    assert profile_update.json()["display_name"] == "系统管理员测试"

    next_password = TEMP_PASSWORD if current_password != TEMP_PASSWORD else ALT_PASSWORD
    reset_ok = client.post(
        "/api/auth/password/reset",
        json={"old_password": current_password, "new_password": next_password},
    )
    assert reset_ok.status_code == 200, reset_ok.text

    logout_ok = client.post("/api/auth/logout")
    assert logout_ok.status_code == 204

    for path in PROTECTED_PAGES:
        redirect_after_logout = client.get(path, follow_redirects=False)
        assert redirect_after_logout.status_code == 303
        assert redirect_after_logout.headers.get("location") == "/login"

    old_login = login(current_password)
    assert old_login.status_code == 401

    new_login = login(next_password)
    assert new_login.status_code == 200

    final_password = TEMP_PASSWORD if next_password != TEMP_PASSWORD else ALT_PASSWORD
    reset_back = client.post(
        "/api/auth/password/reset",
        json={"old_password": next_password, "new_password": final_password},
    )
    assert reset_back.status_code == 200

    restore_profile = client.put(
        "/api/auth/profile",
        json={"username": "admin", "display_name": "系统管理员"},
    )
    assert restore_profile.status_code == 200

    final_logout = client.post("/api/auth/logout")
    assert final_logout.status_code == 204

    final_login = login(final_password)
    assert final_login.status_code == 200
