"""
图片源适配器模块
提供统一的接口调用不同图片源（官方 API 和通用爬虫）
"""
from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import quote_plus

import httpx


class BaseImageAdapter(ABC):
    """图片源适配器基类"""
    
    @abstractmethod
    def search_images(self, keyword: str, per_page: int = 10) -> list[dict]:
        """搜索图片，返回标准化结果"""
        pass
    
    @property
    @abstractmethod
    def site_code(self) -> str:
        """站点代码"""
        pass
    
    @property
    @abstractmethod
    def site_name(self) -> str:
        """站点名称"""
        pass
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """域名"""
        pass
    
    def _normalize_result(self, title: str, image_url: str, page_url: str) -> dict:
        """标准化结果格式"""
        return {
            "title": title or "Untitled",
            "source_image_url": image_url,
            "source_page_url": page_url or image_url,
            "visual_seed": hash(image_url) % 10000,
        }


class UnsplashAdapter(BaseImageAdapter):
    """Unsplash 官方 API 适配器"""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.base_url = "https://api.unsplash.com"
    
    @property
    def site_code(self) -> str:
        return "unsplash"
    
    @property
    def site_name(self) -> str:
        return "Unsplash"
    
    @property
    def domain(self) -> str:
        return "unsplash.com"
    
    def search_images(self, keyword: str, per_page: int = 10) -> list[dict]:
        """使用 Unsplash API 搜索图片"""
        if not self.api_key:
            raise ValueError("Unsplash API Key is required")
        
        results = []
        safe_keyword = quote_plus(keyword)
        url = f"{self.base_url}/search/photos"
        params = {
            "query": keyword,
            "per_page": min(per_page, 30),  # Unsplash 限制每页最多 30 张
            "orientation": "landscape",
        }
        headers = {
            "Authorization": f"Client-ID {self.api_key}",
            "Accept-Version": "v1",
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                for photo in data.get("results", []):
                    image_url = photo.get("urls", {}).get("regular", "")
                    page_url = photo.get("links", {}).get("html", "")
                    title = photo.get("alt_description", "") or photo.get("description", "")
                    
                    if image_url:
                        results.append(self._normalize_result(title, image_url, page_url))
        except httpx.HTTPError as e:
            print(f"Unsplash API error: {e}")
            raise
        
        return results


class PexelsAdapter(BaseImageAdapter):
    """Pexels 官方 API 适配器"""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/v1"
    
    @property
    def site_code(self) -> str:
        return "pexels"
    
    @property
    def site_name(self) -> str:
        return "Pexels"
    
    @property
    def domain(self) -> str:
        return "pexels.com"
    
    def search_images(self, keyword: str, per_page: int = 10) -> list[dict]:
        """使用 Pexels API 搜索图片"""
        if not self.api_key:
            raise ValueError("Pexels API Key is required")
        
        results = []
        url = f"{self.base_url}/search"
        params = {
            "query": keyword,
            "per_page": min(per_page, 80),  # Pexels 限制每页最多 80 张
            "orientation": "landscape",
        }
        headers = {
            "Authorization": self.api_key,
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                for photo in data.get("photos", []):
                    image_url = photo.get("src", {}).get("large", "")
                    page_url = photo.get("url", "")
                    title = photo.get("alt", "") or photo.get("photographer", "")
                    
                    if image_url:
                        results.append(self._normalize_result(title, image_url, page_url))
        except httpx.HTTPError as e:
            print(f"Pexels API error: {e}")
            raise
        
        return results


class PixabayAdapter(BaseImageAdapter):
    """Pixabay 官方 API 适配器"""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.base_url = "https://pixabay.com/api"
    
    @property
    def site_code(self) -> str:
        return "pixabay"
    
    @property
    def site_name(self) -> str:
        return "Pixabay"
    
    @property
    def domain(self) -> str:
        return "pixabay.com"
    
    def search_images(self, keyword: str, per_page: int = 10) -> list[dict]:
        """使用 Pixabay API 搜索图片"""
        if not self.api_key:
            raise ValueError("Pixabay API Key is required")
        
        results = []
        url = self.base_url
        params = {
            "key": self.api_key,
            "q": keyword,
            "image_type": "photo",
            "orientation": "horizontal",
            "per_page": min(per_page, 200),  # Pixabay 限制每页最多 200 张
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for hit in data.get("hits", []):
                    image_url = hit.get("largeImageURL", "")
                    page_url = hit.get("pageURL", "")
                    title = hit.get("tags", "") or f"{hit.get('user', '')} photo"
                    
                    if image_url:
                        results.append(self._normalize_result(title, image_url, page_url))
        except httpx.HTTPError as e:
            print(f"Pixabay API error: {e}")
            raise
        
        return results


class GenericCrawlAdapter(BaseImageAdapter):
    """通用爬虫适配器（基于 HTML 解析）"""
    
    def __init__(self, site_config: dict):
        """
        初始化通用爬虫适配器
        
        Args:
            site_config: 站点配置字典，包含：
                - code: 站点代码
                - name: 站点名称
                - domain: 域名
                - search_rule: 搜索 URL 规则（支持{keyword}和{page}占位符）
                - rule_config: 解析规则配置（CSS 选择器等）
        """
        self.config = site_config
    
    @property
    def site_code(self) -> str:
        return self.config.get("code", "generic")
    
    @property
    def site_name(self) -> str:
        return self.config.get("name", "Generic Site")
    
    @property
    def domain(self) -> str:
        return self.config.get("domain", "")
    
    def search_images(self, keyword: str, per_page: int = 10) -> list[dict]:
        """使用通用爬虫抓取图片"""
        from bs4 import BeautifulSoup
        
        results = []
        safe_keyword = quote_plus(keyword)
        
        # 构建搜索 URL
        search_rule = self.config.get("search_rule", "/search?q={keyword}")
        search_url = search_rule.replace("{keyword}", safe_keyword).replace("{page}", "1")
        if not search_url.startswith("http"):
            search_url = f"https://{self.domain}{search_url}"
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(search_url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "lxml")
                rule_config = self.config.get("rule_config", {})
                
                # 获取选择器配置
                item_selector = rule_config.get("item_selector", "")
                image_selector = rule_config.get("image_selector", "img[src]")
                title_selector = rule_config.get("title_selector", "")
                link_selector = rule_config.get("link_selector", "a[href]")
                
                if not item_selector:
                    # 直接查找所有图片
                    images = soup.select(image_selector)
                    for img in images[:per_page]:
                        image_url = img.get("src") or img.get("data-src") or ""
                        if image_url:
                            from urllib.parse import urljoin
                            image_url = urljoin(search_url, image_url)
                            title = img.get("alt") or img.get("title") or keyword
                            
                            parent_link = img.find_parent("a")
                            page_url = urljoin(search_url, parent_link.get("href")) if parent_link else search_url
                            
                            results.append(self._normalize_result(title, image_url, page_url))
                else:
                    # 按 item 分组查找
                    items = soup.select(item_selector)
                    for item in items[:per_page]:
                        image_el = item.select_one(image_selector) if image_selector else None
                        if not image_el:
                            continue
                        
                        image_url = image_el.get("src") or image_el.get("data-src") or ""
                        if image_url:
                            from urllib.parse import urljoin
                            image_url = urljoin(search_url, image_url)
                            
                            title = ""
                            if title_selector:
                                title_el = item.select_one(title_selector)
                                title = title_el.get_text(strip=True) if title_el else ""
                            else:
                                title = image_el.get("alt") or image_el.get("title") or keyword
                            
                            page_url = search_url
                            if link_selector:
                                link_el = item.select_one(link_selector)
                                if link_el and link_el.get("href"):
                                    page_url = urljoin(search_url, link_el.get("href"))
                            
                            results.append(self._normalize_result(title, image_url, page_url))
        
        except httpx.HTTPError as e:
            print(f"Generic crawl error for {self.site_code}: {e}")
            raise
        
        return results


def get_adapter(site_code: str, **kwargs) -> BaseImageAdapter:
    """
    工厂函数：根据站点代码获取对应的适配器
    
    Args:
        site_code: 站点代码（unsplash, pexels, pixabay, generic）
        **kwargs: 适配器所需参数（如 api_key, site_config 等）
    
    Returns:
        对应的适配器实例
    """
    adapters = {
        "unsplash": lambda: UnsplashAdapter(kwargs.get("api_key")),
        "pexels": lambda: PexelsAdapter(kwargs.get("api_key")),
        "pixabay": lambda: PixabayAdapter(kwargs.get("api_key")),
        "generic": lambda: GenericCrawlAdapter(kwargs.get("site_config", {})),
    }
    
    if site_code not in adapters:
        raise ValueError(f"Unknown site code: {site_code}. Supported: {list(adapters.keys())}")
    
    return adapters[site_code]()
