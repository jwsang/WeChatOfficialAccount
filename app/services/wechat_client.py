from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException, status


class WechatApiClient:
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"

    def __init__(self, app_id: str, app_secret: str, timeout: float = 20.0):
        self.app_id = app_id
        self.app_secret = app_secret
        self.timeout = timeout

    def get_access_token(self) -> str:
        payload = self._request_json(
            "GET",
            "/token",
            params={
                "grant_type": "client_credential",
                "appid": self.app_id,
                "secret": self.app_secret,
            },
        )
        access_token = str(payload.get("access_token") or "").strip()
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="微信 access_token 获取失败：返回中缺少 access_token",
            )
        return access_token

    def upload_article_image(self, access_token: str, image_path: Path) -> str:
        payload = self._upload_file(
            "/media/uploadimg",
            access_token=access_token,
            image_path=image_path,
        )
        image_url = str(payload.get("url") or "").strip()
        if not image_url:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="微信正文图片上传失败：返回中缺少 url",
            )
        return image_url

    def upload_permanent_image(self, access_token: str, image_path: Path) -> str:
        payload = self._upload_file(
            "/material/add_material",
            access_token=access_token,
            image_path=image_path,
            extra_params={"type": "image"},
        )
        media_id = str(payload.get("media_id") or "").strip()
        if not media_id:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="微信封面素材上传失败：返回中缺少 media_id",
            )
        return media_id

    def add_draft(self, access_token: str, article: dict[str, Any]) -> str:
        payload = self._request_json(
            "POST",
            "/draft/add",
            params={"access_token": access_token},
            json_body={"articles": [article]},
        )
        media_id = str(payload.get("media_id") or "").strip()
        if not media_id:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="微信草稿创建失败：返回中缺少 media_id",
            )
        return media_id

    def update_draft(self, access_token: str, media_id: str, article: dict[str, Any], index: int = 0) -> None:
        self._request_json(
            "POST",
            "/draft/update",
            params={"access_token": access_token},
            json_body={
                "media_id": media_id,
                "index": index,
                "articles": article,
            },
        )

    def submit_publish(self, access_token: str, media_id: str) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/freepublish/submit",
            params={"access_token": access_token},
            json_body={"media_id": media_id},
        )

    def get_publish_status(self, access_token: str, publish_id: str) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/freepublish/get",
            params={"access_token": access_token},
            json_body={"publish_id": publish_id},
        )

    def _upload_file(
        self,
        endpoint: str,
        *,
        access_token: str,
        image_path: Path,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        media_type, _ = mimetypes.guess_type(image_path.name)
        binary = image_path.read_bytes()
        files = {
            "media": (
                image_path.name,
                binary,
                media_type or "application/octet-stream",
            )
        }
        params = {"access_token": access_token}
        if extra_params:
            params.update(extra_params)
        return self._request_json(
            "POST",
            endpoint,
            params=params,
            files=files,
        )

    def _request_json(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        files: dict[str, tuple[str, bytes, str]] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_body,
                    files=files,
                )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"调用微信接口失败：{exc}",
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="微信接口返回非 JSON 数据",
            ) from exc

        if not response.is_success:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"微信接口 HTTP {response.status_code}：{payload}",
            )

        if isinstance(payload, dict):
            errcode = payload.get("errcode")
            if errcode not in (None, 0, "0"):
                errmsg = payload.get("errmsg") or "unknown"
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"微信接口错误[{errcode}]：{errmsg}",
                )
            return payload

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="微信接口返回结构异常",
        )
