// 模型配置管理页面的JavaScript逻辑
document.addEventListener('DOMContentLoaded', function() {
    // DOM元素引用
    const modelForm = document.getElementById('model-form');
    const modelList = document.getElementById('model-list');
    const formTitle = document.getElementById('form-title');
    const modelIdInput = document.getElementById('model-id');
    const cancelBtn = document.getElementById('cancel-btn');
    const resetButton = document.getElementById('reset-button');
    const refreshButton = document.getElementById('refresh-button');
    const formMessage = document.getElementById('form-message');
    const listMessage = document.getElementById('list-message');
    
    // 表单字段
    const nameInput = document.getElementById('name');
    const providerInput = document.getElementById('provider');
    const modelIdentifierInput = document.getElementById('model_identifier');
    const apiKeyInput = document.getElementById('api_key');
    const apiBaseInput = document.getElementById('api_base');
    const isDefaultInput = document.getElementById('is_default');
    const descriptionInput = document.getElementById('description');
    const extraConfigInput = document.getElementById('extra_config');
    
    // 监听提供商选择变化，动态调整API基础URL提示
    providerInput.addEventListener('change', function() {
        updateApiBasePlaceholder(this.value);
    });
    
    // 初始化时也设置一次占位符
    if (providerInput.value) {
        updateApiBasePlaceholder(providerInput.value);
    }
    
    /**
     * 根据模型提供商更新API基础URL的占位符提示
     */
    function updateApiBasePlaceholder(provider) {
        const placeholderMap = {
            'openai': 'https://api.openai.com/v1',
            'anthropic': 'https://api.anthropic.com/v1',
            'aliyun': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'zhipu': 'https://open.bigmodel.cn/api/paas/v4',
            'baidu': 'https://aip.baidubce.com/rpc/2.0/ernie_bot',
            'tencent': 'https://hunyuan.tencentcloudapi.com',
            'moonshot': 'https://api.moonshot.cn/v1',
            'deepseek': 'https://api.deepseek.com/v1',
            'minimax': 'https://api.minimaxi.com/v1',
            'stepfun': 'https://api.stepfun.com/v1',
            'other': 'https://your-provider-api-url.com/v1'
        };
        
        apiBaseInput.placeholder = placeholderMap[provider] || 'https://your-provider-api-url.com/v1';
    }

    // 页面加载时获取模型列表
    loadModelConfigs();

    // 刷新按钮
    if (refreshButton) {
        refreshButton.addEventListener('click', loadModelConfigs);
    }

    // 重置按钮
    if (resetButton) {
        resetButton.addEventListener('click', resetForm);
    }

    // 表单提交事件处理
    modelForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            name: nameInput.value,
            provider: providerInput.value,
            model_identifier: modelIdentifierInput.value,
            api_key: apiKeyInput.value,
            api_base: apiBaseInput.value || null,
            is_default: isDefaultInput.checked,
            description: descriptionInput.value,
            extra_config: extraConfigInput.value || '{}'
        };

        try {
            showMessage(formMessage, '正在保存...', 'info');
            let response;
            const modelId = modelIdInput.value;

            if (modelId) {
                // 更新现有模型
                response = await fetch(`/api/model-configs/${modelId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': getCSRFToken()
                    },
                    body: JSON.stringify(formData)
                });
            } else {
                // 创建新模型
                response = await fetch('/api/model-configs/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': getCSRFToken()
                    },
                    body: JSON.stringify(formData)
                });
            }

            if (response.ok) {
                const result = await response.json();
                showMessage(formMessage, `模型 ${result.name} 已${modelId ? '更新' : '创建'}成功！`, 'success');
                
                // 清空表单并重置为添加模式
                resetForm();
                
                // 刷新模型列表
                loadModelConfigs();
            } else {
                const errorData = await response.json();
                showMessage(formMessage, `操作失败: ${errorData.detail || '未知错误'}`, 'error');
            }
        } catch (error) {
            console.error('请求出错:', error);
            showMessage(formMessage, '网络请求失败，请稍后重试', 'error');
        }
    });

    // 取消按钮事件处理
    cancelBtn.addEventListener('click', resetForm);

    /**
     * 加载模型配置列表
     */
    async function loadModelConfigs() {
        try {
            showMessage(listMessage, '正在加载列表...', 'info');
            const response = await fetch('/api/model-configs/', {
                headers: {
                    'X-CSRF-Token': getCSRFToken()
                }
            });

            if (response.ok) {
                const models = await response.json();
                renderModelList(models);
                showMessage(listMessage, '', 'info');
            } else {
                showMessage(listMessage, '获取模型列表失败', 'error');
            }
        } catch (error) {
            console.error('加载模型列表出错:', error);
            showMessage(listMessage, '网络请求失败', 'error');
        }
    }

    /**
     * 渲染模型列表
     */
    function renderModelList(models) {
        modelList.innerHTML = '';

        if (models.length === 0) {
            modelList.innerHTML = '<div class="empty">暂无模型配置数据。</div>';
            return;
        }

        models.forEach(model => {
            const article = document.createElement('article');
            article.className = 'model-item';
            
            // 如果是默认模型，添加特殊标记
            const defaultTag = model.is_default ? '<span class="status enabled">默认</span>' : '';
            
            article.innerHTML = `
                <div class="item-header">
                    <div>
                        <h3>${escapeHtml(model.name)}</h3>
                        <div class="muted">提供商：${escapeHtml(model.provider)}</div>
                    </div>
                    ${defaultTag}
                </div>
                <div class="meta-grid">
                    <div><span class="muted">模型标识</span><strong>${escapeHtml(model.model_identifier)}</strong></div>
                    <div><span class="muted">API 地址</span><strong>${escapeHtml(model.api_base || '系统默认')}</strong></div>
                    <div><span class="muted">最后更新</span><strong>${formatDate(model.updated_at)}</strong></div>
                    <div><span class="muted">描述</span><strong>${escapeHtml(model.description || '无')}</strong></div>
                </div>
                <div class="actions block-top">
                    <button type="button" class="secondary" onclick="editModel(${model.id})">编辑</button>
                    <button type="button" class="secondary" onclick="testModelConnection(${model.id})">测试连接</button>
                    <button type="button" class="danger" onclick="deleteModel(${model.id})">删除</button>
                </div>
            `;
            
            modelList.appendChild(article);
        });
    }

    /**
     * 编辑模型
     */
    window.editModel = async function(modelId) {
        try {
            const response = await fetch(`/api/model-configs/${modelId}`, {
                headers: {
                    'X-CSRF-Token': getCSRFToken()
                }
            });

            if (response.ok) {
                const model = await response.json();
                
                // 填充表单
                modelIdInput.value = model.id;
                nameInput.value = model.name;
                providerInput.value = model.provider;
                modelIdentifierInput.value = model.model_identifier;
                apiKeyInput.value = model.api_key; 
                apiBaseInput.value = model.api_base || '';
                isDefaultInput.checked = model.is_default;
                descriptionInput.value = model.description;
                extraConfigInput.value = model.extra_config;
                
                // 更新表单标题和按钮
                formTitle.textContent = '编辑模型';
                cancelBtn.style.display = 'inline-block';
                
                // 滚动到表单
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                showMessage(formMessage, '获取模型信息失败', 'error');
            }
        } catch (error) {
            console.error('编辑模型出错:', error);
            showMessage(formMessage, '网络请求失败', 'error');
        }
    };

    /**
     * 删除模型
     */
    window.deleteModel = async function(modelId) {
        if (!confirm('确定要删除此模型配置吗？此操作不可恢复。')) {
            return;
        }

        try {
            const response = await fetch(`/api/model-configs/${modelId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRF-Token': getCSRFToken()
                }
            });

            if (response.ok) {
                showMessage(listMessage, '模型删除成功！', 'success');
                loadModelConfigs(); // 刷新列表
            } else {
                const errorData = await response.json();
                showMessage(listMessage, `删除失败: ${errorData.detail || '未知错误'}`, 'error');
            }
        } catch (error) {
            console.error('删除模型出错:', error);
            showMessage(listMessage, '网络请求失败', 'error');
        }
    };

    /**
     * 重置表单为添加模式
     */
    function resetForm() {
        modelForm.reset();
        modelIdInput.value = '';
        formTitle.textContent = '添加新模型';
        cancelBtn.style.display = 'none';
        apiKeyInput.removeAttribute('readonly'); 
        showMessage(formMessage, '', 'info');
    }

    /**
     * 显示消息提示
     */
    function showMessage(target, text, type = 'info') {
        if (!target) return;
        target.innerHTML = text ? `<div class="message ${type}">${escapeHtml(text)}</div>` : '';
        
        // 自动隐藏消息 (5秒后)
        if (text && (type === 'success' || type === 'info')) {
            setTimeout(() => {
                if (target.innerHTML.includes(escapeHtml(text))) {
                    target.innerHTML = '';
                }
            }, 5000);
        }
    }

    /**
     * 转义HTML字符以防止XSS攻击
     */
    function escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }

    /**
     * 获取CSRF令牌
     */
    function getCSRFToken() {
        return document.cookie.split('; ').find(row => row.startsWith('csrf_token='))?.split('=')[1] || '';
    }
    
    /**
     * 测试模型连接
     */
    window.testModelConnection = async function(modelId) {
        // 查找触发按钮
        const testButtons = document.querySelectorAll(`button[onclick="testModelConnection(${modelId})"]`);
        testButtons.forEach(button => {
            button.innerHTML = '测试中...';
            button.disabled = true;
        });
        
        try {
            const response = await fetch(`/api/model-configs/test-connection/${modelId}`, {
                method: 'POST',
                headers: {
                    'X-CSRF-Token': getCSRFToken()
                }
            });

            const result = await response.json();
            
            if (response.ok) {
                const messageType = result.success ? 'success' : 'warning';
                showMessage(listMessage, `${result.model_name}: ${result.message}`, messageType);
            } else {
                showMessage(listMessage, `测试失败: ${result.message || '未知错误'}`, 'error');
            }
        } catch (error) {
            console.error('测试模型连接出错:', error);
            showMessage(listMessage, '网络请求失败，请稍后重试', 'error');
        } finally {
            // 恢复按钮状态
            testButtons.forEach(button => {
                button.innerHTML = '测试连接';
                button.disabled = false;
            });
        }
    };
});