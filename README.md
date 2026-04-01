# 🚀 微信公众号智能运营工作台

<div align="center">

![GitHub release](https://img.shields.io/badge/version-0.4.0-blue)
![Python](https://img.shields.io/badge/python-3.13+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**一站式微信公众号内容创作与运营管理解决方案**

[特性](#-主要特性) • [技术栈](#-技术栈) • [快速开始](#-快速开始) • [功能演示](#-功能模块) • [API 文档](#-api-接口)

</div>

---

## 📖 项目简介

**微信公众号智能运营工作台** 是一款专为微信公众号运营者打造的现代化管理工具，集成了 **AI 智能创作**、**素材管理**、**文章编辑**、**自动采集**、**一键发布** 等核心功能。通过轻量化的技术栈和简洁的界面设计，帮助运营者大幅提升内容创作效率和运营质量。

### 💡 核心价值

- ✨ **AI 赋能**：集成 GPT 等主流大模型，智能生成封面图、配图和内容建议
- 🎯 **全流程管理**：从素材采集、文章编辑到微信发布，一站式完成所有操作流程
- 🔧 **灵活配置**：支持多模型切换、自定义采集站点、个性化 AI 参数设置
- 📊 **数据驱动**：完善的发布记录和草稿管理，让每次运营都有迹可循
- 🌐 **开源免费**：基于 FastAPI + 原生js 构建，代码开源透明，可自由扩展

---

## ⭐ 主要特性

### 🎨 AI 智能助手
- **图片生成**：支持 DALL-E 3、Midjourney 等多种 AI 模型，生成高质量封面图和配图
- **智能推荐**：根据文章内容自动生成标题、摘要和排版建议
- **多图批量生成**：单次最多生成 6 张图片，支持负向提示词精准控制
- **参考图功能**：支持上传参考图进行风格迁移和相似度生成
- **动态模型切换**：可在运行时切换不同的大模型配置

### 📁 素材管理系统
- **永久素材库**：上传图片自动生成缩略图，支持分类管理和快速检索
- **采集素材**：从配置的网站自动抓取图片资源，建立专属素材库
- **素材关联**：灵活绑定素材与草稿，支持拖拽排序和 caption 编辑
- **CDN 加速**：本地文件服务静态资源托管，访问更流畅

### ✍️ 文章编辑器
- **可视化编辑**：富文本编辑器，所见即所得的文章编排体验
- **模板系统**：内置多种精美排版模板（图片画廊、极简图文、混合排版）
- **智能排版**：自动优化段落间距、字体大小、配色方案
- **草稿箱**：保存多个版本草稿，支持复制、重新编辑和历史追溯

### 🤖 自动化采集
- **站点配置**：灵活配置采集目标网站和规则
- **定时任务**：支持周期性自动采集和增量更新
- **任务监控**：实时查看采集进度和日志记录
- **智能过滤**：去重、质量筛选、版权标识

### 📤 微信发布
- **草稿同步**：一键将编辑好的文章同步到微信公众号草稿箱
- **正式发布**：直接从工作台发布文章到公众号
- **状态追踪**：实时显示草稿/已发布状态，发布记录可查询
- **预览功能**：发布前微信扫码预览效果
- **配置检测**：智能检测微信公众号 API 配置状态

### 🔐 用户与权限
- **账户管理**：支持多用户登录和账户信息维护
- **默认管理员**：首次启动自动创建 admin 账户
- **会话安全**：基于 Session 的身份验证机制

---

## 🛠️ 技术栈

### 后端框架
- **核心框架**：[FastAPI 0.116+](https://fastapi.tiangolo.com/) - 现代高性能 Web 框架
- **ASGI 服务器**：[Uvicorn 0.35+](https://www.uvicorn.org/) - 高性能异步服务器
- **数据验证**：[Pydantic 2.11+](https://docs.pydantic.dev/) - 类型安全的数据校验
- **数据库 ORM**：[SQLAlchemy 2.0+](https://www.sqlalchemy.org/) - Python SQL 工具包
- **模板引擎**：[Jinja2 3.1+](https://jinja.palletsprojects.com/) - 现代化模板系统
- **HTTP 客户端**：[Httpx 0.28+](https://www.python-httpx.org/) - 异步 HTTP 请求库
- **AI SDK**：[OpenAI Python 1.55+](https://github.com/openai/openai-python) - OpenAI 官方 SDK

### 前端技术
- **UI 框架**：原生 JavaScript (Vanilla JS) + 自定义 CSS
- **模板系统**：Jinja2 服务端渲染 (SSR)
- **样式方案**：Flexbox + Grid 响应式布局
- **交互组件**：原生 DOM API + Fetch AJAX

### 数据存储
- **数据库**：SQLite 3.x - 轻量级嵌入式数据库
- **配置文件**：YAML + Pydantic Settings
- **文件存储**：本地文件系统（图片、缩略图、AI 生成资源）

### 开发测试
- **测试框架**：[Pytest 8.4+](https://docs.pytest.org/) - 功能丰富的测试框架
- **测试工具**：FastAPI TestClient - 接口集成测试

---

## 🚀 快速开始

### 环境要求

- Python 3.13+
- pip 包管理器
- Git（克隆仓库用）

### 安装步骤

#### 1. 克隆项目

```bash
git clone git@github.com:jwsang/WeChatOfficialAccount.git
cd WeChatOfficialAccount
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> 💡 **提示**：AI 模型配置可在系统启动后通过「模型配置」和「AI 助手」页面动态管理，无需手动修改配置文件。

#### 4. 初始化数据库（可选）

项目首次启动时会自动创建数据库表，也可手动执行：

```bash
python bootstrap_phase1.py
```

#### 5. 启动服务

```bash
python app/main.py
```

访问 http://localhost:8000 即可使用

### 默认账户

首次启动会自动创建默认管理员账户：
- **用户名**：admin
- **密码**：请联系项目管理员或查看数据库配置

### 动态配置说明

本项目采用**运行时动态配置**方式，大部分设置可在系统启动后通过 Web 界面完成：

- ✅ **AI 模型配置**：在「模型配置」页面管理多个大模型
- ✅ **AI 助手设置**：在「AI 助手」页面配置默认参数
- ✅ **微信配置**：在草稿箱页面直接配置公众号 AppID 和 Secret
- ✅ **采集站点**：在「站点配置」页面添加和管理采集源
- ✅ **用户账户**：登录后在「账户管理」页面修改个人信息和密码

---

## 📦 功能模块详解

### AI 助手模块

**路径**：`/ai-assist`

AI 助手提供强大的图片生成能力：

1. **模型选择**：可从模型管理中选择预设模型或临时切换
2. **参数配置**：
   - 尺寸：1024x1024, 1792x1024, 1024x1792 等
   - 质量：standard / hd
   - 风格：vivid / natural
   - 数量：1-6 张
3. **提示词工程**：
   - 正向提示词：描述想要的画面
   - 负向提示词：排除不需要的元素（如文字、水印）
4. **参考图功能**：上传参考图片进行风格引导
5. **生成历史**：查看和管理历史生成记录
6. **快捷操作**：
   - 添加到素材库
   - 下载原图
   - 重新生成

### 素材管理模块

**路径**：`/materials`

素材管理是内容创作的基础：

- **上传方式**：
  - 单张上传：选择图片文件立即上传
  - 批量上传：一次选择多张图片
  - AI 生成：从 AI 助手直接添加
  - 采集获取：从配置站点自动抓取

- **素材属性**：
  - 原始文件名
  - 本地存储路径
  - 缩略图预览
  - 来源标识（上传/AI 生成/采集）
  - 创建时间

- **管理操作**：
  - 预览大图
  - 删除素材
  - 筛选排序
  - 快速检索

### 文章创作模块

**路径**：`/articles` → `/drafts`

完整的文章创作流程：

#### 文章列表页
- 展示所有已创建的文章
- 按模板类型筛选
- 关键字搜索
- 快速删除

#### 草稿箱（核心编辑器）
- **基础信息编辑**：
  - 标题（必填，限 200 字内）
  - 摘要（选填，限 500 字内）
  - 作者名（选填）
  - 原文链接（选填）

- **封面设置**：
  - 从素材库选择封面图
  - 预览封面效果

- **内容编排**：
  - 选择模板（image_gallery / minimal_gallery / mixed_graphic）
  - 添加素材（图片/视频）
  - 拖拽排序
  - 编辑说明文字

- **微信集成**：
  - 同步草稿：推送到微信公众号草稿箱
  - 预览：微信扫码预览
  - 发布：直接发布到公众号
  - 状态显示：已草稿/已发布

### 采集管理模块

**路径**：`/crawl`

自动化素材采集系统：

- **站点管理**：
  - 配置目标网站 URL
  - 设置采集规则
  - 定义更新频率

- **采集任务**：
  - 立即执行：手动触发单次采集
  - 周期任务：按计划自动执行
  - 增量模式：仅采集新增内容

- **任务监控**：
  - 实时进度显示
  - 成功/失败统计
  - 详细日志记录
  - 错误重试机制

### 发布历史模块

**路径**：`/history`

追踪所有发布记录：

- **记录详情**：
  - 文章标题
  - 发布时间
  - 发布操作人
  - 微信文章 ID
  - 素材使用情况

- **数据分析**：
  - 发布频次统计
  - 模板使用偏好
  - 素材复用率

### 模型配置模块

**路径**：`/model-configs`

管理多个 AI 大模型配置：

- **支持模型**：
  - OpenAI GPT 系列
  - 国内大模型（通义千问、文心一言等）
  - 自建模型服务

- **配置项**：
  - API Base URL
  - API Key
  - 模型名称
  - 超时时间
  - 其他参数

- **使用场景**：
  - 为不同任务选择不同模型
  - 成本优化（便宜模型用于日常任务）
  - 性能对比测试

### 站点配置模块

**路径**：`/sites`

管理采集源站点：

- **站点信息**：
  - 站点名称
  - 域名地址
  - 采集优先级
  - 启用状态

- **AI 辅助建议**：
  - 智能推荐优质站点
  - 分析站点内容质量
  - 生成采集策略

---

## 🔌 API 接口

项目提供完整的 RESTful API，所有接口均有认证保护。

### 认证相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/logout` | 用户登出 |
| GET | `/api/auth/me` | 获取当前用户信息 |
| PUT | `/api/auth/me` | 更新用户信息 |

### AI 助手

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/ai-assist/config` | 获取 AI 配置 |
| PUT | `/api/ai-assist/config` | 更新 AI 配置 |
| PUT | `/api/ai-assist/config-with-model/{model_id}` | 使用模型管理配置 |
| POST | `/api/ai-assist/generate` | 生成图片 |
| POST | `/api/ai-assist/materials` | 添加到素材库 |

### 素材管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/materials` | 获取素材列表 |
| POST | `/api/materials` | 上传素材 |
| DELETE | `/api/materials/{material_id}` | 删除素材 |
| GET | `/api/materials/{material_id}` | 获取素材详情 |

### 文章与草稿

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/articles` | 获取文章列表 |
| POST | `/api/articles` | 创建文章 |
| PUT | `/api/articles/{article_id}` | 更新文章 |
| DELETE | `/api/articles/{article_id}` | 删除文章 |
| GET | `/api/drafts` | 获取草稿列表 |
| GET | `/api/drafts/{draft_id}` | 获取草稿详情 |
| PUT | `/api/drafts/{draft_id}` | 更新草稿 |
| DELETE | `/api/drafts/{draft_id}` | 删除草稿 |
| POST | `/api/drafts/{draft_id}/sync` | 同步到微信草稿箱 |
| POST | `/api/drafts/{draft_id}/publish` | 发布到公众号 |

### 采集任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/crawl/tasks` | 获取任务列表 |
| POST | `/api/crawl/tasks` | 创建采集任务 |
| GET | `/api/crawl/tasks/{task_id}` | 获取任务详情 |
| POST | `/api/crawl/tasks/{task_id}/execute` | 执行任务 |

### 发布历史

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/history` | 获取历史记录 |
| GET | `/api/history/{record_id}` | 获取记录详情 |

### 站点管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sites` | 获取站点列表 |
| POST | `/api/sites` | 创建站点 |
| PUT | `/api/sites/{site_id}` | 更新站点 |
| DELETE | `/api/sites/{site_id}` | 删除站点 |
| POST | `/api/sites/suggest` | AI 推荐站点 |

### 模型配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/model-configs` | 获取模型列表 |
| POST | `/api/model-configs` | 创建模型配置 |
| PUT | `/api/model-configs/{config_id}` | 更新配置 |
| DELETE | `/api/model-configs/{config_id}` | 删除配置 |

### 微信配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/wechat/config-status` | 获取微信配置状态 |
| PUT | `/api/wechat/config` | 更新微信配置 |

---

## 📂 项目结构

```
WeChatOfficialAccount/
├── app/                          # 应用主目录
│   ├── api/                      # API 路由
│   │   ├── ai_assist_routes.py   # AI 助手接口
│   │   ├── article_routes.py     # 文章管理接口
│   │   ├── auth_routes.py        # 认证接口
│   │   ├── crawl_routes.py       # 采集任务接口
│   │   ├── history_routes.py     # 历史记录接口
│   │   ├── material_routes.py    # 素材管理接口
│   │   ├── model_config_routes.py # 模型配置接口
│   │   └── site_routes.py        # 站点管理接口
│   ├── core/                     # 核心配置
│   │   └── config.py             # 应用配置
│   ├── db/                       # 数据库相关
│   │   └── session.py            # 数据库会话
│   ├── models/                   # 数据模型
│   │   ├── article_draft.py      # 文章草稿模型
│   │   ├── material_image.py     # 素材图片模型
│   │   ├── crawl_task.py         # 采集任务模型
│   │   ├── model_config.py       # 模型配置模型
│   │   └── ...
│   ├── repositories/             # 数据访问层
│   │   ├── article_repository.py
│   │   ├── material_repository.py
│   │   └── ...
│   ├── schemas/                  # Pydantic 模型
│   │   ├── ai_assist.py          # AI 助手 Schema
│   │   ├── article.py            # 文章 Schema
│   │   └── ...
│   ├── services/                 # 业务逻辑层
│   │   ├── ai_assist_service.py  # AI 助手服务
│   │   ├── article_service.py    # 文章服务
│   │   ├── wechat_client.py      # 微信客户端
│   │   └── ...
│   ├── static/                   # 静态资源
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── app.js
│   │       └── pages/
│   ├── templates/                # HTML 模板
│   │   ├── base.html             # 基础模板
│   │   ├── ai_assist.html        # AI 助手页面
│   │   ├── articles.html         # 文章列表页
│   │   ├── drafts.html           # 草稿箱页面
│   │   ├── materials.html        # 素材管理页
│   │   └── ...
│   └── main.py                   # 应用入口
├── config/                       # 配置文件
│   └── config.yml                # YAML 配置
├── data/                         # 数据目录（运行时生成）
│   ├── ai_generated/             # AI 生成图片
│   ├── thumbnails/               # 缩略图
│   ├── uploads/                  # 用户上传
│   └── app.db                    # SQLite 数据库
├── tests/                        # 测试用例
│   ├── test_ai_assist.py
│   ├── test_articles.py
│   ├── test_auth.py
│   └── ...
├── bootstrap_*.py                # 初始化脚本
├── requirements.txt              # Python 依赖
└── README.md                     # 项目文档
```

---

## 🧪 运行测试

项目使用 Pytest 进行测试，确保核心功能稳定性：

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_ai_assist.py -v

# 带覆盖率报告
pytest --cov=app --cov-report=html
```

---

## 🔒 安全性

### 认证机制
- 基于 Session 的身份验证
- 密码加密存储
- 登录态自动过期

### 数据安全
- SQL 注入防护（SQLAlchemy ORM）
- XSS 攻击防护（Jinja2 自动转义）
- CSRF 保护（SameSite Cookie 策略）

### 配置安全
- 敏感信息与环境变量分离
- API Key 掩码显示
- 配置文件权限控制

---

## 🛣️ 开发路线图

### v0.5.0（规划中）
- [ ] 支持视频素材处理
- [ ] 增加更多排版模板
- [ ] 微信菜单管理
- [ ] 粉丝消息自动回复

### v0.6.0（规划中）
- [ ] 多公众号支持
- [ ] 定时群发功能
- [ ] 数据统计看板
- [ ] 移动端适配

### 长期目标
- [ ] 插件系统
- [ ] 团队协作功能
- [ ] AIGC 内容质量检测
- [ ] 一键分发多平台

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境搭建

1. Fork 本项目
2. 克隆到本地
3. 创建虚拟环境：`python -m venv venv`
4. 激活虚拟环境并安装依赖
5. 安装开发依赖（如有）

### 提交规范

- 功能需求：请提交详细的需求描述和使用场景
- Bug 反馈：请提供复现步骤和环境信息
- 代码贡献：请确保代码格式规范并通过测试

---

## 📄 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

---

## 📬 联系方式

- 📧 Email: your.email@example.com
- 💬 Issues: [GitHub Issues](https://github.com/yourusername/WeChatOfficialAccount/issues)
- 📖 文档：本项目 Wiki

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代高效的 Web 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包
- [OpenAI Python SDK](https://github.com/openai/openai-python) - OpenAI 官方 SDK
- [Pydantic](https://docs.pydantic.dev/) - 数据验证库
- [Jinja2](https://jinja.palletsprojects.com/) - 模板引擎

---

<div align="center">

**如果觉得有用，请给个 ⭐ Star 支持一下！**

Made with ❤️ by WeChatOfficialAccount Team

</div>
