# 爬虫模块使用说明

## 功能概述

爬虫模块已更新为支持真实的 URL 解析和页面抓取功能，主要包括：

1. **真实网页抓取**：使用 httpx 进行网络请求
2. **HTML 解析**：使用 BeautifulSoup + lxml 解析 HTML 页面
3. **API 接口支持**：支持 JSON API 数据解析
4. **智能降级**：当网站访问受限时自动降级到模拟数据

## 新增依赖

```
beautifulsoup4>=4.12.0
lxml>=5.0.0
```

## 配置站点

在数据库的 `site_configs` 表中配置站点信息：

### 字段说明

- `name`: 站点名称
- `code`: 站点代码（唯一标识）
- `domain`: 站点域名
- `crawl_method`: 抓取方式（"HTML 解析" 或 "API 接口"）
- `search_rule`: 搜索 URL 规则，支持 `{keyword}` 和 `{page}` 占位符
- `rule_config`: JSON 格式的配置，包含解析规则

### HTML 解析模式配置示例

```json
{
    "item_selector": "figure.photo-card",
    "image_selector": "img",
    "title_selector": ".photo-title",
    "link_selector": "a.photo-link"
}
```

- `item_selector`: 每个图片项的 CSS 选择器（可选）
- `image_selector`: 图片元素的 CSS 选择器
- `title_selector`: 标题元素的 CSS 选择器（可选）
- `link_selector`: 链接元素的 CSS 选择器（可选）

### API 接口模式配置示例

```json
{
    "items_path": "results.photos",
    "title_field": "alt_description",
    "image_field": "urls.regular",
    "page_field": "links.html",
    "api_key": "your_api_key_here"
}
```

- `items_path`: JSON 数据路径，用点号分隔
- `title_field`: 标题字段路径
- `image_field`: 图片 URL 字段路径
- `page_field`: 页面链接字段路径
- `api_key`: API 密钥（可选）

## 使用示例

### 创建抓取任务

```python
from app.services.crawl_service import CrawlService
from app.schemas.crawl_task import CrawlTaskCreate

# 创建服务实例
service = CrawlService(db)

# 创建任务
payload = CrawlTaskCreate(
    keyword="nature",
    target_scope="all",  # 或 "selected"
    target_site_codes=["unsplash", "pexels"],
    per_site_limit=10,
    max_pages=3,
    created_by="admin"
)

result = service.create_task(payload)
```

### Unsplash 配置说明

Unsplash 需要 API Key 才能访问，配置示例：

```sql
INSERT INTO site_configs (name, code, domain, crawl_method, search_rule, rule_config, enabled)
VALUES (
    'Unsplash',
    'unsplash',
    'api.unsplash.com',
    'API 接口',
    '/search/photos?query={keyword}&per_page={page}',
    '{
        "items_path": "results",
        "title_field": "alt_description",
        "image_field": "urls.regular",
        "page_field": "links.html",
        "api_key": "YOUR_UNSPLASH_ACCESS_KEY"
    }',
    true
);
```

### 免登录网站配置示例

对于不需要登录的网站（如某些公开图片站）：

```sql
INSERT INTO site_configs (name, code, domain, crawl_method, search_rule, rule_config, enabled)
VALUES (
    'Example Site',
    'example',
    'example.com',
    'HTML 解析',
    '/search?q={keyword}&page={page}',
    '{
        "image_selector": "img.photo-thumb",
        "title_selector": ".photo-title",
        "link_selector": "a.photo-detail"
    }',
    true
);
```

## 注意事项

1. **反爬虫机制**：许多网站（如 Unsplash、Pexels）有反爬虫机制，需要：
   - 使用 API Key
   - 设置合适的 User-Agent
   - 控制请求频率

2. **降级机制**：当网站返回 401/403 错误时，系统会自动降级到模拟数据，确保任务不中断

3. **图片去重**：系统会通过图片 hash 值进行去重，避免重复保存

4. **错误处理**：单个站点失败不会影响其他站点的抓取

## 测试建议

1. 先使用公开免费、无反爬的网站进行测试
2. 验证 HTML 解析规则是否正确
3. 逐步添加需要 API Key 的网站
4. 监控日志查看抓取结果
