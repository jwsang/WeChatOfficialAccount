from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime

from app.models.user_account import UserAccount
from app.repositories.user_repository import UserRepository


class UserService:
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "123456"

    def __init__(self, db):
        self.repository = UserRepository(db)

    def ensure_default_admin(self) -> UserAccount:
        user = self.repository.get_by_username(self.DEFAULT_ADMIN_USERNAME)
        if user:
            return user

        return self.repository.create(
            {
                "username": self.DEFAULT_ADMIN_USERNAME,
                "password_hash": self.hash_password(self.DEFAULT_ADMIN_PASSWORD),
                "display_name": "系统管理员",
                "role": "admin",
                "is_active": True,
            }
        )

    def get_user_by_id(self, user_id: int) -> UserAccount | None:
        return self.repository.get_by_id(user_id)

    def authenticate(self, username: str, password: str) -> UserAccount | None:
        user = self.repository.get_by_username(username.strip())
        if not user or not user.is_active:
            return None
        if not self.verify_password(password, user.password_hash):
            return None

        user.last_login_at = datetime.now(UTC)
        return self.repository.save(user)

    def update_profile(self, user_id: int, username: str, display_name: str) -> UserAccount:
        user = self._require_user(user_id)
        normalized_username = username.strip()
        normalized_display_name = display_name.strip()

        if len(normalized_username) < 3:
            raise ValueError("用户名至少 3 个字符。")
        if len(normalized_display_name) < 2:
            raise ValueError("显示名称至少 2 个字符。")

        if normalized_username != user.username:
            exists = self.repository.get_by_username(normalized_username)
            if exists and exists.id != user.id:
                raise ValueError("用户名已存在，请更换后重试。")

        user.username = normalized_username
        user.display_name = normalized_display_name
        return self.repository.save(user)

    def reset_password(self, user_id: int, old_password: str, new_password: str) -> UserAccount:
        user = self._require_user(user_id)

        if not self.verify_password(old_password, user.password_hash):
            raise ValueError("原密码不正确。")
        if len(new_password) < 6:
            raise ValueError("新密码长度至少 6 位。")
        if old_password == new_password:
            raise ValueError("新密码不能与原密码相同。")

        user.password_hash = self.hash_password(new_password)
        return self.repository.save(user)

    def to_public(self, user: UserAccount) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
            "is_active": user.is_active,
            "last_login_at": user.last_login_at,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    def _require_user(self, user_id: int) -> UserAccount:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在。")
        return user

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16).hex()
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120000).hex()
        return f"{salt}${digest}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            salt, expected = password_hash.split("$", 1)
        except ValueError:
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120000).hex()
        return digest == expected
