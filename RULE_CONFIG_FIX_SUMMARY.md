# Rule Config 字段修复总结

## 问题描述
用户反馈在站点配置页面找不到 `rule_config` 相关字段，导致无法配置 API Key 和其他抓取规则。

## 根本原因
1. **Schema 定义不完整**: `SiteRuleConfig` 类只定义了 HTML 解析模式的字段，缺少 API 接口模式所需字段（如 `api_key`, `items_path`, `title_field` 等）
2. **前端表单缺失**: 站点配置页面只显示了部分高级配置字段，没有针对 API 接口和 HTML 解析分别提供专用配置区域
3. **JavaScript 未同步**: 前端 JS 代码中的 `collectRuleConfig()` 和 `applyRuleConfigToForm()` 函数未包含新字段

## 解决方案

### 1. 扩展 Schema 定义 (`app/schemas/site.py`)
```python
class SiteRuleConfig(BaseModel):
    # HTML 解析模式字段
    search_url_template: str = ""
    result_container_path: str = ""
    image_url_path: str = ""
    source_page_url_path: str = ""
    title_path: str = ""
    pagination_param: str = "page"
    pagination_start: int = 1
    pagination_size_param: str = "limit"
    request_method: Literal["GET", "POST"] = "GET"
    request_headers: dict[str, str] = Field(default_factory=dict)
    request_query_template: dict[str, str] = Field(default_factory=dict)
    extra_notes: str = ""
    
    # API 接口模式字段（兼容旧版配置）
    api_key: str = ""
    items_path: str = ""
    title_field: str = ""
    image_field: str = ""
    page_field: str = ""
    
    # 通用爬虫字段（CSS 选择器）
    item_selector: str = ""
    image_selector: str = ""
    link_selector: str = ""
```

### 2. 优化前端表单 (`app/templates/sites.html`)
将结构化规则配置分为三个区域：

**API 接口配置区** (适用于 Unsplash/Pexels/Pixabay 等)
- API Key
- 数据项路径 (items_path)
- 标题字段 (title_field)
- 图片 URL 字段 (image_field)
- 页面 URL 字段 (page_field)

**HTML 解析配置区** (适用于普通网页)
- 搜索模板 (search_url_template)
- 请求方法 (request_method)
- 条目选择器 (item_selector)
- 图片选择器 (image_selector)
- 链接选择器 (link_selector)
- 标题选择器 (title_selector)

**高级配置区**
- 结果容器路径
- 分页参数
- 请求头 JSON
- 固定查询参数 JSON
- 规则备注

### 3. 更新 JavaScript 逻辑 (`app/static/js/app.js`)

**新增元素引用:**
```javascript
elements: {
    // API 接口模式字段
    ruleApiKey: document.getElementById('rule-api-key'),
    ruleItemsPath: document.getElementById('rule-items-path'),
    ruleTitleField: document.getElementById('rule-title-field'),
    ruleImageField: document.getElementById('rule-image-field'),
    rulePageField: document.getElementById('rule-page-field'),
    // HTML 解析模式字段
    ruleItemSelector: document.getElementById('rule-item-selector'),
    ruleImageSelector: document.getElementById('rule-image-selector'),
    ruleLinkSelector: document.getElementById('rule-link-selector'),
    ruleTitleSelector: document.getElementById('rule-title-selector'),
    // ...其他字段
}
```

**更新 collectRuleConfig():**
收集所有新字段到配置对象中

**更新 applyRuleConfigToForm():**
支持将所有新字段回填到表单

### 4. 数据库配置验证
确保现有站点的 `rule_config` 包含必要字段：
```python
{
  "api_key": "",
  "items_path": "results",
  "title_field": "alt_description",
  "image_field": "urls.regular",
  "page_field": "links.html"
}
```

## 使用方式

### 配置 Unsplash API
1. 登录系统 → 进入「站点管理」页面
2. 编辑 "Unsplash" 站点
3. 在 "API 接口配置" 区域填写您的 API Key
4. 确认其他字段已正确填充：
   - 数据项路径：`results`
   - 标题字段：`alt_description`
   - 图片 URL 字段：`urls.regular`
   - 页面 URL 字段：`links.html`
5. 保存并启用站点

### 配置 HTML 解析站点
1. 新建或编辑站点
2. 选择抓取方式为 "HTML 解析"
3. 在 "HTML 解析配置" 区域填写 CSS 选择器：
   - 条目选择器：`.photo-item`
   - 图片选择器：`img.photo-thumb`
   - 链接选择器：`a.photo-link`
   - 标题选择器：`h3.photo-title`
4. 保存并测试

## 验证结果
```
✓ SiteRuleConfig 新字段测试通过
✓ 所有模块导入成功
✓ 适配器模块正常工作
✓ 数据库配置已更新
```

## 后续建议
1. 为用户提供常用站点的配置模板
2. 增加配置验证和提示功能
3. 添加一键测试功能，实时验证配置是否正确
