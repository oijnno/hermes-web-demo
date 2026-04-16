// FastAPI 版本的聊天界面 JavaScript

// 全局变量
let currentModel = null;
let currentSessionId = null;
let isProcessing = false;

// API 基础 URL
const API_BASE = '/api/v1';

// DOM 元素
const messageInput = document.getElementById('message-input');
const chatMessages = document.getElementById('chat-messages');
const sendButton = document.getElementById('send-button');
const loadingOverlay = document.getElementById('loading-overlay');
const currentModelElement = document.getElementById('current-model');
const modelDescriptionElement = document.getElementById('model-description');
const statusIndicator = document.getElementById('status-indicator');

// 初始化
document.addEventListener('DOMContentLoaded', async function() {
    // 从 cookie 获取会话 ID
    currentSessionId = getCookie('session_id');
    
    // 加载历史消息
    await loadHistory();
    
    // 设置输入框自动调整高度
    setupTextareaAutoResize();
    
    // 检查模型状态
    await checkModels();
    
    // 设置状态指示器
    updateStatus('ready', '准备就绪');
    
    // 聚焦到输入框
    messageInput.focus();
});

// 设置文本区域自动调整高度
function setupTextareaAutoResize() {
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
}

// 选择模型
async function selectModel(modelId) {
    const modelItem = document.querySelector(`.model-item[data-model="${modelId}"]`);
    
    // 检查模型是否可用
    if (!modelItem.classList.contains('available')) {
        showNotification('该模型当前不可用，请检查API密钥配置', 'error');
        return;
    }
    
    // 更新选中状态
    document.querySelectorAll('.model-item').forEach(item => {
        item.classList.remove('selected');
    });
    modelItem.classList.add('selected');
    
    // 更新当前模型
    currentModel = modelId;
    
    // 更新界面显示
    const modelInfo = await getModelInfo(modelId);
    currentModelElement.textContent = `${modelInfo.name} 模型`;
    modelDescriptionElement.textContent = modelInfo.description || 'AI 助手';
    
    // 更新状态
    updateStatus('ready', `已选择 ${modelInfo.name} 模型`);
    
    // 聚焦到输入框
    messageInput.focus();
    
    showNotification(`已切换到 ${modelInfo.name} 模型`, 'success');
}

// 获取模型信息
async function getModelInfo(modelId) {
    try {
        const response = await fetch(`${API_BASE}/chat/models`);
        const models = await response.json();
        
        const model = models.find(m => m.id === modelId);
        return model || { name: modelId, description: 'AI 助手' };
    } catch (error) {
        console.error('获取模型信息失败:', error);
        return { name: modelId, description: 'AI 助手' };
    }
}

// 发送消息
async function sendMessage() {
    if (!currentModel) {
        showNotification('请先选择AI模型', 'warning');
        return;
    }
    
    const message = messageInput.value.trim();
    if (!message) {
        showNotification('请输入消息内容', 'warning');
        return;
    }
    
    if (message.length > 2000) {
        showNotification('消息长度不能超过2000字符', 'error');
        return;
    }
    
    if (isProcessing) {
        showNotification('正在处理上一个请求，请稍候...', 'warning');
        return;
    }
    
    // 禁用发送按钮
    setProcessing(true);
    
    // 添加用户消息到界面
    addMessageToUI('user', message);
    
    // 清空输入框
    clearInput();
    
    try {
        // 显示加载动画
        showLoading(true);
        updateStatus('processing', 'AI正在思考...');
        
        // 发送请求到后端
        const response = await fetch(`${API_BASE}/chat/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: currentModel,
                message: message,
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `请求失败: ${response.status}`);
        }
        
        if (data.success) {
            // 更新会话 ID
            if (data.session_id && data.session_id !== currentSessionId) {
                currentSessionId = data.session_id;
                setCookie('session_id', currentSessionId, 7); // 保存7天
                document.getElementById('user-id').textContent = currentSessionId;
            }
            
            // 添加AI回复到界面
            addMessageToUI('assistant', data.response, currentModel);
            
            updateStatus('ready', '准备就绪');
            showNotification('收到AI回复', 'success');
        } else {
            throw new Error(data.error || '请求失败');
        }
        
    } catch (error) {
        console.error('发送消息失败:', error);
        
        // 显示错误消息
        addMessageToUI('assistant', 
            `抱歉，处理您的请求时出现错误：${error.message}\n\n请检查网络连接或稍后重试。`, 
            'error'
        );
        
        updateStatus('error', '请求失败');
        showNotification('发送消息失败: ' + error.message, 'error');
        
    } finally {
        // 恢复状态
        setProcessing(false);
        showLoading(false);
        
        // 滚动到底部
        scrollToBottom();
    }
}

// 添加消息到界面
function addMessageToUI(role, content, model = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const timestamp = new Date().toISOString();
    const formattedTime = datetimeFormat(timestamp);
    
    if (role === 'user') {
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${escapeHtml(content)}</div>
                <div class="message-time">${formattedTime}</div>
            </div>
        `;
    } else {
        const modelName = model ? model.toUpperCase() : 'AI';
        const modelBadge = model ? `<span class="model-badge">${model.toUpperCase()}</span>` : '';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    ${modelBadge}
                </div>
                <div class="message-text">${formatResponse(content)}</div>
                <div class="message-time">${formattedTime}</div>
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    
    // 移除欢迎消息（如果有）
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
}

// 格式化响应内容
function formatResponse(text) {
    // 转义HTML
    let formatted = escapeHtml(text);
    
    // 将代码块用pre标签包裹
    formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, function(match, lang, code) {
        return `<pre><code class="language-${lang || 'text'}">${escapeHtml(code)}</code></pre>`;
    });
    
    // 将行内代码用code标签包裹
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // 将换行符转换为br标签
    formatted = formatted.replace(/\n/g, '<br>');
    
    // 将URL转换为链接
    formatted = formatted.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    
    return formatted;
}

// 转义HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 处理键盘事件
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 清空输入框
function clearInput() {
    messageInput.value = '';
    messageInput.style.height = 'auto';
    document.getElementById('char-count').textContent = '0';
}

// 清空历史
async function clearHistory() {
    if (!currentSessionId) {
        showNotification('没有活跃的会话', 'warning');
        return;
    }
    
    if (!confirm('确定要清空所有聊天历史吗？此操作不可撤销。')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/chat/clear/${currentSessionId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `请求失败: ${response.status}`);
        }
        
        if (data.success) {
            // 清空界面消息
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">
                        <i class="fas fa-comments"></i>
                    </div>
                    <h3>聊天历史已清空</h3>
                    <p>选择左侧的AI模型开始新的对话</p>
                </div>
            `;
            
            showNotification('聊天历史已清空', 'success');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('清空历史失败:', error);
        showNotification('清空历史失败: ' + error.message, 'error');
    }
}

// 复制会话ID
function copySessionId() {
    if (!currentSessionId) {
        showNotification('没有活跃的会话', 'warning');
        return;
    }
    
    navigator.clipboard.writeText(currentSessionId).then(() => {
        showNotification('会话ID已复制到剪贴板', 'success');
    }).catch(err => {
        console.error('复制失败:', err);
        showNotification('复制失败', 'error');
    });
}

// 加载历史记录
async function loadHistory() {
    if (!currentSessionId) return;
    
    try {
        const response = await fetch(`${API_BASE}/chat/history/${currentSessionId}`);
        
        if (!response.ok) {
            // 如果会话不存在，清空会话ID
            if (response.status === 404) {
                currentSessionId = null;
                deleteCookie('session_id');
            }
            return;
        }
        
        const data = await response.json();
        
        if (data.success && data.messages && data.messages.length > 0) {
            // 清空现有消息
            chatMessages.innerHTML = '';
            
            // 添加历史消息
            data.messages.forEach(msg => {
                addMessageToUI(msg.role, msg.content, msg.model);
            });
            
            // 更新消息计数
            updateMessageCount(data.messages.length);
        }
    } catch (error) {
        console.error('加载历史记录失败:', error);
    }
}

// 检查模型状态
async function checkModels() {
    try {
        const response = await fetch(`${API_BASE}/chat/models`);
        const models = await response.json();
        
        models.forEach(model => {
            const element = document.querySelector(`.model-item[data-model="${model.id}"]`);
            if (element) {
                if (model.available) {
                    element.classList.add('available');
                    element.classList.remove('unavailable');
                    element.onclick = () => selectModel(model.id);
                } else {
                    element.classList.add('unavailable');
                    element.classList.remove('available');
                    element.onclick = null;
                }
            }
        });
    } catch (error) {
        console.error('检查模型状态失败:', error);
    }
}

// 更新消息计数
function updateMessageCount(count) {
    document.getElementById('message-count').textContent = Math.floor(count / 2);
}

// 更新状态指示器
function updateStatus(status, message) {
    const dot = statusIndicator.querySelector('.status-dot');
    const text = statusIndicator.querySelector('span');
    
    text.textContent = message;
    
    // 根据状态更新颜色
    switch(status) {
        case 'ready':
            dot.style.background = '#48bb78'; // 绿色
            break;
        case 'processing':
            dot.style.background = '#ed8936'; // 橙色
            break;
        case 'error':
            dot.style.background = '#f56565'; // 红色
            break;
        default:
            dot.style.background = '#a0aec0'; // 灰色
    }
}

// 设置处理状态
function setProcessing(processing) {
    isProcessing = processing;
    sendButton.disabled = processing;
    
    if (processing) {
        sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中';
    } else {
        sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> 发送';
    }
}

// 显示/隐藏加载动画
function showLoading(show) {
    if (show) {
        loadingOverlay.style.display = 'flex';
    } else {
        loadingOverlay.style.display = 'none';
    }
}

// Cookie 操作
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = `expires=${date.toUTCString()}`;
    document.cookie = `${name}=${value}; ${expires}; path=/`;
}

function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

// 日期时间格式化
function datetimeFormat(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 滚动到底部
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 显示通知（使用之前的实现）
function showNotification(message, type = 'info') {
    // 使用之前实现的 showNotification 函数
    // 这里简化为 alert
    alert(`${type.toUpperCase()}: ${message}`);
}