const state = {
    selectedSiteId: null,
    selectedTaskId: null,
    selectedMaterialId: null,
    currentMaterial: null,
    articleCoverMaterialId: null,
    articlePreview: null,
    sites: [],
    tasks: [],
    materials: [],
    materialTags: [],
    materialTagSummaryExpanded: false,
    articleMaterials: [],
    articleDrafts: [],
    articleEditingDraftId: null,
    wechatConfigStatus: null,
    historyOverview: null,
    currentUser: null,
    aiAssistConfig: null,
    aiGeneratedResults: [],
    aiSelectedTempIds: [],
};

const elements = {
    form: document.getElementById('site-form'),
    siteId: document.getElementById('site-id'),
    name: document.getElementById('name'),
    code: document.getElementById('code'),
    domain: document.getElementById('domain'),
    siteAiPrefillButton: document.getElementById('site-ai-prefill-button'),
    siteAiPrefillMessage: document.getElementById('site-ai-prefill-message'),
    crawlMethod: document.getElementById('crawl_method'),
    searchRule: document.getElementById('search_rule'),
    parseRule: document.getElementById('parse_rule'),
    pageRule: document.getElementById('page_rule'),
    remark: document.getElementById('remark'),
    enabled: document.getElementById('enabled'),
    ruleSearchUrlTemplate: document.getElementById('rule-search-url-template'),
    ruleRequestMethod: document.getElementById('rule-request-method'),
    ruleResultContainerPath: document.getElementById('rule-result-container-path'),
    ruleImageUrlPath: document.getElementById('rule-image-url-path'),
    ruleSourcePageUrlPath: document.getElementById('rule-source-page-url-path'),
    ruleTitlePath: document.getElementById('rule-title-path'),
    rulePaginationParam: document.getElementById('rule-pagination-param'),
    rulePaginationStart: document.getElementById('rule-pagination-start'),
    rulePaginationSizeParam: document.getElementById('rule-pagination-size-param'),
    ruleRequestHeaders: document.getElementById('rule-request-headers'),
    ruleRequestQueryTemplate: document.getElementById('rule-request-query-template'),
    ruleExtraNotes: document.getElementById('rule-extra-notes'),
    formMessage: document.getElementById('form-message'),
    listMessage: document.getElementById('list-message'),
    siteList: document.getElementById('site-list'),
    resetButton: document.getElementById('reset-button'),
    refreshButton: document.getElementById('refresh-button'),
    submitButton: document.getElementById('submit-button'),
    testKeyword: document.getElementById('test-keyword'),
    testButton: document.getElementById('test-button'),
    testResult: document.getElementById('test-result'),
    crawlForm: document.getElementById('crawl-form'),
    crawlScope: document.getElementById('crawl-scope'),
    crawlKeyword: document.getElementById('crawl-keyword'),
    crawlSiteSelector: document.getElementById('crawl-site-selector'),
    perSiteLimit: document.getElementById('per-site-limit'),
    maxPages: document.getElementById('max-pages'),
    createdBy: document.getElementById('created-by'),
    crawlFormMessage: document.getElementById('crawl-form-message'),
    crawlListMessage: document.getElementById('crawl-list-message'),
    crawlTaskList: document.getElementById('crawl-task-list'),
    crawlTaskDetail: document.getElementById('crawl-task-detail'),
    crawlRefreshButton: document.getElementById('crawl-refresh-button'),
    crawlResetButton: document.getElementById('crawl-reset-button'),
    retryTaskButton: document.getElementById('retry-task-button'),
    materialFilterForm: document.getElementById('material-filter-form'),
    materialQueryText: document.getElementById('material-query-text'),
    materialKeyword: document.getElementById('material-keyword'),
    materialSourceSiteCode: document.getElementById('material-source-site-code'),
    materialSourceType: document.getElementById('material-source-type'),
    materialSourceAllButton: document.getElementById('material-source-all-button'),
    materialSourceCrawlButton: document.getElementById('material-source-crawl-button'),
    materialSourceAiButton: document.getElementById('material-source-ai-button'),
    materialSourceManualButton: document.getElementById('material-source-manual-button'),
    materialStatus: document.getElementById('material-status'),
    materialAuditStatus: document.getElementById('material-audit-status'),
    materialTag: document.getElementById('material-tag'),
    materialFilterMessage: document.getElementById('material-filter-message'),
    materialTagSummary: document.getElementById('material-tag-summary'),
    materialTagToggleButton: document.getElementById('material-tag-toggle-button'),
    materialRefreshButton: document.getElementById('material-refresh-button'),
    materialFilterResetButton: document.getElementById('material-filter-reset-button'),
    materialUploadForm: document.getElementById('material-upload-form'),
    materialUploadTitle: document.getElementById('material-upload-title'),
    materialUploadKeywords: document.getElementById('material-upload-keywords'),
    materialUploadTags: document.getElementById('material-upload-tags'),
    materialUploadRemark: document.getElementById('material-upload-remark'),
    materialUploadFiles: document.getElementById('material-upload-files'),
    materialUploadMessage: document.getElementById('material-upload-message'),
    materialUploadResetButton: document.getElementById('material-upload-reset-button'),
    materialListMessage: document.getElementById('material-list-message'),
    materialList: document.getElementById('material-list'),
    materialCount: document.getElementById('material-count'),
    materialSelectAllButton: document.getElementById('material-select-all-button'),
    materialBulkAuditButton: document.getElementById('material-bulk-audit-button'),
    materialBulkDeleteButton: document.getElementById('material-bulk-delete-button'),
    materialDetail: document.getElementById('material-detail'),
    materialDetailModal: document.getElementById('material-detail-modal'),
    materialDetailModalBackdrop: document.getElementById('material-detail-modal-backdrop'),
    materialDetailModalCloseButton: document.getElementById('material-detail-modal-close-button'),
    articleBuilderMessage: document.getElementById('article-builder-message'),
    articleSyncSelectionButton: document.getElementById('article-sync-selection-button'),
    articleClearSelectionButton: document.getElementById('article-clear-selection-button'),
    articleSelectedCount: document.getElementById('article-selected-count'),
    articleSelectedMaterials: document.getElementById('article-selected-materials'),
    articleForm: document.getElementById('article-form'),
    articleTitle: document.getElementById('article-title'),
    articleSummary: document.getElementById('article-summary'),
    articleAuthorName: document.getElementById('article-author-name'),
    articleSourceUrl: document.getElementById('article-source-url'),
    articleTemplateCode: document.getElementById('article-template-code'),
    articleAutoSort: document.getElementById('article-auto-sort'),
    articleDraftStatus: document.getElementById('article-draft-status'),
    articlePreviewButton: document.getElementById('article-preview-button'),
    articleSaveButton: document.getElementById('article-save-button'),
    articleResetButton: document.getElementById('article-reset-button'),
    articlePreviewMeta: document.getElementById('article-preview-meta'),
    articlePreviewHtml: document.getElementById('article-preview-html'),
    draftEditorState: document.getElementById('draft-editor-state'),
    draftListMessage: document.getElementById('draft-list-message'),
    draftList: document.getElementById('draft-list'),
    draftRefreshButton: document.getElementById('draft-refresh-button'),
    wechatConfigForm: document.getElementById('wechat-config-form'),
    wechatAppId: document.getElementById('wechat-app-id'),
    wechatAppSecret: document.getElementById('wechat-app-secret'),
    wechatConfigMessage: document.getElementById('wechat-config-message'),
    wechatConfigStatus: document.getElementById('wechat-config-status'),
    wechatConfigRefreshButton: document.getElementById('wechat-config-refresh-button'),
    historyMessage: document.getElementById('history-message'),
    historyRefreshButton: document.getElementById('history-refresh-button'),
    historyArticleSummary: document.getElementById('history-article-summary'),
    historyMaterialSummary: document.getElementById('history-material-summary'),
    historyCrawlList: document.getElementById('history-crawl-list'),
    historyLogList: document.getElementById('history-log-list'),
    historySiteStats: document.getElementById('history-site-stats'),
    historyPublishRecords: document.getElementById('history-publish-records'),
    historyTagStats: document.getElementById('history-tag-stats'),
    topbarUserMenuContainer: document.getElementById('topbar-user-menu-container'),
    topbarUserTrigger: document.getElementById('topbar-user-trigger'),
    topbarUserMenu: document.getElementById('topbar-user-menu'),
    topbarUserAvatar: document.getElementById('topbar-user-avatar'),
    topbarUserName: document.getElementById('topbar-user-name'),
    topbarAccountLink: document.getElementById('topbar-account-link'),
    topbarLogoutButton: document.getElementById('topbar-logout-button'),
    loginForm: document.getElementById('login-form'),
    loginUsername: document.getElementById('login-username'),
    loginPassword: document.getElementById('login-password'),
    loginMessage: document.getElementById('login-message'),
    accountBasicInfo: document.getElementById('account-basic-info'),
    accountProfileForm: document.getElementById('account-profile-form'),
    accountUsername: document.getElementById('account-username'),
    accountDisplayName: document.getElementById('account-display-name'),
    accountProfileMessage: document.getElementById('account-profile-message'),
    accountPasswordForm: document.getElementById('account-password-form'),
    accountOldPassword: document.getElementById('account-old-password'),
    accountNewPassword: document.getElementById('account-new-password'),
    accountConfirmPassword: document.getElementById('account-confirm-password'),
    accountPasswordMessage: document.getElementById('account-password-message'),
    accountPasswordStrength: document.getElementById('account-password-strength'),
    accountPasswordStrengthFill: document.getElementById('account-password-strength-fill'),
    accountPasswordStrengthText: document.getElementById('account-password-strength-text'),
    accountPasswordRuleList: document.getElementById('account-password-rule-list'),
    aiConfigForm: document.getElementById('ai-config-form'),
    aiConfigBaseUrl: document.getElementById('ai-config-base-url'),
    aiConfigModel: document.getElementById('ai-config-model'),
    aiConfigApiKey: document.getElementById('ai-config-api-key'),
    aiConfigDefaultSize: document.getElementById('ai-config-default-size'),
    aiConfigDefaultQuality: document.getElementById('ai-config-default-quality'),
    aiConfigDefaultStyle: document.getElementById('ai-config-default-style'),
    aiConfigDefaultCount: document.getElementById('ai-config-default-count'),
    aiConfigTimeout: document.getElementById('ai-config-timeout'),
    aiConfigNegativePrompt: document.getElementById('ai-config-negative-prompt'),
    aiConfigMessage: document.getElementById('ai-config-message'),
    aiConfigApiKeyMask: document.getElementById('ai-config-api-key-mask'),
    aiGenerateForm: document.getElementById('ai-generate-form'),
    aiPrompt: document.getElementById('ai-generate-prompt'),
    aiNegativePrompt: document.getElementById('ai-generate-negative-prompt'),
    aiGenerateCount: document.getElementById('ai-generate-count'),
    aiGenerateSize: document.getElementById('ai-generate-size'),
    aiGenerateQuality: document.getElementById('ai-generate-quality'),
    aiGenerateStyle: document.getElementById('ai-generate-style'),
    aiReferenceImage: document.getElementById('ai-generate-reference-image'),
    aiGenerateMessage: document.getElementById('ai-generate-message'),
    aiGeneratedSummary: document.getElementById('ai-generated-summary'),
    aiGeneratedList: document.getElementById('ai-generated-list'),
    aiSelectAllButton: document.getElementById('ai-select-all-button'),
    aiClearSelectionButton: document.getElementById('ai-clear-selection-button'),
    aiAddMaterialButton: document.getElementById('ai-add-material-button'),
    aiMaterialTitlePrefix: document.getElementById('ai-material-title-prefix'),
    aiMaterialKeywords: document.getElementById('ai-material-keywords'),
    aiMaterialTags: document.getElementById('ai-material-tags'),
    aiMaterialRemark: document.getElementById('ai-material-remark'),
    aiMaterialMessage: document.getElementById('ai-material-message'),
};

function formatDate(value) {
    if (!value) return '暂无';
    return new Date(value).toLocaleString('zh-CN', { hour12: false });
}

function escapeHtml(value) {
    const span = document.createElement('span');
    span.textContent = String(value ?? '');
    return span.innerHTML;
}

function showMessage(target, text, type = 'info') {
    if (!target) return;
    target.innerHTML = text ? `<div class="message ${type}">${escapeHtml(text)}</div>` : '';
}

function statusClass(status) {
    const map = {
        completed: 'completed',
        executing: 'executing',
        failed: 'failed',
        partial_success: 'partial_success',
        success: 'success',
        duplicate: 'duplicate',
        enabled: 'enabled',
        disabled: 'disabled',
        available: 'success',
        not_recommended: 'failed',
        deleted: 'disabled',
        pending: 'info',
        approved: 'completed',
        manual: 'info',
        crawl: 'enabled',
        ai: 'ai',
        preview: 'info',
        editing: 'info',
        pending_publish: 'partial_success',
        publishing: 'executing',
        published: 'completed',
        publish_failed: 'failed',
    };
    return map[status] || 'info';
}

function request(url, options = {}) {
    const isFormData = options.body instanceof FormData;
    const headers = { ...(options.headers || {}) };
    if (!isFormData && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }
    return fetch(url, {
        ...options,
        headers,
        credentials: 'same-origin',
    }).then(async (response) => {
        if (response.status === 204) return null;
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || '请求失败');
        return data;
    });
}

function userInitial(user) {
    const source = (user?.display_name || user?.username || '').trim();
    if (!source) return '访';
    return source.charAt(0).toUpperCase();
}

function setUserMenuOpen(open) {
    if (!elements.topbarUserTrigger || !elements.topbarUserMenu) return;
    elements.topbarUserTrigger.setAttribute('aria-expanded', String(open));
    elements.topbarUserMenu.hidden = !open;
}

function applyTopbarUser(user) {
    if (user) {
        if (elements.topbarUserName) {
            elements.topbarUserName.textContent = `${user.display_name}（${user.username}）`;
        }
        if (elements.topbarUserAvatar) {
            elements.topbarUserAvatar.textContent = userInitial(user);
        }
        if (elements.topbarAccountLink) {
            elements.topbarAccountLink.textContent = '账号设置';
            elements.topbarAccountLink.href = '/account';
        }
        if (elements.topbarLogoutButton) {
            elements.topbarLogoutButton.style.display = 'inline-flex';
        }
        return;
    }

    if (elements.topbarUserName) {
        elements.topbarUserName.textContent = '未登录';
    }
    if (elements.topbarUserAvatar) {
        elements.topbarUserAvatar.textContent = '访';
    }
    if (elements.topbarAccountLink) {
        elements.topbarAccountLink.textContent = '去登录';
        elements.topbarAccountLink.href = '/login';
    }
    if (elements.topbarLogoutButton) {
        elements.topbarLogoutButton.style.display = 'none';
    }
}

async function loadCurrentUser({ redirectOnUnauthorized = false } = {}) {
    try {
        const user = await request('/api/auth/me');
        state.currentUser = user;
        applyTopbarUser(user);
        return user;
    } catch (error) {
        state.currentUser = null;
        applyTopbarUser(null);
        if (redirectOnUnauthorized) {
            window.location.href = '/login';
        }
        return null;
    }
}

async function submitLogin(event) {
    event.preventDefault();
    if (!elements.loginUsername || !elements.loginPassword) return;

    const username = elements.loginUsername.value.trim();
    const password = elements.loginPassword.value;
    if (!username || !password) {
        showMessage(elements.loginMessage, '请输入用户名和密码。', 'error');
        return;
    }

    try {
        showMessage(elements.loginMessage, '正在登录...', 'info');
        const user = await request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        state.currentUser = user;
        applyTopbarUser(user);
        showMessage(elements.loginMessage, '登录成功，正在跳转...', 'success');
        window.setTimeout(() => {
            window.location.href = '/';
        }, 300);
    } catch (error) {
        showMessage(elements.loginMessage, error.message, 'error');
    }
}

async function logoutCurrentUser() {
    try {
        await request('/api/auth/logout', { method: 'POST' });
    } catch (error) {
        // ignore logout error
    }
    state.currentUser = null;
    applyTopbarUser(null);
    window.location.href = '/login';
}

function renderAccountBasicInfo(user) {
    if (!elements.accountBasicInfo) return;
    elements.accountBasicInfo.innerHTML = `
        <div class="meta-grid">
            <div><span class="muted">用户 ID</span><strong>${user.id}</strong></div>
            <div><span class="muted">角色</span><strong>${escapeHtml(user.role)}</strong></div>
            <div><span class="muted">最后登录</span><strong>${formatDate(user.last_login_at)}</strong></div>
            <div><span class="muted">创建时间</span><strong>${formatDate(user.created_at)}</strong></div>
        </div>
    `;
}

async function loadAccountProfile() {
    const user = state.currentUser || await loadCurrentUser({ redirectOnUnauthorized: true });
    if (!user) return;
    if (elements.accountUsername) elements.accountUsername.value = user.username;
    if (elements.accountDisplayName) elements.accountDisplayName.value = user.display_name;
    renderAccountBasicInfo(user);
}

async function submitAccountProfile(event) {
    event.preventDefault();
    if (!elements.accountUsername || !elements.accountDisplayName) return;

    const payload = {
        username: elements.accountUsername.value.trim(),
        display_name: elements.accountDisplayName.value.trim(),
    };

    try {
        showMessage(elements.accountProfileMessage, '正在保存账号信息...', 'info');
        const updated = await request('/api/auth/profile', {
            method: 'PUT',
            body: JSON.stringify(payload),
        });
        state.currentUser = updated;
        applyTopbarUser(updated);
        renderAccountBasicInfo(updated);
        showMessage(elements.accountProfileMessage, '账号信息更新成功。', 'success');
    } catch (error) {
        showMessage(elements.accountProfileMessage, error.message, 'error');
    }
}

function evaluatePasswordStrength(password) {
    const source = String(password || '');
    const rules = {
        length: source.length >= 8,
        letter: /[A-Za-z]/.test(source),
        number: /\d/.test(source),
        special: /[^A-Za-z0-9]/.test(source),
    };
    const passedCount = Object.values(rules).filter(Boolean).length;

    if (!source) {
        return {
            rules,
            passedCount,
            score: 0,
            level: 'empty',
            text: '密码强度：未输入',
        };
    }

    const score = Math.min(100, passedCount * 25 + (source.length >= 12 ? 10 : 0));
    if (passedCount <= 1) {
        return { rules, passedCount, score, level: 'weak', text: '密码强度：弱' };
    }
    if (passedCount <= 3) {
        return { rules, passedCount, score, level: 'medium', text: '密码强度：中' };
    }
    return { rules, passedCount, score, level: 'strong', text: '密码强度：强' };
}

function renderPasswordStrength(password) {
    const result = evaluatePasswordStrength(password);

    if (elements.accountPasswordStrengthFill) {
        elements.accountPasswordStrengthFill.style.width = `${result.score}%`;
        elements.accountPasswordStrengthFill.className = `password-strength-fill ${result.level}`;
    }
    if (elements.accountPasswordStrengthText) {
        elements.accountPasswordStrengthText.textContent = result.text;
    }
    if (elements.accountPasswordStrength) {
        const progressBar = elements.accountPasswordStrength.querySelector('[role="progressbar"]');
        if (progressBar) {
            progressBar.setAttribute('aria-valuenow', String(result.score));
        }
    }
    if (elements.accountPasswordRuleList) {
        const items = elements.accountPasswordRuleList.querySelectorAll('.password-rule-item');
        items.forEach((item) => {
            const rule = item.dataset.rule;
            if (!rule) return;
            const passed = Boolean(result.rules[rule]);
            item.classList.toggle('passed', passed);
            item.classList.toggle('failed', !passed);
        });
    }

    return result;
}

async function submitPasswordReset(event) {
    event.preventDefault();
    if (!elements.accountOldPassword || !elements.accountNewPassword || !elements.accountConfirmPassword) return;

    const oldPassword = elements.accountOldPassword.value;
    const newPassword = elements.accountNewPassword.value;
    const confirmPassword = elements.accountConfirmPassword.value;
    if (!oldPassword || !newPassword || !confirmPassword) {
        showMessage(elements.accountPasswordMessage, '请完整填写密码信息。', 'error');
        return;
    }

    const strength = renderPasswordStrength(newPassword);
    if (strength.passedCount < 4) {
        showMessage(elements.accountPasswordMessage, '新密码不符合规则：至少 8 位，且需包含字母、数字和特殊字符。', 'error');
        return;
    }
    if (newPassword !== confirmPassword) {
        showMessage(elements.accountPasswordMessage, '两次输入的新密码不一致。', 'error');
        return;
    }

    try {
        showMessage(elements.accountPasswordMessage, '正在重置密码...', 'info');
        const updated = await request('/api/auth/password/reset', {
            method: 'POST',
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword,
            }),
        });
        state.currentUser = updated;
        applyTopbarUser(updated);
        if (elements.accountPasswordForm) {
            elements.accountPasswordForm.reset();
        }
        renderPasswordStrength('');
        showMessage(elements.accountPasswordMessage, '密码重置成功。', 'success');
    } catch (error) {
        showMessage(elements.accountPasswordMessage, error.message, 'error');
    }
}

function safeParseJson(text, fallback = {}) {
    const source = String(text || '').trim();
    if (!source) return fallback;
    try {
        const parsed = JSON.parse(source);
        return parsed && typeof parsed === 'object' ? parsed : fallback;
    } catch (error) {
        throw new Error('结构化规则中的 JSON 配置格式不正确，请检查请求头或固定查询参数。');
    }
}

function stringifyRuleJson(value) {
    return Object.keys(value || {}).length ? JSON.stringify(value, null, 2) : '';
}

function collectRuleConfig() {
    return {
        search_url_template: elements.ruleSearchUrlTemplate.value.trim(),
        result_container_path: elements.ruleResultContainerPath.value.trim(),
        image_url_path: elements.ruleImageUrlPath.value.trim(),
        source_page_url_path: elements.ruleSourcePageUrlPath.value.trim(),
        title_path: elements.ruleTitlePath.value.trim(),
        pagination_param: elements.rulePaginationParam.value.trim() || 'page',
        pagination_start: Number(elements.rulePaginationStart.value || 1),
        pagination_size_param: elements.rulePaginationSizeParam.value.trim() || 'limit',
        request_method: elements.ruleRequestMethod.value,
        request_headers: safeParseJson(elements.ruleRequestHeaders.value, {}),
        request_query_template: safeParseJson(elements.ruleRequestQueryTemplate.value, {}),
        extra_notes: elements.ruleExtraNotes.value.trim(),
    };
}

function applyRuleConfigToForm(ruleConfig = {}) {
    elements.ruleSearchUrlTemplate.value = ruleConfig.search_url_template || '';
    elements.ruleRequestMethod.value = ruleConfig.request_method || 'GET';
    elements.ruleResultContainerPath.value = ruleConfig.result_container_path || '';
    elements.ruleImageUrlPath.value = ruleConfig.image_url_path || '';
    elements.ruleSourcePageUrlPath.value = ruleConfig.source_page_url_path || '';
    elements.ruleTitlePath.value = ruleConfig.title_path || '';
    elements.rulePaginationParam.value = ruleConfig.pagination_param || 'page';
    elements.rulePaginationStart.value = String(ruleConfig.pagination_start || 1);
    elements.rulePaginationSizeParam.value = ruleConfig.pagination_size_param || 'limit';
    elements.ruleRequestHeaders.value = stringifyRuleJson(ruleConfig.request_headers || {});
    elements.ruleRequestQueryTemplate.value = stringifyRuleJson(ruleConfig.request_query_template || {});
    elements.ruleExtraNotes.value = ruleConfig.extra_notes || '';
}

function renderRuleConfigSummary(ruleConfig = {}) {
    const lines = [
        `模板：${ruleConfig.search_url_template || '未配置'}`,
        `提取：${ruleConfig.result_container_path || '未配置'} → ${ruleConfig.image_url_path || '未配置'}`,
        `分页：${ruleConfig.pagination_param || 'page'} 从 ${ruleConfig.pagination_start || 1} 开始`,
    ];
    if (ruleConfig.extra_notes) {
        lines.push(`备注：${ruleConfig.extra_notes}`);
    }
    return lines.map((line) => `<div>${escapeHtml(line)}</div>`).join('');
}

function applySiteAiSuggestionToForm(suggestion = {}) {
    if (!suggestion || typeof suggestion !== 'object') return;

    if (elements.name && suggestion.name) {
        elements.name.value = suggestion.name;
    }
    if (elements.domain && suggestion.domain) {
        elements.domain.value = suggestion.domain;
    }
    if (elements.code && suggestion.code && (!elements.code.disabled || !elements.code.value.trim())) {
        elements.code.value = suggestion.code;
    }

    if (elements.enabled) {
        const enabledValue = typeof suggestion.enabled === 'boolean' ? suggestion.enabled : true;
        elements.enabled.value = String(enabledValue);
    }
    if (elements.crawlMethod && suggestion.crawl_method) {
        elements.crawlMethod.value = suggestion.crawl_method;
    }
    if (elements.searchRule && suggestion.search_rule) {
        elements.searchRule.value = suggestion.search_rule;
    }
    if (elements.parseRule && suggestion.parse_rule) {
        elements.parseRule.value = suggestion.parse_rule;
    }
    if (elements.pageRule && suggestion.page_rule) {
        elements.pageRule.value = suggestion.page_rule;
    }
    if (elements.remark && suggestion.remark) {
        elements.remark.value = suggestion.remark;
    }
    if (suggestion.rule_config && typeof suggestion.rule_config === 'object') {
        applyRuleConfigToForm(suggestion.rule_config);
    }
}

function resetSiteForm() {
    if (!elements.form) return;
    elements.form.reset();
    if (elements.siteId) elements.siteId.value = '';
    if (elements.enabled) elements.enabled.value = 'true';
    applyRuleConfigToForm();
    if (elements.code) elements.code.disabled = false;
    if (elements.submitButton) elements.submitButton.textContent = '保存站点';
    state.selectedSiteId = null;
    showMessage(elements.siteAiPrefillMessage, '');
    showMessage(elements.formMessage, '已切换为新增站点模式。', 'info');
    renderSiteList();
}

function resetMaterialUploadForm() {
    if (!elements.materialUploadForm) return;
    elements.materialUploadForm.reset();
    showMessage(elements.materialUploadMessage, '上传表单已重置。', 'info');
}

function resetMaterialFilters() {
    if (!elements.materialFilterForm) return;
    elements.materialFilterForm.reset();
    syncMaterialSourceQuickFilterButtons();
    showMessage(elements.materialFilterMessage, '已清空素材筛选条件。', 'info');
}

function applyAiConfigToForm(config = {}) {
    if (elements.aiConfigBaseUrl) elements.aiConfigBaseUrl.value = config.base_url || '';
    if (elements.aiConfigModel) elements.aiConfigModel.value = config.model || '';
    if (elements.aiConfigDefaultSize) elements.aiConfigDefaultSize.value = config.default_size || '1024x1024';
    if (elements.aiConfigDefaultQuality) elements.aiConfigDefaultQuality.value = config.default_quality || 'standard';
    if (elements.aiConfigDefaultStyle) elements.aiConfigDefaultStyle.value = config.default_style || 'vivid';
    if (elements.aiConfigDefaultCount) elements.aiConfigDefaultCount.value = String(config.default_count || 4);
    if (elements.aiConfigTimeout) elements.aiConfigTimeout.value = String(config.timeout_seconds || 120);
    if (elements.aiConfigNegativePrompt) {
        elements.aiConfigNegativePrompt.value = config.default_negative_prompt || '';
    }
    if (elements.aiGenerateCount) elements.aiGenerateCount.value = String(config.default_count || 4);
    if (elements.aiGenerateSize) elements.aiGenerateSize.value = config.default_size || '1024x1024';
    if (elements.aiGenerateQuality) elements.aiGenerateQuality.value = config.default_quality || 'standard';
    if (elements.aiGenerateStyle) elements.aiGenerateStyle.value = config.default_style || 'vivid';
    if (elements.aiNegativePrompt) elements.aiNegativePrompt.value = config.default_negative_prompt || '';
    if (elements.aiConfigApiKeyMask) {
        elements.aiConfigApiKeyMask.textContent = config.has_api_key
            ? `已保存密钥：${config.api_key_masked || '******'}`
            : '尚未保存 API Key';
    }
}

function syncAiSelectionActions() {
    const total = state.aiGeneratedResults.length;
    const selected = state.aiSelectedTempIds.length;
    if (elements.aiGeneratedSummary) {
        elements.aiGeneratedSummary.textContent = total
            ? `已生成 ${total} 张，已选择 ${selected} 张。`
            : '暂无生成结果。';
    }
    if (elements.aiSelectAllButton) elements.aiSelectAllButton.disabled = total === 0 || selected === total;
    if (elements.aiClearSelectionButton) elements.aiClearSelectionButton.disabled = selected === 0;
    if (elements.aiAddMaterialButton) elements.aiAddMaterialButton.disabled = selected === 0;
}

function renderAiGeneratedResults() {
    if (!elements.aiGeneratedList) return;
    const rows = state.aiGeneratedResults || [];
    if (!rows.length) {
        elements.aiGeneratedList.innerHTML = '<div class="empty">暂无生成图片，请先填写提示词后生成。</div>';
        syncAiSelectionActions();
        return;
    }

    const selectedSet = new Set(state.aiSelectedTempIds || []);
    elements.aiGeneratedList.innerHTML = rows
        .map((item) => {
            const checked = selectedSet.has(item.temp_id);
            return `
                <article class="ai-generated-item${checked ? ' selected' : ''}">
                    <label class="checkbox-item ai-generated-check">
                        <input
                            type="checkbox"
                            ${checked ? 'checked' : ''}
                            onchange="toggleAiGeneratedSelection('${escapeHtml(item.temp_id)}', this.checked)"
                        />
                        <span>选择入素材库</span>
                    </label>
                    <img class="ai-generated-thumb" src="${escapeHtml(item.preview_url)}" alt="AI 生成图" />
                    <div class="muted">尺寸：${item.width} × ${item.height}</div>
                    <div class="muted">生成时间：${formatDate(item.created_at)}</div>
                </article>
            `;
        })
        .join('');
    syncAiSelectionActions();
}

async function loadAiAssistConfig(message = '正在加载 AI 配置...') {
    try {
        showMessage(elements.aiConfigMessage, message, 'info');
        const config = await request('/api/ai-assist/config');
        state.aiAssistConfig = config;
        applyAiConfigToForm(config);
        showMessage(elements.aiConfigMessage, 'AI 配置加载完成。', 'success');
    } catch (error) {
        showMessage(elements.aiConfigMessage, error.message, 'error');
    }
}

async function submitAiAssistConfig(event) {
    event.preventDefault();
    const payload = {
        base_url: elements.aiConfigBaseUrl?.value?.trim() || '',
        model: elements.aiConfigModel?.value?.trim() || '',
        default_size: elements.aiConfigDefaultSize?.value?.trim() || '1024x1024',
        default_quality: elements.aiConfigDefaultQuality?.value?.trim() || 'standard',
        default_style: elements.aiConfigDefaultStyle?.value?.trim() || 'vivid',
        default_count: Number(elements.aiConfigDefaultCount?.value || 4),
        timeout_seconds: Number(elements.aiConfigTimeout?.value || 120),
        default_negative_prompt: elements.aiConfigNegativePrompt?.value?.trim() || '',
        api_key: elements.aiConfigApiKey?.value || '',
    };

    try {
        showMessage(elements.aiConfigMessage, '正在保存 AI 配置...', 'info');
        const result = await request('/api/ai-assist/config', {
            method: 'PUT',
            body: JSON.stringify(payload),
        });
        state.aiAssistConfig = result;
        applyAiConfigToForm(result);
        if (elements.aiConfigApiKey) elements.aiConfigApiKey.value = '';
        showMessage(elements.aiConfigMessage, 'AI 配置保存成功。', 'success');
    } catch (error) {
        showMessage(elements.aiConfigMessage, error.message, 'error');
    }
}

async function submitAiGenerate(event) {
    event.preventDefault();
    const prompt = elements.aiPrompt?.value?.trim() || '';
    if (!prompt) {
        showMessage(elements.aiGenerateMessage, '请输入生成提示词。', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('negative_prompt', elements.aiNegativePrompt?.value?.trim() || '');
    formData.append('count', String(Number(elements.aiGenerateCount?.value || 4)));
    formData.append('size', elements.aiGenerateSize?.value?.trim() || '1024x1024');
    formData.append('quality', elements.aiGenerateQuality?.value?.trim() || 'standard');
    formData.append('style', elements.aiGenerateStyle?.value?.trim() || 'vivid');

    const file = elements.aiReferenceImage?.files?.[0];
    if (file) {
        formData.append('reference_image', file);
    }

    try {
        showMessage(elements.aiGenerateMessage, '正在生成图片，请稍候...', 'info');
        const result = await request('/api/ai-assist/generate', {
            method: 'POST',
            body: formData,
        });
        const generated = result.generated || [];
        state.aiGeneratedResults = generated;
        state.aiSelectedTempIds = generated.map((item) => item.temp_id);
        renderAiGeneratedResults();
        showMessage(elements.aiGenerateMessage, `生成完成，共 ${generated.length} 张图片。`, 'success');
    } catch (error) {
        showMessage(elements.aiGenerateMessage, error.message, 'error');
    }
}

async function addAiSelectedToMaterials() {
    const selected = state.aiSelectedTempIds || [];
    if (!selected.length) {
        showMessage(elements.aiMaterialMessage, '请先选择至少一张生成图片。', 'error');
        return;
    }

    const payload = {
        temp_ids: selected,
        title_prefix: elements.aiMaterialTitlePrefix?.value?.trim() || 'AI素材',
        keywords: elements.aiMaterialKeywords?.value?.trim() || '',
        tags: elements.aiMaterialTags?.value?.trim() || 'AI',
        remark: elements.aiMaterialRemark?.value?.trim() || '',
    };

    try {
        showMessage(elements.aiMaterialMessage, '正在加入素材库...', 'info');
        const result = await request('/api/ai-assist/materials', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        showMessage(
            elements.aiMaterialMessage,
            `已加入素材库：新增 ${result.uploaded.length}，去重 ${result.duplicate_count}，失效 ${result.missing_count}。新增素材已自动审核通过。`,
            'success',
        );
    } catch (error) {
        showMessage(elements.aiMaterialMessage, error.message, 'error');
    }
}

function normalizeSourceType(value) {
    const source = String(value || '').trim().toLowerCase();
    if (source === 'crawler') return 'crawl';
    if (source === 'upload') return 'manual';
    return source;
}

function materialSourceTypeLabel(sourceType) {
    const source = normalizeSourceType(sourceType);
    const map = {
        crawl: '爬虫抓取',
        ai: 'AI 生成',
        manual: '手动上传',
    };
    if (!source) return '未知来源';
    return map[source] || `其他来源（${source}）`;
}

function materialSourceStatusClass(sourceType) {
    const source = normalizeSourceType(sourceType);
    if (source === 'ai') return 'ai';
    if (source === 'crawl') return 'enabled';
    return 'info';
}

function syncMaterialSourceQuickFilterButtons() {
    const current = normalizeSourceType(elements.materialSourceType?.value || '');
    const configs = [
        [elements.materialSourceAllButton, ''],
        [elements.materialSourceCrawlButton, 'crawl'],
        [elements.materialSourceAiButton, 'ai'],
        [elements.materialSourceManualButton, 'manual'],
    ];
    configs.forEach(([button, sourceType]) => {
        if (!button) return;
        const active = sourceType === current || (sourceType === '' && !current);
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
    });
}

async function applyMaterialSourceQuickFilter(sourceType) {
    if (!elements.materialSourceType) return;
    const normalized = normalizeSourceType(sourceType);
    elements.materialSourceType.value = normalized;
    syncMaterialSourceQuickFilterButtons();
    const filterText = normalized ? `正在按来源“${materialSourceTypeLabel(normalized)}”筛选素材...` : '正在加载全部来源素材...';
    await loadMaterials(filterText);
    await loadMaterialTags();
    showMessage(
        elements.materialFilterMessage,
        normalized ? `已按来源“${materialSourceTypeLabel(normalized)}”筛选。` : '已切换为全部来源。',
        'success',
    );
}

function renderSiteSelector() {
    if (!elements.crawlSiteSelector) return;
    if (!state.sites.length) {
        elements.crawlSiteSelector.innerHTML = '<div class="empty">暂无可选站点，请先创建并启用站点。</div>';
        return;
    }
    elements.crawlSiteSelector.innerHTML = state.sites
        .filter((site) => site.enabled)
        .map((site) => `
            <label class="checkbox-item">
                <input type="checkbox" name="crawl-site-code" value="${escapeHtml(site.code)}" />
                <span>${escapeHtml(site.name)}（${escapeHtml(site.code)}）</span>
            </label>
        `)
        .join('') || '<div class="empty">当前没有启用站点。</div>';
}

function renderSiteList() {
    if (!elements.siteList) return;
    if (!state.sites.length) {
        elements.siteList.innerHTML = '<div class="empty">暂无站点数据。</div>';
        return;
    }
    elements.siteList.innerHTML = state.sites.map((site) => `
        <article class="site-item ${state.selectedSiteId === site.id ? 'active' : ''}">
            <div class="item-header">
                <div>
                    <h3>${escapeHtml(site.name)}</h3>
                    <div class="muted">标识：${escapeHtml(site.code)}</div>
                </div>
                <span class="status ${site.enabled ? 'enabled' : 'disabled'}">${site.enabled ? '启用' : '停用'}</span>
            </div>
            <div class="meta-grid">
                <div><span class="muted">域名</span><strong>${escapeHtml(site.domain)}</strong></div>
                <div><span class="muted">抓取方式</span><strong>${escapeHtml(site.crawl_method)}</strong></div>
                <div><span class="muted">最近抓取</span><strong>${formatDate(site.last_crawled_at)}</strong></div>
                <div><span class="muted">备注</span><strong>${escapeHtml(site.remark || '无')}</strong></div>
            </div>
            <div class="rule-summary block-top">
                <span class="muted">结构化规则</span>
                ${renderRuleConfigSummary(site.rule_config || {})}
            </div>
            <div class="site-actions block-top">
                <button type="button" class="secondary" onclick="editSite(${site.id})">编辑</button>
                <button type="button" class="ghost" onclick="toggleSite(${site.id}, ${site.enabled ? 'false' : 'true'})">${site.enabled ? '停用' : '启用'}</button>
                <button type="button" class="danger" onclick="deleteSite(${site.id})">删除</button>
            </div>
        </article>
    `).join('');
}

function renderTaskList() {
    if (!elements.crawlTaskList) return;
    if (!state.tasks.length) {
        elements.crawlTaskList.innerHTML = '<div class="empty">暂无抓取任务。</div>';
        return;
    }
    elements.crawlTaskList.innerHTML = state.tasks.map((task) => `
        <article class="task-item ${state.selectedTaskId === task.id ? 'active' : ''}">
            <div class="item-header">
                <div>
                    <h3>${escapeHtml(task.keyword)}</h3>
                    <div class="muted">任务 ID：${task.id} ｜ 执行人：${escapeHtml(task.created_by)}</div>
                </div>
                <span class="status ${statusClass(task.status)}">${escapeHtml(task.status)}</span>
            </div>
            <div class="meta-grid">
                <div><span class="muted">抓取范围</span><strong>${task.target_scope === 'all' ? '全部启用站点' : escapeHtml(task.target_site_codes.join('、') || '指定站点')}</strong></div>
                <div><span class="muted">每站上限 / 页数</span><strong>${task.per_site_limit} / ${task.max_pages}</strong></div>
                <div><span class="muted">统计</span><strong>抓取 ${task.total_count} ｜ 新增 ${task.success_count} ｜ 去重 ${task.duplicate_count}</strong></div>
                <div><span class="muted">完成时间</span><strong>${formatDate(task.finished_at)}</strong></div>
            </div>
            <div class="muted block-top">${escapeHtml(task.summary_message || '暂无摘要')}</div>
            <div class="task-actions block-top">
                <button type="button" class="secondary" onclick="loadTaskDetail(${task.id})">查看详情</button>
                <button type="button" class="ghost" onclick="retryTask(${task.id})">重试任务</button>
            </div>
        </article>
    `).join('');
}

function renderTaskDetail(task) {
    if (!elements.crawlTaskDetail) return;
    state.selectedTaskId = task.id;
    if (elements.retryTaskButton) {
        elements.retryTaskButton.disabled = false;
        elements.retryTaskButton.dataset.taskId = task.id;
    }
    const logs = task.logs.length
        ? `<div class="log-list">${task.logs.map((log) => `
            <article class="log-item">
                <div class="item-header">
                    <strong>${escapeHtml(log.site_code)}</strong>
                    <span class="status ${statusClass(log.status)}">${escapeHtml(log.status)}</span>
                </div>
                <div class="muted">耗时：${log.duration_ms} ms ｜ 时间：${formatDate(log.created_at)}</div>
                <div class="block-top">${escapeHtml(log.message)}</div>
            </article>
        `).join('')}</div>`
        : '<div class="empty">暂无抓取日志。</div>';

    const materials = task.materials.length
        ? `<div class="material-list">${task.materials.map((item) => `
            <article class="material-item material-compact-card">
                <img src="/data/${encodeURI(item.local_thumbnail_path)}" alt="${escapeHtml(item.material_name)}" />
                <strong>${escapeHtml(item.material_name)}</strong>
                <div class="muted">站点：${escapeHtml(item.source_site_code)}</div>
                <div class="muted">尺寸：${item.image_width} × ${item.image_height}</div>
                <div class="muted">标签：${escapeHtml(item.tag_codes || '无')}</div>
                <div class="block-top"><a href="/data/${encodeURI(item.local_file_path)}" target="_blank">查看原图</a></div>
            </article>
        `).join('')}</div>`
        : '<div class="empty">暂无素材入库。</div>';

    elements.crawlTaskDetail.innerHTML = `
        <div class="detail-grid">
            <article>
                <div class="item-header">
                    <div>
                        <h3>${escapeHtml(task.keyword)}</h3>
                        <div class="muted">任务 ID：${task.id} ｜ 创建时间：${formatDate(task.created_at)}</div>
                    </div>
                    <span class="status ${statusClass(task.status)}">${escapeHtml(task.status)}</span>
                </div>
                <div class="meta-grid">
                    <div><span class="muted">抓取范围</span><strong>${task.target_scope === 'all' ? '全部启用站点' : escapeHtml(task.target_site_codes.join('、'))}</strong></div>
                    <div><span class="muted">每站上限 / 页数</span><strong>${task.per_site_limit} / ${task.max_pages}</strong></div>
                    <div><span class="muted">执行统计</span><strong>抓取 ${task.total_count} ｜ 新增 ${task.success_count} ｜ 去重 ${task.duplicate_count} ｜ 失败 ${task.fail_count}</strong></div>
                    <div><span class="muted">执行区间</span><strong>${formatDate(task.started_at)} ~ ${formatDate(task.finished_at)}</strong></div>
                </div>
                <div class="block-top">${escapeHtml(task.summary_message || '暂无摘要')}</div>
            </article>
            <article>
                <h3>站点抓取日志</h3>
                ${logs}
            </article>
            <article>
                <h3>入库素材</h3>
                ${materials}
            </article>
        </div>
    `;
    renderTaskList();
}

function materialFilters() {
    return {
        query_text: elements.materialQueryText?.value?.trim() || '',
        keyword: elements.materialKeyword?.value?.trim() || '',
        source_site_code: elements.materialSourceSiteCode?.value?.trim() || '',
        source_type: normalizeSourceType(elements.materialSourceType?.value || ''),
        material_status: elements.materialStatus?.value || '',
        audit_status: elements.materialAuditStatus?.value || '',
        tag: elements.materialTag?.value?.trim() || '',
    };
}

function buildQueryString(params) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
            query.set(key, value);
        }
    });
    const result = query.toString();
    return result ? `?${result}` : '';
}

function articleMaterialId(item) {
    return Number(item?.material_id ?? item?.id ?? 0);
}

function resolveMaterialById(materialId) {
    const numericId = Number(materialId);
    if (!numericId) return null;
    if (state.currentMaterial && state.currentMaterial.id === numericId) {
        return state.currentMaterial;
    }
    const listMaterial = state.materials.find((item) => item.id === numericId);
    if (listMaterial) {
        return listMaterial;
    }
    const selectedMaterial = state.articleMaterials.find((item) => item.material.id === numericId);
    return selectedMaterial ? selectedMaterial.material : null;
}

function findArticleMaterialIndex(materialId) {
    return state.articleMaterials.findIndex((item) => item.material.id === Number(materialId));
}

function isMaterialSelectedForArticle(materialId) {
    return findArticleMaterialIndex(materialId) !== -1;
}

function mergeMaterialIntoSelection(material) {
    const index = findArticleMaterialIndex(material.id);
    if (index === -1) return;
    state.articleMaterials[index] = {
        ...state.articleMaterials[index],
        material: {
            ...state.articleMaterials[index].material,
            ...material,
        },
    };
}

function ensureArticleCoverMaterialId() {
    if (!state.articleMaterials.length) {
        state.articleCoverMaterialId = null;
        return;
    }
    const exists = state.articleMaterials.some((item) => item.material.id === state.articleCoverMaterialId);
    if (!exists) {
        state.articleCoverMaterialId = state.articleMaterials[0].material.id;
    }
}

function clearArticlePreview() {
    state.articlePreview = null;
    renderArticlePreview();
}

function updateArticleEditorState() {
    if (elements.articleDraftStatus && !elements.articleDraftStatus.value) {
        elements.articleDraftStatus.value = 'editing';
    }
    const currentDraft = state.articleDrafts.find((item) => item.id === state.articleEditingDraftId);
    const isEditing = Boolean(currentDraft || state.articleEditingDraftId);

    if (elements.articleSaveButton) {
        elements.articleSaveButton.textContent = isEditing ? '更新草稿' : '保存草稿';
    }
    if (elements.articleResetButton) {
        elements.articleResetButton.textContent = isEditing ? '退出编辑' : '清空编辑器';
    }
    if (!elements.draftEditorState) {
        return;
    }
    if (isEditing) {
        elements.draftEditorState.className = 'message info';
        elements.draftEditorState.textContent = `当前正在编辑草稿 #${state.articleEditingDraftId}${currentDraft ? `：${currentDraft.article_title}` : ''}。保存时将更新原草稿。`;
        return;
    }
    elements.draftEditorState.className = 'empty';
    elements.draftEditorState.textContent = '当前为新建草稿模式，可直接保存为新草稿。';
}

function resetArticleDraftEditor() {
    state.articleEditingDraftId = null;
    if (elements.articleForm) {
        elements.articleForm.reset();
    }
    state.articleMaterials = [];
    state.articleCoverMaterialId = null;
    if (elements.articleDraftStatus) {
        elements.articleDraftStatus.value = 'editing';
    }
    clearArticlePreview();
    renderArticleSelection();
    renderMaterialList();
    if (state.currentMaterial) {
        const latestCurrent = resolveMaterialById(state.currentMaterial.id) || state.currentMaterial;
        renderMaterialDetail(latestCurrent);
    }
    updateArticleEditorState();
    showMessage(elements.articleBuilderMessage, '已清空编辑器并切换为新建草稿模式。', 'info');
}

function loadDraftDetail(draftId) {
    return request(`/api/articles/drafts/${draftId}`);
}

function getDraftById(draftId) {
    return state.articleDrafts.find((item) => item.id === Number(draftId)) || null;
}

function renderWechatConfigStatus() {
    if (!elements.wechatConfigStatus) return;
    const info = state.wechatConfigStatus;
    if (!info) {
        elements.wechatConfigStatus.className = 'empty';
        elements.wechatConfigStatus.textContent = '正在检查微信公众号配置...';
        return;
    }

    elements.wechatConfigStatus.className = 'wechat-config-panel';
    elements.wechatConfigStatus.innerHTML = `
        <div class="item-header compact-header">
            <div>
                <h3>微信公众号配置</h3>
                <div class="muted">${escapeHtml(info.message || '暂无说明')}</div>
            </div>
            <span class="status ${statusClass(info.auth_ready ? 'completed' : 'failed')}">${info.auth_ready ? '已就绪' : '未就绪'}</span>
        </div>
        <div class="meta-grid compact-grid">
            <div><span class="muted">运行模式</span><strong>${escapeHtml(info.mode || 'live')}</strong></div>
            <div><span class="muted">AppID</span><strong>${info.app_id_configured ? '已配置' : '未配置'}</strong></div>
            <div><span class="muted">AppSecret</span><strong>${info.app_secret_configured ? '已配置' : '未配置'}</strong></div>
            <div><span class="muted">发布能力</span><strong>${info.auth_ready ? '可执行发布/同步' : '请先完善配置'}</strong></div>
        </div>
    `;
}

async function loadWechatConfigStatus(message = '正在检查微信公众号配置...') {
    showMessage(elements.wechatConfigMessage, message, 'info');
    try {
        state.wechatConfigStatus = await request('/api/articles/wechat/config-status');
        renderWechatConfigStatus();
        showMessage(
            elements.wechatConfigMessage,
            state.wechatConfigStatus.message,
            state.wechatConfigStatus.auth_ready ? 'success' : 'error',
        );
        renderDraftList();
    } catch (error) {
        state.wechatConfigStatus = null;
        renderWechatConfigStatus();
        showMessage(elements.wechatConfigMessage, error.message, 'error');
    }
}

async function submitWechatConfig(event) {
    event.preventDefault();
    const payload = {
        app_id: elements.wechatAppId?.value?.trim() || '',
        app_secret: elements.wechatAppSecret?.value?.trim() || '',
    };

    try {
        showMessage(elements.wechatConfigMessage, '正在保存微信公众号配置...', 'info');
        state.wechatConfigStatus = await request('/api/articles/wechat/config', {
            method: 'PUT',
            body: JSON.stringify(payload),
        });
        renderWechatConfigStatus();
        showMessage(
            elements.wechatConfigMessage,
            state.wechatConfigStatus.message || '微信公众号配置已保存。',
            state.wechatConfigStatus.auth_ready ? 'success' : 'info',
        );
        renderDraftList();
    } catch (error) {
        showMessage(elements.wechatConfigMessage, error.message, 'error');
    }
}

function renderHistoryOverview() {
    const overview = state.historyOverview;
    if (!overview) {
        if (elements.historyArticleSummary) {
            elements.historyArticleSummary.className = 'empty';
            elements.historyArticleSummary.textContent = '正在加载文章统计...';
        }
        if (elements.historyMaterialSummary) {
            elements.historyMaterialSummary.className = 'empty';
            elements.historyMaterialSummary.textContent = '正在加载素材统计...';
        }
        if (elements.historyCrawlList) {
            elements.historyCrawlList.className = 'empty';
            elements.historyCrawlList.textContent = '正在加载抓取历史...';
        }
        if (elements.historyLogList) {
            elements.historyLogList.className = 'empty';
            elements.historyLogList.textContent = '正在加载日志中心...';
        }
        if (elements.historySiteStats) {
            elements.historySiteStats.className = 'empty';
            elements.historySiteStats.textContent = '正在加载站点素材统计...';
        }
        if (elements.historyPublishRecords) {
            elements.historyPublishRecords.className = 'empty';
            elements.historyPublishRecords.textContent = '正在加载发布记录...';
        }
        if (elements.historyTagStats) {
            elements.historyTagStats.className = 'empty';
            elements.historyTagStats.textContent = '正在加载标签统计...';
        }
        return;
    }

    if (elements.historyArticleSummary) {
        const article = overview.article_summary || {};
        elements.historyArticleSummary.className = 'history-panel';
        elements.historyArticleSummary.innerHTML = `
            <div class="item-header compact-header">
                <div>
                    <h3>文章历史</h3>
                    <div class="muted">生成、发布与草稿状态概览</div>
                </div>
                <span class="status info">文章</span>
            </div>
            <div class="meta-grid compact-grid">
                <div><span class="muted">已生成文章</span><strong>${article.total_generated || 0}</strong></div>
                <div><span class="muted">已发布文章</span><strong>${article.total_published || 0}</strong></div>
                <div><span class="muted">草稿数量</span><strong>${article.total_drafts || 0}</strong></div>
            </div>
        `;
    }

    if (elements.historyMaterialSummary) {
        const material = overview.material_summary || {};
        elements.historyMaterialSummary.className = 'history-panel';
        elements.historyMaterialSummary.innerHTML = `
            <div class="item-header compact-header">
                <div>
                    <h3>素材使用统计</h3>
                    <div class="muted">复用、未使用与总量概览</div>
                </div>
                <span class="status success">素材</span>
            </div>
            <div class="meta-grid compact-grid">
                <div><span class="muted">素材总数</span><strong>${material.total_materials || 0}</strong></div>
                <div><span class="muted">未使用素材</span><strong>${material.unused_materials || 0}</strong></div>
                <div><span class="muted">已使用素材</span><strong>${material.reused_materials || 0}</strong></div>
                <div><span class="muted">累计复用次数</span><strong>${material.total_reuse_count || 0}</strong></div>
            </div>
        `;
    }

    if (elements.historyCrawlList) {
        const items = overview.crawl_history || [];
        elements.historyCrawlList.className = 'history-panel';
        elements.historyCrawlList.innerHTML = `
            <div class="item-header compact-header">
                <div>
                    <h3>抓取历史</h3>
                    <div class="muted">最近抓取任务执行记录</div>
                </div>
                <span class="status enabled">${items.length} 条</span>
            </div>
            <div class="history-list">
                ${items.length ? items.map((item) => `
                    <article class="history-item">
                        <div class="item-header compact-header">
                            <div>
                                <strong>${escapeHtml(item.keyword || '-')}</strong>
                                <div class="muted">任务 #${item.id} ｜ 站点：${escapeHtml((item.target_site_codes || []).join('、') || '全部')}</div>
                            </div>
                            <span class="status ${statusClass(item.status)}">${escapeHtml(item.status || 'unknown')}</span>
                        </div>
                        <div class="meta-grid compact-grid">
                            <div><span class="muted">抓取/新增</span><strong>${item.total_count || 0} / ${item.success_count || 0}</strong></div>
                            <div><span class="muted">去重/失败</span><strong>${item.duplicate_count || 0} / ${item.fail_count || 0}</strong></div>
                            <div><span class="muted">执行耗时</span><strong>${item.duration_ms || 0} ms</strong></div>
                            <div><span class="muted">完成时间</span><strong>${formatDate(item.finished_at)}</strong></div>
                        </div>
                        <div class="muted block-top">${escapeHtml(item.summary_message || '暂无摘要')}</div>
                    </article>
                `).join('') : '<div class="empty">暂无抓取历史。</div>'}
            </div>
        `;
    }

    if (elements.historyLogList) {
        const items = overview.log_center || [];
        elements.historyLogList.className = 'history-panel';
        elements.historyLogList.innerHTML = `
            <div class="item-header compact-header">
                <div>
                    <h3>日志中心</h3>
                    <div class="muted">抓取、发布与异常汇总</div>
                </div>
                <span class="status info">${items.length} 条</span>
            </div>
            <div class="history-list">
                ${items.length ? items.map((item) => `
                    <article class="history-item">
                        <div class="item-header compact-header">
                            <div>
                                <strong>${escapeHtml(item.title || '-')}</strong>
                                <div class="muted">${escapeHtml(item.log_type || 'system')} ｜ 关联 ID：${item.related_id || '-'}</div>
                            </div>
                            <span class="status ${statusClass(item.status)}">${escapeHtml(item.status || 'info')}</span>
                        </div>
                        <div class="muted">${escapeHtml(item.message || '暂无日志内容')}</div>
                        <div class="muted block-top">发生时间：${formatDate(item.occurred_at)}</div>
                    </article>
                `).join('') : '<div class="empty">暂无日志中心数据。</div>'}
            </div>
        `;
    }

    if (elements.historySiteStats) {
        const items = overview.material_site_stats || [];
        elements.historySiteStats.className = 'history-panel';
        elements.historySiteStats.innerHTML = `
            <div class="item-header compact-header">
                <div>
                    <h3>站点素材统计</h3>
                    <div class="muted">每个站点素材入库与复用情况</div>
                </div>
                <span class="status success">${items.length} 个站点</span>
            </div>
            <div class="history-list">
                ${items.length ? items.map((item) => `
                    <article class="history-item">
                        <div class="item-header compact-header">
                            <div>
                                <strong>${escapeHtml(item.source_site_code || '-')}</strong>
                            </div>
                        </div>
                        <div class="meta-grid compact-grid">
                            <div><span class="muted">入库数量</span><strong>${item.material_count || 0}</strong></div>
                            <div><span class="muted">已复用素材</span><strong>${item.reused_count || 0}</strong></div>
                            <div><span class="muted">总复用次数</span><strong>${item.total_used_count || 0}</strong></div>
                        </div>
                    </article>
                `).join('') : '<div class="empty">暂无站点素材统计。</div>'}
            </div>
        `;
    }

    if (elements.historyPublishRecords) {
        const items = overview.recent_publish_records || [];
        elements.historyPublishRecords.className = 'history-panel';
        elements.historyPublishRecords.innerHTML = `
            <div class="item-header compact-header">
                <div>
                    <h3>发布记录</h3>
                    <div class="muted">最近公众号发布流水</div>
                </div>
                <span class="status completed">${items.length} 条</span>
            </div>
            <div class="history-list">
                ${items.length ? items.map((item) => `
                    <article class="history-item">
                        <div class="item-header compact-header">
                            <div>
                                <strong>${escapeHtml(item.draft_title || `草稿 #${item.draft_id}`)}</strong>
                                <div class="muted">草稿 ID：${item.draft_id} ｜ 发布时间：${formatDate(item.published_at || item.created_at)}</div>
                            </div>
                            <span class="status ${statusClass(item.publish_status)}">${escapeHtml(item.publish_status || 'unknown')}</span>
                        </div>
                        <div class="muted">${escapeHtml(item.publish_message || '暂无发布说明')}</div>
                        <div class="wechat-meta-list block-top">
                            <span class="wechat-meta-chip">微信草稿：${escapeHtml(item.wx_result?.wx_draft_id || '无')}</span>
                            <span class="wechat-meta-chip">发布单号：${escapeHtml(item.wx_result?.wx_publish_id || '无')}</span>
                        </div>
                    </article>
                `).join('') : '<div class="empty">暂无发布记录。</div>'}
            </div>
        `;
    }

    if (elements.historyTagStats) {
        const hotTags = overview.material_hot_tags || [];
        const dailyTags = overview.material_daily_tags || [];
        elements.historyTagStats.className = 'history-panel';
        elements.historyTagStats.innerHTML = `
            <div class="item-header compact-header">
                <div>
                    <h3>标签统计</h3>
                    <div class="muted">热门标签与每日标签分类概览</div>
                </div>
                <span class="status info">标签</span>
            </div>
            <div class="history-tag-grid">
                <article class="history-item">
                    <h4>热门标签</h4>
                    <div class="tag-summary block-top">
                        ${hotTags.length ? hotTags.map((item) => `<span class="tag-pill static-tag">${escapeHtml(item.tag)}<span>${item.count}</span></span>`).join('') : '<span class="muted">暂无热门标签</span>'}
                    </div>
                </article>
                <article class="history-item">
                    <h4>每日标签统计</h4>
                    <div class="history-list block-top">
                        ${dailyTags.length ? dailyTags.map((item) => `
                            <div class="history-inline-row">
                                <strong>${escapeHtml(item.date)}</strong>
                                <span class="muted">分类 ${item.tag_category_count} ｜ 热门：${escapeHtml((item.hot_tags || []).join('、') || '无')}</span>
                            </div>
                        `).join('') : '<div class="muted">暂无每日标签统计</div>'}
                    </div>
                </article>
            </div>
        `;
    }
}

async function loadHistoryOverview(message = '正在加载历史记录与统计分析...') {
    showMessage(elements.historyMessage, message, 'info');
    try {
        state.historyOverview = await request('/api/history/overview');
        renderHistoryOverview();
        showMessage(elements.historyMessage, '历史记录与统计分析已刷新。', 'success');
    } catch (error) {
        state.historyOverview = null;
        renderHistoryOverview();
        showMessage(elements.historyMessage, error.message, 'error');
    }
}

function syncDraftState(draft) {
    if (!draft) return;
    const index = state.articleDrafts.findIndex((item) => item.id === draft.id);
    if (index >= 0) {
        state.articleDrafts[index] = draft;
    } else {
        state.articleDrafts.unshift(draft);
    }

    if (state.articleEditingDraftId === draft.id) {
        applyDraftToEditor(draft);
    } else if (state.articlePreview?.id === draft.id) {
        state.articlePreview = draft;
        renderArticlePreview();
    }
    renderDraftList();
}

async function syncDraftToWechat(draftId) {
    if (state.wechatConfigStatus && !state.wechatConfigStatus.auth_ready) {
        showMessage(elements.draftListMessage, state.wechatConfigStatus.message, 'error');
        return;
    }
    try {
        showMessage(elements.draftListMessage, `正在同步草稿 ${draftId} 到微信草稿箱...`, 'info');
        const result = await request(`/api/articles/drafts/${draftId}/sync`, {
            method: 'POST',
        });
        syncDraftState(result.draft);
        await loadDrafts('正在刷新草稿箱...');
        showMessage(elements.draftListMessage, result.message || `草稿 ${draftId} 已同步到微信草稿箱。`, 'success');
    } catch (error) {
        showMessage(elements.draftListMessage, error.message, 'error');
    }
}

async function publishDraftToWechat(draftId) {
    const draft = getDraftById(draftId);
    if (state.wechatConfigStatus && !state.wechatConfigStatus.auth_ready) {
        showMessage(elements.draftListMessage, state.wechatConfigStatus.message, 'error');
        return;
    }
    if (draft?.wx_publish_id && !window.confirm(`草稿 ${draftId} 已存在发布记录，确认重新发布吗？`)) {
        return;
    }
    try {
        showMessage(elements.draftListMessage, `正在发布草稿 ${draftId} 到微信公众号...`, 'info');
        const result = await request(`/api/articles/drafts/${draftId}/publish`, {
            method: 'POST',
        });
        syncDraftState(result.draft);
        await loadDrafts('正在刷新草稿箱...');
        showMessage(elements.draftListMessage, result.message || `草稿 ${draftId} 发布请求已提交。`, 'success');
    } catch (error) {
        showMessage(elements.draftListMessage, error.message, 'error');
    }
}

function applyDraftToEditor(draft) {
    state.articleEditingDraftId = draft.id || null;
    if (elements.articleTitle) elements.articleTitle.value = draft.article_title || '';
    if (elements.articleSummary) elements.articleSummary.value = draft.article_summary || '';
    if (elements.articleAuthorName) elements.articleAuthorName.value = draft.author_name || '';
    if (elements.articleSourceUrl) elements.articleSourceUrl.value = draft.source_url || '';
    if (elements.articleTemplateCode) elements.articleTemplateCode.value = draft.template_code || 'image_gallery';
    if (elements.articleAutoSort) elements.articleAutoSort.value = 'manual';
    if (elements.articleDraftStatus) {
        elements.articleDraftStatus.value = draft.draft_status === 'pending_publish' ? 'pending_publish' : 'editing';
    }
    applyArticleResult(draft);
    updateArticleEditorState();
}

function renderDraftList() {
    if (!elements.draftList) return;
    if (!state.articleDrafts.length) {
        elements.draftList.className = 'draft-list empty';
        elements.draftList.innerHTML = '暂无草稿，请先从上方文章生成区保存一篇草稿。';
        return;
    }

    const wechatReady = Boolean(state.wechatConfigStatus?.auth_ready);
    elements.draftList.className = 'draft-list';
    elements.draftList.innerHTML = state.articleDrafts.map((draft) => {
        const imagePath = draft.cover_local_thumbnail_path || '';
        const active = state.articleEditingDraftId === draft.id;
        const coverText = draft.cover_material_name || (draft.cover_material_id ? `素材 ${draft.cover_material_id}` : '无');
        const syncDisabled = wechatReady ? '' : 'disabled';
        const publishDisabled = wechatReady ? '' : 'disabled';
        const publishText = draft.wx_publish_id ? '重新发布' : '发布';
        const wxDraftStateLabel = draft.wx_draft_id ? '已同步' : '待同步';
        const wxPublishStateLabel = draft.draft_status === 'published'
            ? '已发布'
            : (draft.draft_status === 'publishing' ? '发布中' : (draft.draft_status === 'publish_failed' ? '发布失败' : '未发布'));
        return `
            <article class="draft-item ${active ? 'active' : ''}">
                <div class="draft-cover">
                    ${imagePath ? `<img src="/data/${encodeURI(imagePath)}" alt="${escapeHtml(draft.article_title)}" />` : '<div class="empty">暂无封面</div>'}
                </div>
                <div class="draft-main">
                    <div class="item-header compact-header">
                        <div>
                            <h3>${escapeHtml(draft.article_title || '未命名草稿')}</h3>
                            <div class="muted">草稿 ID：${draft.id} ｜ 更新时间：${formatDate(draft.updated_at)}</div>
                        </div>
                        <span class="status ${statusClass(draft.draft_status)}">${escapeHtml(draft.draft_status)}</span>
                    </div>
                    <div class="meta-grid compact-grid">
                        <div><span class="muted">模板</span><strong>${escapeHtml(draft.template_code || '-')}</strong></div>
                        <div><span class="muted">素材数</span><strong>${draft.material_count || 0}</strong></div>
                        <div><span class="muted">封面</span><strong>${escapeHtml(coverText)}</strong></div>
                        <div><span class="muted">创建时间</span><strong>${formatDate(draft.created_at)}</strong></div>
                        <div><span class="muted">微信草稿</span><strong>${escapeHtml(draft.wx_draft_id || '未同步')}</strong></div>
                        <div><span class="muted">发布单号</span><strong>${escapeHtml(draft.wx_publish_id || '未发布')}</strong></div>
                    </div>
                    <div class="draft-summary block-top">${escapeHtml(draft.article_summary || '暂无摘要')}</div>
                    <div class="wechat-meta-list block-top">
                        <span class="wechat-meta-chip">微信草稿状态：${escapeHtml(wxDraftStateLabel)}</span>
                        <span class="wechat-meta-chip">微信公众号发布：${escapeHtml(wxPublishStateLabel)}</span>
                        <span class="wechat-meta-chip">发布通道：${wechatReady ? 'live 真实发布已就绪' : '配置未就绪'}</span>
                    </div>
                    <div class="task-actions block-top">
                        <button type="button" class="secondary" onclick="previewDraft(${draft.id})">预览草稿</button>
                        <button type="button" class="ghost" onclick="editDraft(${draft.id})">${active ? '重新加载编辑' : '继续编辑'}</button>
                        <button type="button" class="ghost" onclick="duplicateDraft(${draft.id})">复制草稿</button>
                        <button type="button" class="secondary" onclick="syncDraftToWechat(${draft.id})" ${syncDisabled}>同步微信草稿</button>
                        <button type="button" class="secondary" onclick="publishDraftToWechat(${draft.id})" ${publishDisabled}>${publishText}</button>
                        <button type="button" class="danger" onclick="deleteDraft(${draft.id})">删除草稿</button>
                    </div>
                </div>
            </article>
        `;
    }).join('');
}

async function loadDrafts(message = '正在加载草稿箱...') {
    showMessage(elements.draftListMessage, message, 'info');
    try {
        state.articleDrafts = await request('/api/articles/drafts');
        if (state.articleEditingDraftId && !state.articleDrafts.some((item) => item.id === state.articleEditingDraftId)) {
            state.articleEditingDraftId = null;
            if (elements.articleDraftStatus) {
                elements.articleDraftStatus.value = 'editing';
            }
        }
        renderDraftList();
        updateArticleEditorState();
        showMessage(
            elements.draftListMessage,
            state.articleDrafts.length ? `已加载 ${state.articleDrafts.length} 篇草稿。` : '当前还没有草稿。',
            state.articleDrafts.length ? 'success' : 'info',
        );
    } catch (error) {
        showMessage(elements.draftListMessage, error.message, 'error');
    }
}

async function previewDraft(draftId) {
    try {
        showMessage(elements.draftListMessage, `正在加载草稿 ${draftId} 预览...`, 'info');
        const draft = await loadDraftDetail(draftId);
        state.articlePreview = draft;
        openArticlePreviewWindow(draft, { previewTitle: `草稿 ${draftId} 预览` });
        showMessage(elements.draftListMessage, `草稿 ${draftId} 预览已在新窗口打开。`, 'success');
    } catch (error) {
        showMessage(elements.draftListMessage, error.message, 'error');
    }
}

async function editDraft(draftId) {
    const currentPage = document.body?.dataset?.page || '';
    if (currentPage !== 'articles' || !elements.articleForm) {
        window.location.href = `/articles?draft_id=${draftId}`;
        return;
    }
    const messageTarget = elements.articleBuilderMessage || elements.draftListMessage;
    try {
        showMessage(messageTarget, `正在加载草稿 ${draftId} 进入编辑器...`, 'info');
        const draft = await loadDraftDetail(draftId);
        applyDraftToEditor(draft);
        renderDraftList();
        showMessage(messageTarget, `草稿 ${draftId} 已回填到编辑器。`, 'success');
    } catch (error) {
        showMessage(messageTarget, error.message, 'error');
    }
}

async function duplicateDraft(draftId) {
    try {
        showMessage(elements.draftListMessage, `正在复制草稿 ${draftId}...`, 'info');
        const duplicate = await request(`/api/articles/drafts/${draftId}/duplicate`, {
            method: 'POST',
        });
        applyDraftToEditor(duplicate);
        await loadDrafts('正在刷新草稿箱...');
        showMessage(elements.draftListMessage, `草稿 ${draftId} 已复制为草稿 ${duplicate.id}。`, 'success');
    } catch (error) {
        showMessage(elements.draftListMessage, error.message, 'error');
    }
}

async function deleteDraft(draftId) {
    if (!window.confirm(`确认删除草稿 ${draftId} 吗？删除后将从草稿箱隐藏。`)) {
        return;
    }
    try {
        showMessage(elements.draftListMessage, `正在删除草稿 ${draftId}...`, 'info');
        await request(`/api/articles/drafts/${draftId}`, {
            method: 'DELETE',
        });
        if (state.articleEditingDraftId === draftId) {
            state.articleEditingDraftId = null;
            if (elements.articleDraftStatus) {
                elements.articleDraftStatus.value = 'editing';
            }
            updateArticleEditorState();
            showMessage(elements.articleBuilderMessage, '当前编辑草稿已删除，编辑器内容已保留，可直接另存为新草稿。', 'info');
        }
        if (state.articlePreview?.id === draftId) {
            clearArticlePreview();
        }
        await loadDrafts('正在刷新草稿箱...');
        showMessage(elements.draftListMessage, `草稿 ${draftId} 已删除。`, 'success');
    } catch (error) {
        showMessage(elements.draftListMessage, error.message, 'error');
    }
}

function applyArticleResult(result) {
    const selectedMap = new Map(state.articleMaterials.map((item) => [item.material.id, item]));
    if (Array.isArray(result.materials) && result.materials.length) {
        state.articleMaterials = result.materials
            .map((item) => {
                const materialId = articleMaterialId(item);
                const current = selectedMap.get(materialId);
                if (!materialId) return null;
                return {
                    material: {
                        ...(current?.material || {}),
                        id: materialId,
                        material_name: item.material_name || current?.material?.material_name || `素材 ${materialId}`,
                        local_thumbnail_path: item.local_thumbnail_path || current?.material?.local_thumbnail_path || item.local_file_path || '',
                        local_file_path: item.local_file_path || current?.material?.local_file_path || '',
                        source_site_code: item.source_site_code || current?.material?.source_site_code || '',
                        material_status: item.material_status || current?.material?.material_status || 'available',
                        audit_status: item.audit_status || current?.material?.audit_status || 'pending',
                        created_at: item.created_at || current?.material?.created_at || null,
                    },
                    captionText: item.caption_text || current?.captionText || '',
                };
            })
            .filter(Boolean);
    }
    state.articleCoverMaterialId = result.cover_material_id || state.articleCoverMaterialId;
    state.articlePreview = result;
    ensureArticleCoverMaterialId();
    renderArticleSelection();
    renderMaterialList();
    if (state.currentMaterial) {
        const latestCurrent = resolveMaterialById(state.currentMaterial.id) || state.currentMaterial;
        renderMaterialDetail(latestCurrent);
    }
    renderArticlePreview();
}

function renderArticleSelection() {
    if (!elements.articleSelectedMaterials || !elements.articleSelectedCount) return;
    ensureArticleCoverMaterialId();
    elements.articleSelectedCount.textContent = `已选 ${state.articleMaterials.length} 张`;
    if (!state.articleMaterials.length) {
        elements.articleSelectedMaterials.className = 'selected-material-list empty';
        elements.articleSelectedMaterials.innerHTML = '请先从素材库选择至少一张可用素材。';
        return;
    }

    elements.articleSelectedMaterials.className = 'selected-material-list';
    elements.articleSelectedMaterials.innerHTML = state.articleMaterials.map((entry, index) => {
        const material = entry.material;
        const imagePath = material.local_thumbnail_path || material.local_file_path;
        return `
            <article class="selected-material-item ${state.articleCoverMaterialId === material.id ? 'cover-active' : ''}">
                ${imagePath ? `<img src="/data/${encodeURI(imagePath)}" alt="${escapeHtml(material.material_name || `素材 ${material.id}`)}" />` : ''}
                <div class="selected-material-content">
                    <div class="item-header compact-header">
                        <div>
                            <h3>${escapeHtml(material.material_name || `素材 ${material.id}`)}</h3>
                            <div class="muted">素材 ID：${material.id} ｜ 当前顺序：${index + 1}</div>
                        </div>
                        <span class="status ${statusClass(material.material_status || 'available')}">${escapeHtml(material.material_status || 'available')}</span>
                    </div>
                    <div class="status-row">
                        <label class="selection-checkbox compact-checkbox">
                            <input type="radio" name="article-cover-material" value="${material.id}" ${state.articleCoverMaterialId === material.id ? 'checked' : ''} onchange="setArticleCoverMaterial(${material.id})" />
                            <span>设为封面</span>
                        </label>
                        <span class="status ${statusClass(material.audit_status || 'pending')}">审核：${escapeHtml(material.audit_status || 'pending')}</span>
                    </div>
                    <div class="field block-top">
                        <label for="article-caption-${material.id}">图注</label>
                        <textarea id="article-caption-${material.id}" placeholder="可选，用于正文图片说明" oninput="updateArticleCaption(${material.id}, this.value)">${escapeHtml(entry.captionText)}</textarea>
                    </div>
                    <div class="task-actions block-top">
                        <button type="button" class="ghost" onclick="moveArticleMaterial(${material.id}, -1)" ${index === 0 ? 'disabled' : ''}>上移</button>
                        <button type="button" class="ghost" onclick="moveArticleMaterial(${material.id}, 1)" ${index === state.articleMaterials.length - 1 ? 'disabled' : ''}>下移</button>
                        <button type="button" class="secondary" onclick="loadMaterialDetail(${material.id})">查看详情</button>
                        <button type="button" class="danger" onclick="removeArticleMaterial(${material.id})">移出组稿</button>
                    </div>
                </div>
            </article>
        `;
    }).join('');
}

function openArticlePreviewWindow(result, { previewTitle = '文章预览' } = {}) {
    if (!result) {
        throw new Error('当前没有可预览的文章内容。');
    }

    const materials = Array.isArray(result.materials) ? result.materials : [];
    const materialHtml = materials.length
        ? materials.map((item) => {
            const materialId = articleMaterialId(item);
            const imagePath = item.local_thumbnail_path || item.local_file_path || '';
            return `
                <article class="preview-material-card">
                    ${imagePath ? `<img src="/data/${encodeURI(imagePath)}" alt="${escapeHtml(item.material_name || `素材 ${materialId}`)}" />` : ''}
                    <div>
                        <strong>${escapeHtml(item.material_name || `素材 ${materialId}`)}</strong>
                        <div class="muted">素材 ID：${materialId} ｜ 排序：${item.sort_index || '-'}</div>
                        <div class="muted">图注：${escapeHtml(item.caption_text || '无')}</div>
                    </div>
                </article>
            `;
        }).join('')
        : '<div class="empty">当前预览没有素材数据。</div>';

    const sourceUrl = result.source_url
        ? `<a target="_blank" href="${escapeHtml(result.source_url)}">${escapeHtml(result.source_url)}</a>`
        : '无';
    const titleText = escapeHtml(result.article_title || '未命名文章');
    const summaryText = escapeHtml(result.article_summary || '暂无摘要');
    const payloadText = escapeHtml(JSON.stringify(result.publish_payload || {}, null, 2));
    const contentHtml = result.content_html || '<div class="empty">没有可展示的 HTML 内容。</div>';

    const previewWindow = window.open('', '_blank');
    if (!previewWindow) {
        throw new Error('无法打开预览窗口，请检查浏览器弹窗拦截设置。');
    }

    previewWindow.document.open();
    previewWindow.document.write(`
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>${titleText} - ${escapeHtml(previewTitle)}</title>
    <style>
        :root { color-scheme: light; }
        * { box-sizing: border-box; }
        body { margin: 0; font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #f2f5f9; color: #1b2433; }
        .wrap { max-width: 1200px; margin: 0 auto; padding: 20px; display: grid; gap: 14px; }
        .card { background: #fff; border: 1px solid #dbe6f4; border-radius: 12px; box-shadow: 0 8px 24px rgba(18,42,76,.08); padding: 16px 18px; }
        h1, h2, h3 { margin: 0; }
        .muted { color: #5f6f86; font-size: 13px; line-height: 1.7; }
        .meta { margin-top: 10px; display: grid; grid-template-columns: repeat(2, minmax(160px, 1fr)); gap: 8px 14px; }
        .meta strong { color: #1b2433; word-break: break-word; }
        .status { display: inline-flex; align-items: center; border: 1px solid #c9dbff; background: #e8f3ff; color: #1d4ed8; border-radius: 999px; padding: 2px 10px; font-size: 12px; font-weight: 700; }
        .materials { display: grid; gap: 10px; }
        .preview-material-card { display: grid; grid-template-columns: 120px minmax(0, 1fr); gap: 10px; border: 1px solid #dbe6f4; border-radius: 10px; padding: 10px; }
        .preview-material-card img { width: 100%; height: 88px; object-fit: cover; border-radius: 8px; border: 1px solid #dbe6f4; }
        .json { margin: 0; padding: 12px; border-radius: 8px; background: #1f2329; color: #dce0e6; font-size: 12px; white-space: pre-wrap; word-break: break-word; }
        .content { border: 1px solid #dbe6f4; border-radius: 10px; background: #fff; padding: 14px; min-height: 220px; overflow: auto; }
        .empty { border: 1px dashed #dcdfe6; background: #f7f8fa; border-radius: 8px; padding: 10px 12px; color: #5f6f86; font-size: 13px; }
    </style>
</head>
<body>
    <main class="wrap">
        <section class="card">
            <h1>${titleText}</h1>
            <div class="muted">${escapeHtml(previewTitle)}</div>
            <div style="margin-top:8px;"><span class="status">${escapeHtml(result.draft_status || 'preview')}</span></div>
            <div class="meta">
                <div><span class="muted">模板</span><br /><strong>${escapeHtml(result.template_code || '-')}</strong></div>
                <div><span class="muted">素材数量</span><br /><strong>${materials.length}</strong></div>
                <div><span class="muted">封面素材</span><br /><strong>${result.cover_material_id || '-'}</strong></div>
                <div><span class="muted">作者</span><br /><strong>${escapeHtml(result.author_name || '系统生成')}</strong></div>
                <div><span class="muted">来源链接</span><br /><strong>${sourceUrl}</strong></div>
                <div><span class="muted">更新时间</span><br /><strong>${escapeHtml(formatDate(result.updated_at || result.created_at))}</strong></div>
            </div>
            <div class="empty" style="margin-top:10px;">${summaryText}</div>
        </section>
        <section class="card">
            <h2>素材顺序</h2>
            <div class="materials" style="margin-top:10px;">${materialHtml}</div>
        </section>
        <section class="card">
            <h2>发布结构数据</h2>
            <pre class="json" style="margin-top:10px;">${payloadText}</pre>
        </section>
        <section class="card">
            <h2>HTML 预览</h2>
            <div class="content" style="margin-top:10px;">${contentHtml}</div>
        </section>
    </main>
</body>
</html>
    `);
    previewWindow.document.close();
    previewWindow.focus();
}

function renderArticlePreview() {
    if (!elements.articlePreviewMeta || !elements.articlePreviewHtml) return;
    if (!state.articlePreview) {
        elements.articlePreviewMeta.className = 'empty';
        elements.articlePreviewMeta.innerHTML = '尚未生成文章预览。';
        elements.articlePreviewHtml.className = 'article-html-preview empty';
        elements.articlePreviewHtml.innerHTML = '尚未生成 HTML 内容。';
        return;
    }

    const result = state.articlePreview;
    const materials = Array.isArray(result.materials) ? result.materials : [];
    const materialHtml = materials.length
        ? materials.map((item) => {
            const materialId = articleMaterialId(item);
            const imagePath = item.local_thumbnail_path || item.local_file_path || '';
            return `
                <article class="selected-material-item compact-preview-item ${result.cover_material_id === materialId ? 'cover-active' : ''}">
                    ${imagePath ? `<img src="/data/${encodeURI(imagePath)}" alt="${escapeHtml(item.material_name || `素材 ${materialId}`)}" />` : ''}
                    <div class="selected-material-content">
                        <div class="item-header compact-header">
                            <div>
                                <h3>${escapeHtml(item.material_name || `素材 ${materialId}`)}</h3>
                                <div class="muted">素材 ID：${materialId} ｜ 排序：${item.sort_index || '-'}</div>
                            </div>
                            <span class="status ${result.cover_material_id === materialId ? 'completed' : 'info'}">${result.cover_material_id === materialId ? '封面' : '正文'}</span>
                        </div>
                        <div class="muted block-top">图注：${escapeHtml(item.caption_text || '无')}</div>
                    </div>
                </article>
            `;
        }).join('')
        : '<div class="empty">当前预览没有素材数据。</div>';

    elements.articlePreviewMeta.className = '';
    elements.articlePreviewMeta.innerHTML = `
        <div class="detail-grid">
            <article>
                <div class="item-header">
                    <div>
                        <h3>${escapeHtml(result.article_title || '未命名文章')}</h3>
                        <div class="muted">状态：${escapeHtml(result.draft_status || 'preview')} ｜ 模板：${escapeHtml(result.template_code || '-')}</div>
                    </div>
                    <span class="status ${statusClass(result.draft_status || 'info')}">${escapeHtml(result.draft_status || 'preview')}</span>
                </div>
                <div class="meta-grid">
                    <div><span class="muted">封面素材</span><strong>${result.cover_material_id || '-'}</strong></div>
                    <div><span class="muted">素材数量</span><strong>${materials.length}</strong></div>
                    <div><span class="muted">作者</span><strong>${escapeHtml(result.author_name || '系统生成')}</strong></div>
                    <div><span class="muted">来源链接</span><strong class="break-all">${result.source_url ? `<a target="_blank" href="${escapeHtml(result.source_url)}">${escapeHtml(result.source_url)}</a>` : '无'}</strong></div>
                </div>
                <div class="block-top empty">${escapeHtml(result.article_summary || '暂无摘要')}</div>
            </article>
            <article>
                <h3>素材顺序</h3>
                <div class="selected-material-list compact-selected-list">${materialHtml}</div>
            </article>
            <article>
                <h3>发布结构数据</h3>
                <pre class="json-preview">${escapeHtml(JSON.stringify(result.publish_payload || {}, null, 2))}</pre>
            </article>
        </div>
    `;
    elements.articlePreviewHtml.className = 'article-html-preview';
    elements.articlePreviewHtml.innerHTML = result.content_html || '<div class="empty">没有可展示的 HTML 内容。</div>';
}

function syncArticleSelectionFromChecked() {
    const checkedIds = Array.from(document.querySelectorAll('input[name="article-material-selector"]:checked'))
        .map((node) => Number(node.value))
        .filter(Boolean);
    const existingMap = new Map(state.articleMaterials.map((item) => [item.material.id, item]));
    state.articleMaterials = checkedIds.map((materialId) => {
        const current = existingMap.get(materialId);
        const material = resolveMaterialById(materialId) || current?.material;
        if (!material) return null;
        return {
            material: {
                ...(current?.material || {}),
                ...material,
            },
            captionText: current?.captionText || '',
        };
    }).filter(Boolean);
    ensureArticleCoverMaterialId();
    clearArticlePreview();
    renderArticleSelection();
    renderMaterialList();
    if (state.currentMaterial) {
        const latestCurrent = resolveMaterialById(state.currentMaterial.id) || state.currentMaterial;
        renderMaterialDetail(latestCurrent);
    }
    showMessage(elements.articleBuilderMessage, state.articleMaterials.length ? `已同步 ${state.articleMaterials.length} 张素材进入组稿区。` : '当前没有勾选任何素材。', state.articleMaterials.length ? 'success' : 'info');
}

function quickAddArticleMaterial(materialId) {
    const material = resolveMaterialById(materialId);
    if (!material) {
        showMessage(elements.articleBuilderMessage, `无法找到素材 ${materialId}，请先刷新素材库。`, 'error');
        return;
    }
    if (isMaterialSelectedForArticle(materialId)) {
        showMessage(elements.articleBuilderMessage, `素材“${material.material_name}”已在组稿区。`, 'info');
        return;
    }
    state.articleMaterials.push({
        material: { ...material },
        captionText: '',
    });
    ensureArticleCoverMaterialId();
    clearArticlePreview();
    renderArticleSelection();
    renderMaterialList();
    if (state.currentMaterial && state.currentMaterial.id === material.id) {
        renderMaterialDetail({ ...state.currentMaterial, ...material });
    }
    showMessage(elements.articleBuilderMessage, `已将素材“${material.material_name}”加入组稿区。`, 'success');
}

function removeArticleMaterial(materialId) {
    const index = findArticleMaterialIndex(materialId);
    if (index === -1) return;
    const removed = state.articleMaterials[index];
    state.articleMaterials = state.articleMaterials.filter((item) => item.material.id !== Number(materialId));
    ensureArticleCoverMaterialId();
    clearArticlePreview();
    renderArticleSelection();
    renderMaterialList();
    if (state.currentMaterial && state.currentMaterial.id === Number(materialId)) {
        renderMaterialDetail(state.currentMaterial);
    }
    showMessage(elements.articleBuilderMessage, `已将素材“${removed.material.material_name}”移出组稿区。`, 'success');
}

function setArticleMaterialChecked(materialId, checked) {
    if (checked) {
        quickAddArticleMaterial(materialId);
        return;
    }
    removeArticleMaterial(materialId);
}

function setArticleCoverMaterial(materialId) {
    if (!isMaterialSelectedForArticle(materialId)) return;
    state.articleCoverMaterialId = Number(materialId);
    renderArticleSelection();
    showMessage(elements.articleBuilderMessage, `已将素材 ${materialId} 设为封面。`, 'info');
}

function moveArticleMaterial(materialId, step) {
    const index = findArticleMaterialIndex(materialId);
    const targetIndex = index + Number(step);
    if (index === -1 || targetIndex < 0 || targetIndex >= state.articleMaterials.length) {
        return;
    }
    const next = [...state.articleMaterials];
    const [current] = next.splice(index, 1);
    next.splice(targetIndex, 0, current);
    state.articleMaterials = next;
    clearArticlePreview();
    renderArticleSelection();
    renderMaterialList();
    showMessage(elements.articleBuilderMessage, '已调整素材顺序。', 'success');
}

function updateArticleCaption(materialId, value) {
    const index = findArticleMaterialIndex(materialId);
    if (index === -1) return;
    state.articleMaterials[index] = {
        ...state.articleMaterials[index],
        captionText: String(value || ''),
    };
}

function clearArticleSelection() {
    state.articleMaterials = [];
    state.articleCoverMaterialId = null;
    clearArticlePreview();
    renderArticleSelection();
    renderMaterialList();
    if (state.currentMaterial) {
        renderMaterialDetail(state.currentMaterial);
    }
    showMessage(elements.articleBuilderMessage, '已清空组稿区素材。', 'info');
}

function selectedMaterialIdsFromCheckboxes() {
    return Array.from(document.querySelectorAll('input[name="article-material-selector"]:checked'))
        .map((item) => Number(item.value))
        .filter((value) => Number.isFinite(value) && value > 0);
}

function selectAllVisibleMaterials() {
    const selectableMaterials = state.materials.filter((item) => item.material_status !== 'deleted');
    if (!selectableMaterials.length) {
        showMessage(elements.materialListMessage, '当前没有可全选的素材（已删除素材不可选）。', 'info');
        return;
    }

    const existingMap = new Map(state.articleMaterials.map((item) => [item.material.id, item]));
    state.articleMaterials = selectableMaterials.map((material) => {
        const current = existingMap.get(material.id);
        return {
            material: {
                ...(current?.material || {}),
                ...material,
            },
            captionText: current?.captionText || '',
        };
    });

    ensureArticleCoverMaterialId();
    clearArticlePreview();
    renderArticleSelection();
    renderMaterialList();
    if (state.currentMaterial) {
        const latestCurrent = resolveMaterialById(state.currentMaterial.id) || state.currentMaterial;
        renderMaterialDetail(latestCurrent);
    }
    showMessage(elements.materialListMessage, `已全选当前列表中 ${state.articleMaterials.length} 条可用素材。`, 'success');
}

async function bulkUpdateMaterialAction(action, actionText, { confirmMessage = '' } = {}) {
    const materialIds = selectedMaterialIdsFromCheckboxes();
    if (!materialIds.length) {
        showMessage(elements.materialListMessage, '请先勾选需要批量处理的素材。', 'error');
        return;
    }

    const finalConfirmMessage = confirmMessage ? confirmMessage.replace('{count}', String(materialIds.length)) : '';
    if (finalConfirmMessage && !window.confirm(finalConfirmMessage)) {
        return;
    }

    showMessage(elements.materialListMessage, `正在批量执行“${actionText}”操作（共 ${materialIds.length} 条）...`, 'info');
    let successCount = 0;
    let failedCount = 0;

    for (const materialId of materialIds) {
        try {
            const material = await request(`/api/materials/${materialId}/actions`, {
                method: 'POST',
                body: JSON.stringify({ action }),
            });
            if (material.material_status === 'deleted') {
                state.articleMaterials = state.articleMaterials.filter((item) => item.material.id !== material.id);
            } else {
                mergeMaterialIntoSelection(material);
            }
            successCount += 1;
        } catch (error) {
            failedCount += 1;
        }
    }

    ensureArticleCoverMaterialId();
    clearArticlePreview();
    await loadMaterials('正在刷新素材列表...');
    await loadMaterialTags();

    const resultText = `批量${actionText}完成：成功 ${successCount} 条，失败 ${failedCount} 条。`;
    showMessage(elements.materialListMessage, resultText, failedCount ? 'error' : 'success');
}

async function bulkAuditSelectedMaterials() {
    await bulkUpdateMaterialAction('audit', '审核通过');
}

async function bulkDeleteSelectedMaterials() {
    await bulkUpdateMaterialAction('delete', '删除', {
        confirmMessage: '确认批量逻辑删除选中的 {count} 条素材吗？',
    });
}

function buildArticlePayload() {
    const title = elements.articleTitle?.value.trim() || '';
    if (!title) {
        throw new Error('请输入文章标题。');
    }
    if (!state.articleMaterials.length) {
        throw new Error('请先从素材库选择至少一张素材。');
    }
    ensureArticleCoverMaterialId();
    return {
        title,
        summary: elements.articleSummary?.value.trim() || '',
        author_name: elements.articleAuthorName?.value.trim() || '',
        source_url: elements.articleSourceUrl?.value.trim() || '',
        cover_material_id: state.articleCoverMaterialId,
        template_code: elements.articleTemplateCode?.value || 'image_gallery',
        auto_sort: elements.articleAutoSort?.value || 'manual',
        materials: state.articleMaterials.map((item) => ({
            material_id: item.material.id,
            caption_text: item.captionText.trim(),
        })),
    };
}

function materialActions(material) {
    const page = document.body?.dataset?.page || '';
    if (page === 'materials' || page === 'articles') {
        return '';
    }

    const actions = [];
    actions.push(`<button type="button" class="secondary" onclick="loadMaterialDetail(${material.id})">查看详情</button>`);
    return actions.join('');
}

function syncMaterialTagSummaryToggleState() {
    if (!elements.materialTagSummary || !elements.materialTagToggleButton) return;

    const hasTags = state.materialTags.length > 0;
    if (!hasTags) {
        elements.materialTagToggleButton.hidden = true;
        elements.materialTagToggleButton.textContent = '展开';
        elements.materialTagToggleButton.setAttribute('aria-expanded', 'false');
        return;
    }

    const expanded = Boolean(state.materialTagSummaryExpanded);
    elements.materialTagSummary.classList.toggle('collapsed', !expanded);

    const hasOverflow = elements.materialTagSummary.scrollWidth > elements.materialTagSummary.clientWidth + 2;
    const showToggle = expanded || hasOverflow;
    elements.materialTagToggleButton.hidden = !showToggle;
    elements.materialTagToggleButton.textContent = expanded ? '收起' : '展开';
    elements.materialTagToggleButton.setAttribute('aria-expanded', String(expanded));
}

function toggleMaterialTagSummaryExpanded() {
    if (!state.materialTags.length) return;
    state.materialTagSummaryExpanded = !state.materialTagSummaryExpanded;
    syncMaterialTagSummaryToggleState();
}

function openMaterialDetailModal() {
    if (!elements.materialDetailModal) return;
    elements.materialDetailModal.hidden = false;
    document.body.classList.add('modal-open');
}

function closeMaterialDetailModal() {
    if (!elements.materialDetailModal) return;
    elements.materialDetailModal.hidden = true;
    document.body.classList.remove('modal-open');
}

function renderMaterialTagSummary() {
    if (!elements.materialTagSummary) return;
    if (!state.materialTags.length) {
        elements.materialTagSummary.innerHTML = '暂无标签统计。';
        elements.materialTagSummary.className = 'tag-summary empty';
        if (elements.materialTagToggleButton) {
            elements.materialTagToggleButton.hidden = true;
            elements.materialTagToggleButton.textContent = '展开';
            elements.materialTagToggleButton.setAttribute('aria-expanded', 'false');
        }
        return;
    }
    elements.materialTagSummary.className = 'tag-summary tag-summary-collapsible';
    elements.materialTagSummary.innerHTML = state.materialTags
        .map((item, index) => `<button type="button" class="tag-pill" onclick="applyTagFilterByIndex(${index})">${escapeHtml(item.tag)}<span>${item.count}</span></button>`)
        .join('');
    window.requestAnimationFrame(syncMaterialTagSummaryToggleState);
}

function renderMaterialList() {
    if (!elements.materialList || !elements.materialCount) return;

    const page = document.body?.dataset?.page || '';
    const visibleMaterials = page === 'articles'
        ? state.materials.filter((item) => item.material_status !== 'deleted' && item.audit_status === 'approved')
        : state.materials;

    const selectableCount = visibleMaterials.filter((item) => item.material_status !== 'deleted').length;
    const hasSelected = visibleMaterials.some((item) => item.material_status !== 'deleted' && isMaterialSelectedForArticle(item.id));
    if (elements.materialSelectAllButton) {
        elements.materialSelectAllButton.disabled = selectableCount === 0;
    }
    if (elements.materialBulkAuditButton) {
        elements.materialBulkAuditButton.disabled = !hasSelected;
    }
    if (elements.materialBulkDeleteButton) {
        elements.materialBulkDeleteButton.disabled = !hasSelected;
    }

    elements.materialCount.textContent = `共 ${visibleMaterials.length} 条`;
    if (!visibleMaterials.length) {
        elements.materialList.innerHTML = '<div class="empty">当前筛选条件下暂无素材。</div>';
        return;
    }

    elements.materialList.innerHTML = visibleMaterials.map((material) => {
        const imagePath = material.local_thumbnail_path || material.local_file_path || '';

        if (page === 'articles') {
            return `
        <article class="material-item ${state.selectedMaterialId === material.id ? 'active' : ''}">
            <div class="material-image-wrap">
                <button type="button" class="material-image-button" onclick="loadMaterialDetail(${material.id})" aria-label="查看素材 ${material.id} 详情">
                    <img src="/data/${encodeURI(imagePath)}" alt="${escapeHtml(material.material_name)}" />
                </button>
                <label class="selection-checkbox selection-checkbox-floating">
                    <input type="checkbox" name="article-material-selector" value="${material.id}" ${isMaterialSelectedForArticle(material.id) ? 'checked' : ''} ${material.material_status === 'deleted' ? 'disabled' : ''} onchange="setArticleMaterialChecked(${material.id}, this.checked)" />
                </label>
            </div>
        </article>
    `;
        }

        const actionHtml = page === 'materials'
            ? ''
            : `
                <div class="task-actions block-top">
                    ${materialActions(material)}
                </div>
            `;
        return `
        <article class="material-item ${state.selectedMaterialId === material.id ? 'active' : ''}">
            <div class="material-image-wrap">
                <button type="button" class="material-image-button" onclick="loadMaterialDetail(${material.id})" aria-label="查看素材 ${material.id} 详情">
                    <img src="/data/${encodeURI(imagePath)}" alt="${escapeHtml(material.material_name)}" />
                </button>
                <label class="selection-checkbox selection-checkbox-floating">
                    <input type="checkbox" name="article-material-selector" value="${material.id}" ${isMaterialSelectedForArticle(material.id) ? 'checked' : ''} ${material.material_status === 'deleted' ? 'disabled' : ''} onchange="setArticleMaterialChecked(${material.id}, this.checked)" />
                </label>
            </div>
            <div class="status-row block-top">
                <span class="status ${statusClass(material.material_status)}">${escapeHtml(material.material_status)}</span>
                <span class="status ${statusClass(material.audit_status)}">审核：${escapeHtml(material.audit_status)}</span>
                <span class="status ${materialSourceStatusClass(material.source_type)}">来源：${escapeHtml(materialSourceTypeLabel(material.source_type))}</span>
            </div>
            ${actionHtml}
        </article>
    `;
    }).join('');
}

function renderMaterialDetail(material) {
    if (!elements.materialDetail) return;
    state.selectedMaterialId = material.id;
    state.currentMaterial = material;
    mergeMaterialIntoSelection(material);
    const tagList = (material.tag_codes || '').split('|').filter(Boolean);
    const tagHtml = tagList.length
        ? `<div class="tag-summary">${tagList.map((tag) => `<span class="tag-pill static-tag">${escapeHtml(tag)}</span>`).join('')}</div>`
        : '<div class="empty">暂无标签。</div>';
    const sourcePageHtml = material.source_page_url
        ? `<a target="_blank" href="${escapeHtml(material.source_page_url)}">查看来源</a>`
        : '无';
    const taskText = material.crawl_task_id ? String(material.crawl_task_id) : '手动上传';
    const detailActions = materialActions(material);
    elements.materialDetail.innerHTML = `
        <div class="detail-grid">
            <article>
                <img class="material-detail-image" src="/data/${encodeURI(material.local_file_path)}" alt="${escapeHtml(material.material_name)}" />
            </article>
            <article>
                <div class="item-header">
                    <div>
                        <h3>${escapeHtml(material.material_name)}</h3>
                        <div class="muted">素材 ID：${material.id} ｜ 创建时间：${formatDate(material.created_at)}</div>
                    </div>
                    <span class="status ${statusClass(material.material_status)}">${escapeHtml(material.material_status)}</span>
                </div>
                <div class="status-row block-top">
                    <span class="status ${statusClass(material.audit_status)}">审核：${escapeHtml(material.audit_status)}</span>
                    <span class="status ${materialSourceStatusClass(material.source_type)}">来源：${escapeHtml(materialSourceTypeLabel(material.source_type))}</span>
                </div>
                <div class="meta-grid block-top">
                    <div><span class="muted">关键词</span><strong>${escapeHtml(material.search_keyword || '无')}</strong></div>
                    <div><span class="muted">来源站点</span><strong>${escapeHtml(material.source_site_code || '无')}</strong></div>
                    <div><span class="muted">尺寸</span><strong>${material.image_width} × ${material.image_height}</strong></div>
                    <div><span class="muted">使用次数</span><strong>${material.used_count}</strong></div>
                    <div><span class="muted">图片 Hash</span><strong class="break-all">${escapeHtml(material.image_hash)}</strong></div>
                    <div><span class="muted">抓取任务</span><strong>${escapeHtml(taskText)}</strong></div>
                    <div><span class="muted">来源页面</span><strong class="break-all">${sourcePageHtml}</strong></div>
                    <div><span class="muted">原图文件</span><strong><a target="_blank" href="/data/${encodeURI(material.local_file_path)}">打开原图</a></strong></div>
                </div>
                <div class="block-top">
                    <h3>标签</h3>
                    ${tagHtml}
                </div>
                <div class="block-top">
                    <h3>备注 / Prompt</h3>
                    <div class="empty">${escapeHtml(material.prompt_text || '无')}</div>
                </div>
                ${detailActions ? `<div class="task-actions block-top">${detailActions}</div>` : ''}
            </article>
        </div>
    `;
    if (elements.materialDetailModal) {
        openMaterialDetailModal();
    }
    renderMaterialList();
}

function selectedSiteCodes() {
    return Array.from(document.querySelectorAll('input[name="crawl-site-code"]:checked')).map((item) => item.value);
}

async function triggerSiteAiPrefill() {
    const domain = elements.domain?.value?.trim() || '';
    if (!domain) {
        showMessage(elements.siteAiPrefillMessage, '请先输入站点域名。', 'error');
        return;
    }

    if (elements.siteAiPrefillButton) {
        elements.siteAiPrefillButton.disabled = true;
    }
    try {
        showMessage(elements.siteAiPrefillMessage, '正在调用 AI 生成站点建议...', 'info');
        const result = await request('/api/sites/ai-prefill', {
            method: 'POST',
            body: JSON.stringify({ domain }),
        });
        applySiteAiSuggestionToForm(result?.suggestion || {});
        showMessage(elements.siteAiPrefillMessage, result?.message || 'AI 自动填充完成。', 'success');
        showMessage(elements.formMessage, '已根据域名自动回填站点信息，请人工确认后再保存。', 'info');
    } catch (error) {
        showMessage(elements.siteAiPrefillMessage, error.message, 'error');
    } finally {
        if (elements.siteAiPrefillButton) {
            elements.siteAiPrefillButton.disabled = false;
        }
    }
}

function fillSiteForm(site) {
    state.selectedSiteId = site.id;
    elements.siteId.value = site.id;
    elements.name.value = site.name;
    elements.code.value = site.code;
    elements.code.disabled = true;
    elements.domain.value = site.domain;
    elements.crawlMethod.value = site.crawl_method;
    elements.searchRule.value = site.search_rule;
    elements.parseRule.value = site.parse_rule;
    elements.pageRule.value = site.page_rule;
    elements.remark.value = site.remark;
    elements.enabled.value = String(site.enabled);
    applyRuleConfigToForm(site.rule_config || {});
    elements.submitButton.textContent = '更新站点';
    showMessage(elements.siteAiPrefillMessage, '');
    showMessage(elements.formMessage, `当前正在编辑站点：${site.name}`, 'info');
    renderSiteList();
}

async function loadSites() {
    showMessage(elements.listMessage, '正在加载站点列表...', 'info');
    try {
        state.sites = await request('/api/sites');
        renderSiteList();
        renderSiteSelector();
        showMessage(
            elements.listMessage,
            state.sites.length ? `已加载 ${state.sites.length} 个站点。` : '当前还没有站点，请先创建一个站点配置。',
            state.sites.length ? 'success' : 'info',
        );
    } catch (error) {
        showMessage(elements.listMessage, error.message, 'error');
    }
}

async function loadTasks() {
    showMessage(elements.crawlListMessage, '正在加载抓取任务...', 'info');
    try {
        state.tasks = await request('/api/crawl-tasks');
        renderTaskList();
        showMessage(
            elements.crawlListMessage,
            state.tasks.length ? `已加载 ${state.tasks.length} 条抓取任务。` : '暂无抓取任务。',
            state.tasks.length ? 'success' : 'info',
        );
    } catch (error) {
        showMessage(elements.crawlListMessage, error.message, 'error');
    }
}

async function loadMaterialTags() {
    state.materialTagSummaryExpanded = false;
    try {
        state.materialTags = await request('/api/materials/tags/summary');
        renderMaterialTagSummary();
    } catch (error) {
        if (!elements.materialTagSummary) return;
        elements.materialTagSummary.className = 'tag-summary empty';
        elements.materialTagSummary.textContent = error.message;
        if (elements.materialTagToggleButton) {
            elements.materialTagToggleButton.hidden = true;
            elements.materialTagToggleButton.textContent = '展开';
            elements.materialTagToggleButton.setAttribute('aria-expanded', 'false');
        }
    }
}

async function loadMaterials(message = '正在加载素材库...') {
    showMessage(elements.materialListMessage, message, 'info');
    try {
        const query = buildQueryString(materialFilters());
        syncMaterialSourceQuickFilterButtons();
        state.materials = await request(`/api/materials${query}`);
        state.articleMaterials = state.articleMaterials.map((entry) => ({
            ...entry,
            material: {
                ...entry.material,
                ...(state.materials.find((item) => item.id === entry.material.id) || {}),
            },
        }));
        renderArticleSelection();
        renderMaterialList();
        if (state.selectedMaterialId) {
            const selected = state.materials.find((item) => item.id === state.selectedMaterialId);
            if (selected) {
                renderMaterialDetail(selected);
            } else {
                state.selectedMaterialId = null;
                if (elements.materialDetail) {
                    elements.materialDetail.innerHTML = '<div class="empty">当前选中素材不在筛选结果中，请重新选择。</div>';
                }
                closeMaterialDetailModal();
            }
        }
        showMessage(
            elements.materialListMessage,
            state.materials.length ? `已加载 ${state.materials.length} 条素材。` : '当前筛选条件下暂无素材。',
            state.materials.length ? 'success' : 'info',
        );
    } catch (error) {
        showMessage(elements.materialListMessage, error.message, 'error');
    }
}

async function saveSite(event) {
    event.preventDefault();
    let ruleConfig;
    try {
        ruleConfig = collectRuleConfig();
    } catch (error) {
        showMessage(elements.formMessage, error.message, 'error');
        return;
    }
    const payload = {
        name: elements.name.value.trim(),
        code: elements.code.value.trim(),
        domain: elements.domain.value.trim(),
        enabled: elements.enabled.value === 'true',
        search_rule: elements.searchRule.value.trim(),
        parse_rule: elements.parseRule.value.trim(),
        page_rule: elements.pageRule.value.trim(),
        remark: elements.remark.value.trim(),
        crawl_method: elements.crawlMethod.value,
        rule_config: ruleConfig,
    };
    try {
        if (elements.siteId.value) {
            await request(`/api/sites/${elements.siteId.value}`, {
                method: 'PUT',
                body: JSON.stringify({
                    name: payload.name,
                    domain: payload.domain,
                    enabled: payload.enabled,
                    search_rule: payload.search_rule,
                    parse_rule: payload.parse_rule,
                    page_rule: payload.page_rule,
                    remark: payload.remark,
                    crawl_method: payload.crawl_method,
                    rule_config: payload.rule_config,
                }),
            });
            showMessage(elements.formMessage, '站点更新成功。', 'success');
        } else {
            await request('/api/sites', { method: 'POST', body: JSON.stringify(payload) });
            showMessage(elements.formMessage, '站点创建成功。', 'success');
        }
        resetSiteForm();
        await loadSites();
    } catch (error) {
        showMessage(elements.formMessage, error.message, 'error');
    }
}

async function runTest() {
    const keyword = elements.testKeyword.value.trim();
    if (!state.selectedSiteId) {
        elements.testResult.innerHTML = '<div class="test-result error">请先在站点列表中选择需要测试的站点。</div>';
        return;
    }
    if (!keyword) {
        elements.testResult.innerHTML = '<div class="test-result error">请输入测试关键词。</div>';
        return;
    }
    elements.testResult.innerHTML = '<div class="test-result info">测试抓取执行中...</div>';
    try {
        const result = await request(`/api/sites/${state.selectedSiteId}/test`, {
            method: 'POST',
            body: JSON.stringify({ keyword }),
        });
        const previews = result.preview_results.map((item) => `
            <article class="preview-item">
                <strong>${escapeHtml(item.title)}</strong>
                <div class="muted">图片地址：<a target="_blank" href="${escapeHtml(item.image_url)}">${escapeHtml(item.image_url)}</a></div>
                <div class="muted">来源页面：<a target="_blank" href="${escapeHtml(item.source_page_url)}">${escapeHtml(item.source_page_url)}</a></div>
            </article>
        `).join('');
        const ruleSummary = renderRuleConfigSummary(result.applied_rule_config || {});
        elements.testResult.innerHTML = `<div class="test-result success">${escapeHtml(result.message)}<div class="rule-summary block-top"><span class="muted">本次测试使用规则</span>${ruleSummary}</div><div class="preview-list">${previews}</div></div>`;
        await loadSites();
    } catch (error) {
        elements.testResult.innerHTML = `<div class="test-result error">${escapeHtml(error.message)}</div>`;
    }
}

async function createTask(event) {
    event.preventDefault();
    const payload = {
        keyword: elements.crawlKeyword.value.trim(),
        target_scope: elements.crawlScope.value,
        target_site_codes: selectedSiteCodes(),
        per_site_limit: Number(elements.perSiteLimit.value || 3),
        max_pages: Number(elements.maxPages.value || 1),
        created_by: elements.createdBy.value.trim() || 'system',
    };
    if (payload.target_scope === 'selected' && !payload.target_site_codes.length) {
        showMessage(elements.crawlFormMessage, '指定站点模式下至少选择一个启用站点。', 'error');
        return;
    }
    try {
        showMessage(elements.crawlFormMessage, '正在创建并执行抓取任务...', 'info');
        const detail = await request('/api/crawl-tasks', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        showMessage(elements.crawlFormMessage, '抓取任务执行完成。', 'success');
        await loadTasks();
        await loadMaterials('抓取任务完成，正在刷新素材库...');
        await loadMaterialTags();
        renderTaskDetail(detail);
    } catch (error) {
        showMessage(elements.crawlFormMessage, error.message, 'error');
    }
}

async function loadTaskDetail(taskId) {
    try {
        const detail = await request(`/api/crawl-tasks/${taskId}`);
        renderTaskDetail(detail);
    } catch (error) {
        showMessage(elements.crawlListMessage, error.message, 'error');
    }
}

async function retryTask(taskId) {
    try {
        showMessage(elements.crawlListMessage, `正在重试任务 ${taskId}...`, 'info');
        const detail = await request(`/api/crawl-tasks/${taskId}/retry`, {
            method: 'POST',
            body: JSON.stringify({ site_codes: [] }),
        });
        showMessage(elements.crawlListMessage, `任务 ${taskId} 已重试完成。`, 'success');
        await loadTasks();
        await loadMaterials('任务重试完成，正在刷新素材库...');
        await loadMaterialTags();
        renderTaskDetail(detail);
    } catch (error) {
        showMessage(elements.crawlListMessage, error.message, 'error');
    }
}

async function submitMaterialFilters(event) {
    event.preventDefault();
    syncMaterialSourceQuickFilterButtons();
    await loadMaterials('正在按条件筛选素材...');
    await loadMaterialTags();
    showMessage(elements.materialFilterMessage, '筛选条件已应用。', 'success');
}

async function uploadMaterials(event) {
    event.preventDefault();
    const files = Array.from(elements.materialUploadFiles.files || []);
    if (!files.length) {
        showMessage(elements.materialUploadMessage, '请至少选择一个图片文件。', 'error');
        return;
    }

    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    formData.append('title', elements.materialUploadTitle.value.trim());
    formData.append('keywords', elements.materialUploadKeywords.value.trim());
    formData.append('remark', elements.materialUploadRemark.value.trim());
    formData.append('tags', elements.materialUploadTags.value.trim());

    try {
        showMessage(elements.materialUploadMessage, '正在上传素材并生成缩略图...', 'info');
        const result = await request('/api/materials/upload', {
            method: 'POST',
            body: formData,
        });
        showMessage(
            elements.materialUploadMessage,
            `上传完成，新增 ${result.uploaded.length} 条，去重 ${result.duplicate_count} 条。`,
            'success',
        );
        resetMaterialUploadForm();
        await loadMaterials('上传完成，正在刷新素材库...');
        await loadMaterialTags();
        if (result.uploaded.length) {
            renderMaterialDetail(result.uploaded[0]);
        }
    } catch (error) {
        showMessage(elements.materialUploadMessage, error.message, 'error');
    }
}

async function loadMaterialDetail(materialId) {
    try {
        const material = await request(`/api/materials/${materialId}`);
        renderMaterialDetail(material);
    } catch (error) {
        showMessage(elements.materialListMessage, error.message, 'error');
    }
}

async function updateMaterialAction(materialId, action) {
    const actionTextMap = {
        favorite: '收藏',
        unfavorite: '取消收藏',
        not_recommended: '标记不推荐',
        restore: '恢复可用',
        audit: '审核通过',
        delete: '删除',
    };
    const actionText = actionTextMap[action] || action;
    if (action === 'delete' && !window.confirm('确认将该素材标记为已删除吗？')) {
        return;
    }
    try {
        showMessage(elements.materialListMessage, `正在执行“${actionText}”操作...`, 'info');
        const material = await request(`/api/materials/${materialId}/actions`, {
            method: 'POST',
            body: JSON.stringify({ action }),
        });
        if (material.material_status === 'deleted') {
            state.articleMaterials = state.articleMaterials.filter((item) => item.material.id !== material.id);
            ensureArticleCoverMaterialId();
            clearArticlePreview();
        } else {
            mergeMaterialIntoSelection(material);
        }
        showMessage(elements.materialListMessage, `素材已完成“${actionText}”操作。`, 'success');
        await loadMaterials('正在刷新素材列表...');
        await loadMaterialTags();
        renderMaterialDetail(material);
    } catch (error) {
        showMessage(elements.materialListMessage, error.message, 'error');
    }
}

async function generateArticlePreview(event) {
    event.preventDefault();
    let payload;
    try {
        payload = buildArticlePayload();
    } catch (error) {
        showMessage(elements.articleBuilderMessage, error.message, 'error');
        return;
    }

    try {
        showMessage(elements.articleBuilderMessage, '正在生成公众号文章预览...', 'info');
        const result = await request('/api/articles/preview', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        applyArticleResult(result);
        openArticlePreviewWindow(result, { previewTitle: '文章生成预览' });
        showMessage(elements.articleBuilderMessage, '文章预览已在新窗口打开。', 'success');
    } catch (error) {
        showMessage(elements.articleBuilderMessage, error.message, 'error');
    }
}

async function saveArticleDraft() {
    let payload;
    try {
        payload = buildArticlePayload();
    } catch (error) {
        showMessage(elements.articleBuilderMessage, error.message, 'error');
        return;
    }

    const draftId = Number(state.articleEditingDraftId || 0);
    const isEditing = draftId > 0;
    const requestPayload = isEditing
        ? {
            ...payload,
            content_html: state.articlePreview?.content_html || '',
            draft_status: elements.articleDraftStatus?.value || 'editing',
        }
        : payload;

    try {
        showMessage(elements.articleBuilderMessage, isEditing ? `正在更新草稿 ${draftId}...` : '正在保存文章草稿...', 'info');
        const result = await request(isEditing ? `/api/articles/drafts/${draftId}` : '/api/articles/drafts', {
            method: isEditing ? 'PUT' : 'POST',
            body: JSON.stringify(requestPayload),
        });
        applyDraftToEditor(result);
        await loadDrafts('正在刷新草稿箱...');
        showMessage(
            elements.articleBuilderMessage,
            isEditing ? `草稿 ${result.id} 已更新。` : `文章草稿已保存，草稿 ID：${result.id}`,
            'success',
        );
    } catch (error) {
        showMessage(elements.articleBuilderMessage, error.message, 'error');
    }
}

window.editSite = function(siteId) {
    const site = state.sites.find((item) => item.id === siteId);
    if (site) fillSiteForm(site);
};

window.toggleSite = async function(siteId, enabled) {
    try {
        await request(`/api/sites/${siteId}`, {
            method: 'PUT',
            body: JSON.stringify({ enabled }),
        });
        await loadSites();
        showMessage(elements.listMessage, `站点已${enabled ? '启用' : '停用'}。`, 'success');
    } catch (error) {
        showMessage(elements.listMessage, error.message, 'error');
    }
};

window.deleteSite = async function(siteId) {
    const site = state.sites.find((item) => item.id === siteId);
    if (!site) return;
    if (!window.confirm(`确认删除站点“${site.name}”吗？此操作不可恢复。`)) return;
    try {
        await request(`/api/sites/${siteId}`, { method: 'DELETE' });
        if (Number(elements.siteId.value) === siteId) resetSiteForm();
        await loadSites();
        showMessage(elements.listMessage, '站点删除成功。', 'success');
    } catch (error) {
        showMessage(elements.listMessage, error.message, 'error');
    }
};

window.loadTaskDetail = loadTaskDetail;
window.retryTask = retryTask;
window.loadMaterialDetail = loadMaterialDetail;
window.updateMaterialAction = updateMaterialAction;
window.quickAddArticleMaterial = quickAddArticleMaterial;
window.removeArticleMaterial = removeArticleMaterial;
window.setArticleMaterialChecked = setArticleMaterialChecked;
window.setArticleCoverMaterial = setArticleCoverMaterial;
window.moveArticleMaterial = moveArticleMaterial;
window.updateArticleCaption = updateArticleCaption;
window.previewDraft = previewDraft;
window.editDraft = editDraft;
window.duplicateDraft = duplicateDraft;
window.deleteDraft = deleteDraft;
window.syncDraftToWechat = syncDraftToWechat;
window.publishDraftToWechat = publishDraftToWechat;
window.applyTagFilterByIndex = async function(index) {
    const item = state.materialTags[index];
    if (!item) return;
    if (elements.materialTag) {
        elements.materialTag.value = item.tag;
    }
    await loadMaterials(`正在按标签“${item.tag}”筛选素材...`);
    showMessage(elements.materialFilterMessage, `已按标签“${item.tag}”筛选。`, 'success');
};
window.toggleAiGeneratedSelection = function(tempId, checked) {
    const normalized = String(tempId || '').trim();
    if (!normalized) return;
    const current = new Set(state.aiSelectedTempIds || []);
    if (checked) {
        current.add(normalized);
    } else {
        current.delete(normalized);
    }
    state.aiSelectedTempIds = Array.from(current);
    renderAiGeneratedResults();
};

if (elements.form) elements.form.addEventListener('submit', saveSite);
if (elements.resetButton) elements.resetButton.addEventListener('click', resetSiteForm);
if (elements.refreshButton) elements.refreshButton.addEventListener('click', loadSites);
if (elements.siteAiPrefillButton) elements.siteAiPrefillButton.addEventListener('click', triggerSiteAiPrefill);
if (elements.testButton) elements.testButton.addEventListener('click', runTest);
if (elements.crawlForm) elements.crawlForm.addEventListener('submit', createTask);
if (elements.crawlRefreshButton) elements.crawlRefreshButton.addEventListener('click', loadTasks);
if (elements.crawlResetButton) {
    elements.crawlResetButton.addEventListener('click', () => {
        elements.crawlForm.reset();
        elements.perSiteLimit.value = 3;
        elements.maxPages.value = 2;
        elements.createdBy.value = 'admin';
        showMessage(elements.crawlFormMessage, '任务表单已重置。', 'info');
    });
}
if (elements.retryTaskButton) {
    elements.retryTaskButton.addEventListener('click', () => {
        const taskId = Number(elements.retryTaskButton.dataset.taskId || 0);
        if (taskId) retryTask(taskId);
    });
}
if (elements.materialFilterForm) {
    elements.materialFilterForm.addEventListener('submit', submitMaterialFilters);
}
if (elements.materialSourceType) {
    elements.materialSourceType.addEventListener('change', syncMaterialSourceQuickFilterButtons);
    syncMaterialSourceQuickFilterButtons();
}
if (elements.materialSourceAllButton) {
    elements.materialSourceAllButton.addEventListener('click', () => applyMaterialSourceQuickFilter(''));
}
if (elements.materialSourceCrawlButton) {
    elements.materialSourceCrawlButton.addEventListener('click', () => applyMaterialSourceQuickFilter('crawl'));
}
if (elements.materialSourceAiButton) {
    elements.materialSourceAiButton.addEventListener('click', () => applyMaterialSourceQuickFilter('ai'));
}
if (elements.materialSourceManualButton) {
    elements.materialSourceManualButton.addEventListener('click', () => applyMaterialSourceQuickFilter('manual'));
}
if (elements.materialFilterResetButton) {
    elements.materialFilterResetButton.addEventListener('click', async () => {
        resetMaterialFilters();
        await loadMaterials('已重置筛选条件，正在加载全部素材...');
        await loadMaterialTags();
    });
}
if (elements.materialTagToggleButton) {
    elements.materialTagToggleButton.addEventListener('click', toggleMaterialTagSummaryExpanded);
}
if (elements.materialRefreshButton) {
    elements.materialRefreshButton.addEventListener('click', async () => {
        await loadMaterials('正在刷新素材库...');
        await loadMaterialTags();
    });
}
if (elements.materialUploadForm) {
    elements.materialUploadForm.addEventListener('submit', uploadMaterials);
}
if (elements.materialUploadResetButton) {
    elements.materialUploadResetButton.addEventListener('click', resetMaterialUploadForm);
}
if (elements.materialSelectAllButton) {
    elements.materialSelectAllButton.addEventListener('click', selectAllVisibleMaterials);
}
if (elements.materialBulkAuditButton) {
    elements.materialBulkAuditButton.addEventListener('click', bulkAuditSelectedMaterials);
}
if (elements.materialBulkDeleteButton) {
    elements.materialBulkDeleteButton.addEventListener('click', bulkDeleteSelectedMaterials);
}
if (elements.materialDetailModalCloseButton) {
    elements.materialDetailModalCloseButton.addEventListener('click', closeMaterialDetailModal);
}
if (elements.materialDetailModalBackdrop) {
    elements.materialDetailModalBackdrop.addEventListener('click', closeMaterialDetailModal);
}
if (elements.articleForm) {
    elements.articleForm.addEventListener('submit', generateArticlePreview);
}
if (elements.articleSyncSelectionButton) {
    elements.articleSyncSelectionButton.addEventListener('click', syncArticleSelectionFromChecked);
}
if (elements.articleClearSelectionButton) {
    elements.articleClearSelectionButton.addEventListener('click', clearArticleSelection);
}
if (elements.articleSaveButton) {
    elements.articleSaveButton.addEventListener('click', saveArticleDraft);
}
if (elements.articleResetButton) {
    elements.articleResetButton.addEventListener('click', resetArticleDraftEditor);
}
if (elements.draftRefreshButton) {
    elements.draftRefreshButton.addEventListener('click', () => loadDrafts('正在刷新草稿箱...'));
}
if (elements.wechatConfigForm) {
    elements.wechatConfigForm.addEventListener('submit', submitWechatConfig);
}
if (elements.wechatConfigRefreshButton) {
    elements.wechatConfigRefreshButton.addEventListener('click', () => loadWechatConfigStatus('正在刷新微信公众号配置...'));
}
if (elements.historyRefreshButton) {
    elements.historyRefreshButton.addEventListener('click', () => loadHistoryOverview('正在刷新历史记录与统计分析...'));
}
if (elements.loginForm) {
    elements.loginForm.addEventListener('submit', submitLogin);
}
if (elements.accountProfileForm) {
    elements.accountProfileForm.addEventListener('submit', submitAccountProfile);
}
if (elements.accountPasswordForm) {
    elements.accountPasswordForm.addEventListener('submit', submitPasswordReset);
    elements.accountPasswordForm.addEventListener('reset', () => {
        window.setTimeout(() => renderPasswordStrength(''), 0);
    });
}
if (elements.accountNewPassword) {
    elements.accountNewPassword.addEventListener('input', () => {
        renderPasswordStrength(elements.accountNewPassword.value);
    });
    renderPasswordStrength(elements.accountNewPassword.value || '');
}
if (elements.aiConfigForm) {
    elements.aiConfigForm.addEventListener('submit', submitAiAssistConfig);
}
if (elements.aiGenerateForm) {
    elements.aiGenerateForm.addEventListener('submit', submitAiGenerate);
}
if (elements.aiSelectAllButton) {
    elements.aiSelectAllButton.addEventListener('click', () => {
        state.aiSelectedTempIds = (state.aiGeneratedResults || []).map((item) => item.temp_id);
        renderAiGeneratedResults();
    });
}
if (elements.aiClearSelectionButton) {
    elements.aiClearSelectionButton.addEventListener('click', () => {
        state.aiSelectedTempIds = [];
        renderAiGeneratedResults();
    });
}
if (elements.aiAddMaterialButton) {
    elements.aiAddMaterialButton.addEventListener('click', addAiSelectedToMaterials);
}
if (elements.topbarLogoutButton) {
    elements.topbarLogoutButton.addEventListener('click', logoutCurrentUser);
}
if (elements.topbarUserTrigger && elements.topbarUserMenu) {
    elements.topbarUserTrigger.addEventListener('click', (event) => {
        event.stopPropagation();
        const expanded = elements.topbarUserTrigger.getAttribute('aria-expanded') === 'true';
        setUserMenuOpen(!expanded);
    });
    document.addEventListener('click', (event) => {
        if (!elements.topbarUserMenuContainer) return;
        if (!elements.topbarUserMenuContainer.contains(event.target)) {
            setUserMenuOpen(false);
        }
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            setUserMenuOpen(false);
            closeMaterialDetailModal();
        }
    });
}

async function initPage() {
    const page = document.body?.dataset?.page || 'history';
    applyTopbarUser(null);
    setUserMenuOpen(false);

    if (page === 'login') {
        const current = await loadCurrentUser();
        if (current) {
            window.location.href = '/';
        }
        return;
    }

    const current = await loadCurrentUser({ redirectOnUnauthorized: true });
    if (!current) {
        return;
    }

    if (page === 'sites') {
        resetSiteForm();
        loadSites();
        return;
    }

    if (page === 'crawl') {
        loadSites();
        loadTasks();
        return;
    }

    if (page === 'ai_assist') {
        state.aiGeneratedResults = [];
        state.aiSelectedTempIds = [];
        renderAiGeneratedResults();
        loadAiAssistConfig();
        return;
    }

    if (page === 'materials') {
        loadMaterials();
        loadMaterialTags();
        return;
    }

    if (page === 'articles') {
        renderArticleSelection();
        renderArticlePreview();
        updateArticleEditorState();
        loadMaterials();
        loadMaterialTags();

        const params = new URLSearchParams(window.location.search);
        const draftId = Number(params.get('draft_id') || 0);
        if (draftId) {
            loadDrafts('正在加载草稿箱并回填编辑器...').then(() => editDraft(draftId));
        }
        return;
    }

    if (page === 'drafts') {
        renderArticlePreview();
        loadWechatConfigStatus();
        loadDrafts();
        return;
    }

    if (page === 'history') {
        renderHistoryOverview();
        loadHistoryOverview();
        return;
    }

    if (page === 'account') {
        loadAccountProfile();
    }
}

initPage();
