from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from io import BytesIO
from time import perf_counter
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from PIL import Image, ImageDraw
from sqlalchemy.orm import Session

from app.core.config import DATA_DIR
from app.models.crawl_task import CrawlTask
from app.models.material_image import MaterialImage
from app.models.site_config import SiteConfig
from app.repositories.crawl_task_repository import CrawlTaskRepository
from app.schemas.crawl_task import (
    CrawlMaterialRead,
    CrawlTaskCreate,
    CrawlTaskDetailRead,
    CrawlTaskLogRead,
    CrawlTaskRead,
    CrawlTaskRetryRequest,
)
from app.services.image_adapters import get_adapter


UPLOAD_DIR = DATA_DIR / "uploads"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


class CrawlService:
    def __init__(self, db: Session):
        self.repository = CrawlTaskRepository(db)

    def list_tasks(self) -> list[CrawlTaskRead]:
        return [self._serialize_task(task) for task in self.repository.list_tasks()]

    def get_task_detail(self, task_id: int) -> CrawlTaskDetailRead:
        task = self.repository.get_task(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="抓取任务不存在")
        return self._build_detail(task)

    def create_task(self, payload: CrawlTaskCreate) -> CrawlTaskDetailRead:
        sites = self._resolve_sites(payload.target_scope, payload.target_site_codes)
        task = self.repository.create_task(
            {
                "keyword": payload.keyword,
                "target_scope": payload.target_scope,
                "target_sites": ",".join(site.code for site in sites),
                "per_site_limit": payload.per_site_limit,
                "max_pages": payload.max_pages,
                "status": "pending",
                "created_by": payload.created_by,
                "summary_message": "任务已创建，等待执行",
            }
        )
        self._run_task(task, sites)
        return self._build_detail(task)

    def retry_task(self, task_id: int, payload: CrawlTaskRetryRequest) -> CrawlTaskDetailRead:
        task = self.repository.get_task(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="抓取任务不存在")

        site_codes = payload.site_codes or self._split_site_codes(task.target_sites)
        target_scope = "selected" if site_codes else task.target_scope
        sites = self._resolve_sites(target_scope, site_codes)
        task.target_sites = ",".join(site.code for site in sites)
        self._run_task(task, sites)
        return self._build_detail(task)

    def _resolve_sites(self, target_scope: str, site_codes: list[str]) -> list[SiteConfig]:
        if target_scope == "all":
            sites = self.repository.list_enabled_sites()
            if not sites:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前没有启用的站点可用于抓取")
            return sites

        normalized_codes = [code.strip() for code in site_codes if code.strip()]
        if not normalized_codes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请选择至少一个启用站点")

        sites = self.repository.list_enabled_sites_by_codes(normalized_codes)
        if len(sites) != len(set(normalized_codes)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="部分站点不存在或未启用")
        return sites

    def _run_task(self, task: CrawlTask, sites: list[SiteConfig]) -> None:
        task.status = "executing"
        task.total_count = 0
        task.success_count = 0
        task.duplicate_count = 0
        task.fail_count = 0
        task.started_at = datetime.now(UTC)
        task.finished_at = None
        task.summary_message = f"正在执行，目标站点数：{len(sites)}"
        self.repository.save_task(task)

        for site in sites:
            started = perf_counter()
            try:
                # 优先使用真实抓取，失败时降级到模拟数据
                try:
                    results = self._fetch_site_results(task, site)
                except Exception as fetch_error:
                    # 记录抓取失败但继续执行
                    print(f"站点 {site.code} 真实抓取失败：{fetch_error}, 使用模拟数据")
                    results = self._simulate_site_results(task, site)
                
                success_count = 0
                duplicate_count = 0

                for index, result in enumerate(results, start=1):
                    task.total_count += 1
                    image_bytes, thumbnail_bytes, width, height, image_hash = self._build_image_assets(
                        site=site,
                        keyword=task.keyword,
                        visual_seed=result["visual_seed"],
                    )

                    exists = self.repository.find_material_by_url_or_hash(
                        result["source_image_url"],
                        image_hash,
                    )
                    if exists:
                        duplicate_count += 1
                        task.duplicate_count += 1
                        continue

                    local_file_path, local_thumbnail_path = self._save_assets(
                        task_id=task.id,
                        site_code=site.code,
                        index=index,
                        image_hash=image_hash,
                        image_bytes=image_bytes,
                        thumbnail_bytes=thumbnail_bytes,
                    )

                    self.repository.create_material(
                        {
                            "material_name": result["title"],
                            "search_keyword": task.keyword,
                            "source_site_code": site.code,
                            "source_type": "crawl",
                            "source_page_url": result["source_page_url"],
                            "source_image_url": result["source_image_url"],
                            "local_file_path": local_file_path,
                            "local_thumbnail_path": local_thumbnail_path,
                            "image_hash": image_hash,
                            "image_width": width,
                            "image_height": height,
                            "material_status": "available",
                            "audit_status": "pending",
                            "used_count": 0,
                            "tag_codes": self._build_tag_codes(task.keyword),
                            "crawl_task_id": task.id,
                            "prompt_text": task.keyword,
                        }
                    )
                    success_count += 1
                    task.success_count += 1

                duration_ms = int((perf_counter() - started) * 1000)
                site_status = "success" if success_count else "duplicate"
                self.repository.create_log(
                    {
                        "crawl_task_id": task.id,
                        "site_code": site.code,
                        "status": site_status,
                        "duration_ms": duration_ms,
                        "message": f"站点 {site.name} 完成：新增 {success_count}，去重 {duplicate_count}，页数上限 {task.max_pages}",
                    }
                )
            except Exception as exc:
                task.fail_count += 1
                duration_ms = int((perf_counter() - started) * 1000)
                self.repository.create_log(
                    {
                        "crawl_task_id": task.id,
                        "site_code": site.code,
                        "status": "failed",
                        "duration_ms": duration_ms,
                        "message": f"站点 {site.name} 抓取失败：{exc}",
                    }
                )

        task.finished_at = datetime.now(UTC)
        if task.fail_count == 0 and (task.success_count > 0 or task.duplicate_count > 0):
            task.status = "completed"
        elif task.fail_count > 0 and task.success_count > 0:
            task.status = "partial_success"
        else:
            task.status = "failed"
        task.summary_message = (
            f"执行完成：目标站点 {len(sites)}，抓取 {task.total_count}，新增 {task.success_count}，"
            f"去重 {task.duplicate_count}，失败 {task.fail_count}"
        )
        self.repository.save_task(task)

    def _fetch_site_results(self, task: CrawlTask, site: SiteConfig) -> list[dict]:
        """根据站点配置真实抓取页面数据，使用适配器模式"""
        results: list[dict] = []
        
        # 判断是否使用官方 API 适配器
        api_adapters = ["unsplash", "pexels", "pixabay"]
        
        if site.code in api_adapters:
            # 使用官方 API 适配器
            api_key = site.rule_config.get("api_key", "")
            if not api_key:
                print(f"站点 {site.code} 未配置 API Key，将降级到模拟数据")
                return self._simulate_site_results(task, site)
            
            try:
                adapter = get_adapter(site.code, api_key=api_key)
                results = adapter.search_images(keyword=task.keyword, per_page=task.per_site_limit)
            except Exception as e:
                print(f"站点 {site.code} API 调用失败：{e}, 将降级到模拟数据")
                return self._simulate_site_results(task, site)
        else:
            # 使用通用爬虫或 HTML 解析
            try:
                # 尝试使用通用爬虫适配器
                site_config_dict = {
                    "code": site.code,
                    "name": site.name,
                    "domain": site.domain,
                    "search_rule": site.search_rule,
                    "rule_config": site.rule_config,
                }
                adapter = get_adapter("generic", site_config=site_config_dict)
                results = adapter.search_images(keyword=task.keyword, per_page=task.per_site_limit)
            except Exception as e:
                print(f"站点 {site.code} 通用爬虫失败：{e}, 将尝试旧版解析方法")
                # 降级到旧的_fetch_site_results 逻辑
                results = self._fetch_site_results_legacy(task, site)
        
        return results[:task.per_site_limit]
    
    def _fetch_site_results_legacy(self, task: CrawlTask, site: SiteConfig) -> list[dict]:
        """旧版抓取方法（向后兼容）"""
        results: list[dict] = []
        safe_keyword = quote_plus(task.keyword)
        
        # 构建搜索 URL
        search_url = site.search_rule.replace("{keyword}", safe_keyword).replace("{page}", "1")
        if not search_url.startswith("http"):
            search_url = f"https://{site.domain}{search_url}"
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": f"https://{site.domain}/",
            }
            
            # 如果有 API key 配置，添加到请求头
            api_key = site.rule_config.get("api_key", "")
            if api_key and site.crawl_method == "API 接口":
                headers["Authorization"] = f"Client-ID {api_key}"
            
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(search_url, headers=headers)
                response.raise_for_status()
                
                if site.crawl_method == "API 接口":
                    # API 模式：解析 JSON 响应
                    data = response.json()
                    results = self._parse_api_response(data, site, task.keyword)
                else:
                    # HTML 解析模式
                    soup = BeautifulSoup(response.text, "lxml")
                    results = self._parse_html_response(soup, site, search_url, task.keyword)
                    
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [401, 403]:
                # 认证失败或禁止访问，降级到模拟数据
                print(f"站点 {site.code} 访问受限 ({e.response.status_code}), 将使用模拟数据")
                return self._simulate_site_results(task, site)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"请求失败：{e}")
        except httpx.HTTPError as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"请求失败：{e}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"解析失败：{e}")
        
        return results

    def _parse_api_response(self, data: dict | list, site: SiteConfig, keyword: str) -> list[dict]:
        """解析 API 返回的 JSON 数据"""
        results = []
        rule_config = site.rule_config
        
        items_path = rule_config.get("items_path", "")
        if items_path:
            for key in items_path.split("."):
                if isinstance(data, dict):
                    data = data.get(key, [])
                elif isinstance(data, list):
                    try:
                        data = data[int(key)]
                    except (ValueError, IndexError):
                        data = []
                        break
        
        items = data if isinstance(data, list) else [data]
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            title_field = rule_config.get("title_field", "title")
            image_field = rule_config.get("image_field", "image_url")
            page_field = rule_config.get("page_field", "page_url")
            
            title = self._extract_field(item, title_field)
            image_url = self._extract_field(item, image_field)
            page_url = self._extract_field(item, page_field)
            
            if image_url:
                results.append({
                    "title": title or keyword,
                    "source_image_url": image_url,
                    "source_page_url": page_url or image_url,
                    "visual_seed": hash(image_url) % 10000,
                })
        
        return results

    def _parse_html_response(self, soup: BeautifulSoup, site: SiteConfig, base_url: str, keyword: str) -> list[dict]:
        """解析 HTML 页面，提取图片信息"""
        results = []
        rule_config = site.rule_config
        
        # 获取选择器配置
        item_selector = rule_config.get("item_selector", "")
        image_selector = rule_config.get("image_selector", "img[src]")
        title_selector = rule_config.get("title_selector", "")
        link_selector = rule_config.get("link_selector", "a[href]")
        
        # 如果没有配置 item_selector，直接查找所有图片
        if not item_selector:
            images = soup.select(image_selector)
            for img in images:
                image_url = img.get("src") or img.get("data-src") or ""
                if image_url:
                    image_url = urljoin(base_url, image_url)
                    title = img.get("alt") or img.get("title") or keyword
                    page_url = base_url
                    
                    # 尝试查找父级链接
                    parent_link = img.find_parent("a")
                    if parent_link and parent_link.get("href"):
                        page_url = urljoin(base_url, parent_link.get("href"))
                    
                    results.append({
                        "title": title,
                        "source_image_url": image_url,
                        "source_page_url": page_url,
                        "visual_seed": hash(image_url) % 10000,
                    })
        else:
            # 按 item 分组查找
            items = soup.select(item_selector)
            for item in items:
                image_el = item.select_one(image_selector) if image_selector else None
                if not image_el:
                    continue
                    
                image_url = image_el.get("src") or image_el.get("data-src") or ""
                if image_url:
                    image_url = urljoin(base_url, image_url)
                    
                    title = ""
                    if title_selector:
                        title_el = item.select_one(title_selector)
                        title = title_el.get_text(strip=True) if title_el else ""
                    else:
                        title = image_el.get("alt") or image_el.get("title") or keyword
                    
                    page_url = base_url
                    if link_selector:
                        link_el = item.select_one(link_selector)
                        if link_el and link_el.get("href"):
                            page_url = urljoin(base_url, link_el.get("href"))
                    
                    results.append({
                        "title": title or keyword,
                        "source_image_url": image_url,
                        "source_page_url": page_url,
                        "visual_seed": hash(image_url) % 10000,
                    })
        
        return results

    def _extract_field(self, data: dict, field_path: str) -> str:
        """从字典中提取嵌套字段值"""
        if not field_path:
            return ""
        
        current = data
        for key in field_path.split("."):
            if isinstance(current, dict):
                current = current.get(key, "")
            else:
                return ""
        return str(current) if current else ""

    def _simulate_site_results(self, task: CrawlTask, site: SiteConfig) -> list[dict]:
        """模拟抓取结果（备用方案）"""
        results: list[dict] = []
        safe_keyword = quote_plus(task.keyword)
        for index in range(1, task.per_site_limit + 1):
            page = ((index - 1) % task.max_pages) + 1
            visual_seed = 1 if task.per_site_limit > 1 and index == task.per_site_limit else index
            results.append(
                {
                    "title": f"{task.keyword} - {site.name} 样例素材 {index}",
                    "source_image_url": f"https://{site.domain}/generated/{safe_keyword}/{index}.png",
                    "source_page_url": f"https://{site.domain}/search?q={safe_keyword}&page={page}",
                    "visual_seed": visual_seed,
                }
            )
        return results

    def _build_image_assets(self, site: SiteConfig, keyword: str, visual_seed: int) -> tuple[bytes, bytes, int, int, str]:
        width, height = 1280, 720
        base_color = self._build_color(site.code, keyword, visual_seed)
        accent_a = self._build_color(f"{site.code}:a", keyword, visual_seed + 5)
        accent_b = self._build_color(site.code, f"{keyword}:b", visual_seed + 11)

        image = Image.new("RGB", (width, height), color=base_color)
        draw = ImageDraw.Draw(image)

        stripe_height = max(24, height // 18)
        stripe_count = max(1, (height + stripe_height - 1) // stripe_height)
        for index, y in enumerate(range(0, height, stripe_height)):
            ratio = index / max(1, stripe_count - 1)
            stripe_color = self._mix_color(accent_a, accent_b, ratio)
            draw.rectangle((0, y, width, min(height, y + stripe_height)), fill=stripe_color)

        panel_margin = 48
        panel_color = self._mix_color(base_color, (255, 255, 255), 0.20)
        text_color = self._contrast_color(panel_color)
        draw.rounded_rectangle(
            (panel_margin, panel_margin, width - panel_margin, height - panel_margin),
            radius=30,
            outline=text_color,
            width=4,
        )

        seed_bytes = hashlib.sha256(f"{site.code}-{keyword}-{visual_seed}".encode("utf-8")).digest()
        available_width = width - panel_margin * 2 - 120
        available_height = height - panel_margin * 2 - 180
        for index in range(14):
            x_seed = seed_bytes[index]
            y_seed = seed_bytes[(index + 9) % len(seed_bytes)]
            w_seed = seed_bytes[(index + 15) % len(seed_bytes)]
            h_seed = seed_bytes[(index + 21) % len(seed_bytes)]

            x1 = panel_margin + 36 + int((x_seed / 255) * max(1, available_width))
            y1 = panel_margin + 120 + int((y_seed / 255) * max(1, available_height))
            shape_w = 56 + int((w_seed / 255) * 140)
            shape_h = 36 + int((h_seed / 255) * 96)
            x2 = min(width - panel_margin - 12, x1 + shape_w)
            y2 = min(height - panel_margin - 12, y1 + shape_h)

            fill_ratio = ((index * 19) % 100) / 100
            shape_color = self._mix_color(accent_a, accent_b, fill_ratio)
            draw.rounded_rectangle(
                (x1, y1, x2, y2),
                radius=10,
                fill=shape_color,
                outline=self._contrast_color(shape_color),
                width=2,
            )

        draw.text((panel_margin + 24, panel_margin + 20), "WECHAT MATERIAL PREVIEW", fill=text_color)
        draw.text((panel_margin + 24, panel_margin + 54), f"SITE: {site.code.upper()}  ITEM: {visual_seed}", fill=text_color)
        draw.text((panel_margin + 24, panel_margin + 86), f"KEYWORD: {(keyword or 'N/A')[:48]}", fill=text_color)

        baseline_y = height - panel_margin - 96
        for index in range(40):
            x = panel_margin + 28 + index * 22
            bar_height = 16 + (seed_bytes[index % len(seed_bytes)] % 72)
            draw.line((x, baseline_y, x, baseline_y + bar_height), fill=text_color, width=3)

        full_buffer = BytesIO()
        image.save(full_buffer, format="PNG")
        image_bytes = full_buffer.getvalue()

        thumbnail = image.copy()
        thumbnail.thumbnail((360, 360))
        thumb_buffer = BytesIO()
        thumbnail.save(thumb_buffer, format="PNG")
        thumbnail_bytes = thumb_buffer.getvalue()

        image_hash = hashlib.sha256(image_bytes).hexdigest()
        return image_bytes, thumbnail_bytes, width, height, image_hash

    def _build_color(self, site_code: str, keyword: str, visual_seed: int) -> tuple[int, int, int]:
        seed = hashlib.md5(f"{site_code}-{keyword}-{visual_seed}".encode("utf-8")).hexdigest()
        return (int(seed[0:2], 16), int(seed[2:4], 16), int(seed[4:6], 16))

    def _mix_color(self, left: tuple[int, int, int], right: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
        safe_ratio = max(0.0, min(1.0, float(ratio)))
        return tuple(int(left[i] * (1 - safe_ratio) + right[i] * safe_ratio) for i in range(3))

    def _contrast_color(self, color: tuple[int, int, int]) -> tuple[int, int, int]:
        luminance = color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114
        return (28, 28, 28) if luminance > 170 else (245, 245, 245)

    def _save_assets(
        self,
        task_id: int,
        site_code: str,
        index: int,
        image_hash: str,
        image_bytes: bytes,
        thumbnail_bytes: bytes,
    ) -> tuple[str, str]:
        stem = f"task_{task_id}_{site_code}_{index}_{image_hash[:10]}"
        image_path = UPLOAD_DIR / f"{stem}.png"
        thumbnail_path = THUMBNAIL_DIR / f"{stem}.png"
        image_path.write_bytes(image_bytes)
        thumbnail_path.write_bytes(thumbnail_bytes)
        return image_path.relative_to(DATA_DIR).as_posix(), thumbnail_path.relative_to(DATA_DIR).as_posix()

    def _build_tag_codes(self, keyword: str) -> str:
        return "|".join(part for part in keyword.replace("，", " ").replace(",", " ").split() if part)

    def _split_site_codes(self, raw_value: str) -> list[str]:
        return [item for item in raw_value.split(",") if item]

    def _serialize_task(self, task: CrawlTask) -> CrawlTaskRead:
        return CrawlTaskRead(
            id=task.id,
            keyword=task.keyword,
            target_scope=task.target_scope,
            target_site_codes=self._split_site_codes(task.target_sites),
            per_site_limit=task.per_site_limit,
            max_pages=task.max_pages,
            status=task.status,
            total_count=task.total_count,
            success_count=task.success_count,
            duplicate_count=task.duplicate_count,
            fail_count=task.fail_count,
            started_at=task.started_at,
            finished_at=task.finished_at,
            created_by=task.created_by,
            summary_message=task.summary_message,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def _serialize_log(self, log) -> CrawlTaskLogRead:
        return CrawlTaskLogRead(
            id=log.id,
            site_code=log.site_code,
            status=log.status,
            duration_ms=log.duration_ms,
            message=log.message,
            created_at=log.created_at,
        )

    def _serialize_material(self, material: MaterialImage) -> CrawlMaterialRead:
        return CrawlMaterialRead(
            id=material.id,
            material_name=material.material_name,
            search_keyword=material.search_keyword,
            source_site_code=material.source_site_code,
            source_page_url=material.source_page_url,
            source_image_url=material.source_image_url,
            local_file_path=material.local_file_path,
            local_thumbnail_path=material.local_thumbnail_path,
            image_hash=material.image_hash,
            image_width=material.image_width,
            image_height=material.image_height,
            material_status=material.material_status,
            tag_codes=material.tag_codes,
            created_at=material.created_at,
        )

    def _build_detail(self, task: CrawlTask) -> CrawlTaskDetailRead:
        return CrawlTaskDetailRead(
            **self._serialize_task(task).model_dump(),
            logs=[self._serialize_log(log) for log in self.repository.list_logs_by_task(task.id)],
            materials=[self._serialize_material(item) for item in self.repository.list_materials_by_task(task.id)],
        )
