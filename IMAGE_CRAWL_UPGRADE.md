# 图片采集功能升级说明

## 🎯 改进方案

采用**混合架构**：官方 API 适配器 + 通用爬虫适配器，大幅提升素材采集的稳定性和质量。

---

## ✨ 新增功能

### 1. 官方 API 适配器（推荐）

已集成三大主流高清图库的官方 API：

#### Unsplash 适配器
- **特点**: 高质量艺术摄影，适合封面图和大图
- **申请 API Key**: https://unsplash.com/developers
- **配置方式**: 
  1. 进入「站点配置」页面
  2. 编辑 "Unsplash" 站点
  3. 在 `rule_config` 中填写 `api_key` 字段

#### Pexels 适配器
- **特点**: 丰富的股票照片和视频，人物场景多样
- **申请 API Key**: https://www.pexels.com/api/
- **配置方式**: 同上，编辑 "Pexels" 站点

#### Pixabay 适配器
- **特点**: 超过 2700 万张免费图片和视频，支持多语言
- **申请 API Key**: https://pixabay.com/api/docs/
- **配置方式**: 同上，编辑 "Pixabay" 站点

### 2. 通用爬虫适配器

适用于其他支持 HTML 解析的网站：

- **灵活配置**: 通过 CSS 选择器自定义解析规则
- **智能降级**: 抓取失败时自动切换到模拟数据
- **向后兼容**: 保留原有 `_fetch_site_results_legacy` 方法

---

## 🔧 技术实现

### 适配器模式架构

```
BaseImageAdapter (抽象基类)
├── UnsplashAdapter    # Unsplash API
├── PexelsAdapter      # Pexels API
├── PixabayAdapter     # Pixabay API
└── GenericCrawlAdapter # 通用 HTML 爬虫
```

### 核心文件

1. **`app/services/image_adapters.py`** (新增)
   - 定义适配器基类和具体实现
   - 提供统一的 `search_images()` 接口
   - 工厂函数 `get_adapter()` 根据站点代码创建适配器

2. **`app/services/crawl_service.py`** (优化)
   - `_fetch_site_results()`: 优先使用适配器模式
   - `_fetch_site_results_legacy()`: 保留旧版逻辑作为后备
   - 智能判断：API 站点使用官方适配器，其他使用通用爬虫

---

## 📋 使用指南

### 步骤 1: 配置 API Key

1. 访问对应网站申请 API Key
2. 登录系统，进入「站点配置」页面
3. 编辑对应站点，在 `rule_config` JSON 中添加：
   ```json
   {
     "api_key": "你的 API Key"
   }
   ```
4. 保存并启用站点

### 步骤 2: 创建采集任务

1. 进入「采集管理」页面
2. 点击「新建任务」
3. 输入关键词（如：nature, technology, business）
4. 选择目标站点（勾选已配置的 API 站点）
5. 设置每站数量上限（建议 10-30）
6. 点击执行

### 步骤 3: 查看结果

- 任务执行完成后，可在「素材管理」中查看采集到的图片
- 支持去重、筛选和批量操作

---

## 🔍 示例配置

### Unsplash 完整配置

```json
{
  "name": "Unsplash",
  "code": "unsplash",
  "domain": "unsplash.com",
  "enabled": true,
  "crawl_method": "API 接口",
  "rule_config": {
    "api_key": "YOUR_UNSPLASH_API_KEY",
    "items_path": "results",
    "title_field": "alt_description",
    "image_field": "urls.regular",
    "page_field": "links.html"
  }
}
```

### 通用 HTML 站点配置示例

```json
{
  "name": "某图库网站",
  "code": "example_gallery",
  "domain": "gallery.example.com",
  "enabled": true,
  "crawl_method": "HTML 解析",
  "search_rule": "/search?q={keyword}&page={page}",
  "rule_config": {
    "item_selector": ".photo-item",
    "image_selector": "img.photo-thumb",
    "title_selector": "h3.photo-title",
    "link_selector": "a.photo-link"
  }
}
```

---

## ⚠️ 注意事项

### API 限制

| 站点 | 免费额度 | 速率限制 |
|------|---------|---------|
| Unsplash | 每小时 50 次请求 | 需遵守 [Guidelines](https://unsplash.com/developers/documentation/guidelines) |
| Pexels | 每月 20,000 次请求 | 需标注来源 |
| Pixabay | 每小时 5,000 次请求 | 无强制署名要求 |

### 最佳实践

1. **合理设置采集数量**: 单次任务建议不超过 30 张/站
2. **避免频繁请求**: 设置适当的采集间隔
3. **遵守使用条款**: 注意版权和使用限制
4. **定期更新 API Key**: 如遇限流可申请新 Key

### 故障排查

- **问题**: 采集结果为空或全部是模拟数据
  - **检查**: API Key 是否正确配置
  - **检查**: 站点是否已启用
  - **检查**: 网络连接是否正常

- **问题**: HTTP 401/403 错误
  - **原因**: API Key 无效或过期
  - **解决**: 重新申请并更新配置

- **问题**: 部分站点抓取失败
  - **原因**: 网站反爬或结构变更
  - **解决**: 使用官方 API 或调整 CSS 选择器

---

## 🚀 性能对比

| 方案 | 稳定性 | 图片质量 | 速度 | 推荐度 |
|------|--------|---------|------|--------|
| 官方 API | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 强烈推荐 |
| 通用爬虫 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⚠️ 备用方案 |
| 纯模拟数据 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ❌ 仅测试用 |

---

## 📚 扩展开发

如需添加新的图片源适配器：

1. 继承 `BaseImageAdapter` 类
2. 实现 `search_images()` 方法
3. 在 `get_adapter()` 工厂函数中注册
4. 在数据库中配置对应站点

示例代码见 `app/services/image_adapters.py`

---

## 🆘 获取帮助

- 查看项目文档：README.md
- 提交 Issue: https://github.com/jwsang/WeChatOfficialAccount/issues
- 联系作者：jw_sang@126.com
