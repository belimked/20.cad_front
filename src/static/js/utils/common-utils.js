/**
 * 通用工具函数库
 * 提供DOM操作、API调用、表单处理、UI组件等通用功能
 * 版本: 1.0.0
 * 作者: AI Assistant
 */

// =================================================================================
// 全局配置管理
// =================================================================================

const AppConfig = {
    // API配置
    api: {
        baseUrl: window.location.protocol + "//" + window.location.host,
        timeout: 30000,
        retryCount: 3
    },
    
    // UI配置
    ui: {
        messageTimeout: 3000,
        loadingDelay: 100
    },
    
    // 获取API基础URL
    getApiBaseUrl() {
        return this.api.baseUrl;
    },
    
    // 设置API基础URL
    setApiBaseUrl(url) {
        this.api.baseUrl = url;
    }
};

// =================================================================================
// DOM操作工具
// =================================================================================

const DOMUtils = {
    /**
     * 获取DOM元素
     * @param {string} id - 元素ID
     * @returns {Element|null} DOM元素
     */
    getElement(id) {
        return document.getElementById(id);
    },
    
    /**
     * 批量获取元素
     * @param {string} selector - CSS选择器
     * @returns {NodeList} 元素列表
     */
    getElements(selector) {
        return document.querySelectorAll(selector);
    },
    
    /**
     * 设置元素显示状态
     * @param {string} id - 元素ID
     * @param {string} display - 显示状态
     */
    setElementDisplay(id, display) {
        const element = this.getElement(id);
        if (element) element.style.display = display;
    },
    
    /**
     * 设置元素文本内容
     * @param {string} id - 元素ID
     * @param {string} content - 文本内容
     */
    setElementContent(id, content) {
        const element = this.getElement(id);
        if (element) element.textContent = content;
    },
    
    /**
     * 设置元素HTML内容
     * @param {string} id - 元素ID
     * @param {string} html - HTML内容
     */
    setElementHTML(id, html) {
        const element = this.getElement(id);
        if (element) element.innerHTML = html;
    },
    
    /**
     * 设置元素值
     * @param {string} id - 元素ID
     * @param {any} value - 值
     */
    setElementValue(id, value) {
        const element = this.getElement(id);
        if (element) element.value = value;
    },
    
    /**
     * 获取元素值
     * @param {string} id - 元素ID
     * @returns {string} 元素值
     */
    getElementValue(id) {
        const element = this.getElement(id);
        return element ? element.value : '';
    },
    
    /**
     * 显示/隐藏元素
     * @param {string} id - 元素ID
     * @param {boolean} show - 是否显示
     */
    toggleElement(id, show) {
        this.setElementDisplay(id, show ? 'block' : 'none');
    },
    
    /**
     * 添加CSS类
     * @param {string} id - 元素ID
     * @param {string} className - CSS类名
     */
    addClass(id, className) {
        const element = this.getElement(id);
        if (element) element.classList.add(className);
    },
    
    /**
     * 移除CSS类
     * @param {string} id - 元素ID
     * @param {string} className - CSS类名
     */
    removeClass(id, className) {
        const element = this.getElement(id);
        if (element) element.classList.remove(className);
    }
};

// =================================================================================
// API调用工具
// =================================================================================

const APIUtils = {
    /**
     * 统一API调用处理
     * @param {string} url - API地址
     * @param {Object} options - 请求选项
     * @returns {Promise} API响应数据
     */
    async call(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: AppConfig.api.timeout
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            console.log(`API调用: ${finalOptions.method} ${url}`);
            
            // 创建AbortController用于超时控制
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), finalOptions.timeout);
            
            const response = await fetch(url, {
                ...finalOptions,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            console.log(`API响应状态: ${response.status}`);
            if (!response.ok) {
                throw new Error(`网络错误，状态码: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('API调用成功:', data);
            return data;
        } catch (error) {
            console.error('API调用失败:', error);
            
            // 处理不同类型的错误
            if (error.name === 'AbortError') {
                throw new Error('请求超时，请稍后重试');
            } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('网络连接失败，请检查网络设置');
            }
            
            throw error;
        }
    },
    
    /**
     * GET请求快捷方法
     * @param {string} url - API地址
     * @returns {Promise} API响应数据
     */
    async get(url) {
        return this.call(url, { method: 'GET' });
    },
    
    /**
     * POST请求快捷方法
     * @param {string} url - API地址
     * @param {Object} data - 请求数据
     * @returns {Promise} API响应数据
     */
    async post(url, data) {
        return this.call(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * PUT请求快捷方法
     * @param {string} url - API地址
     * @param {Object} data - 请求数据
     * @returns {Promise} API响应数据
     */
    async put(url, data) {
        return this.call(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * DELETE请求快捷方法
     * @param {string} url - API地址
     * @returns {Promise} API响应数据
     */
    async delete(url) {
        return this.call(url, { method: 'DELETE' });
    },
    
    /**
     * 显示API错误信息
     * @param {string} containerId - 容器ID
     * @param {Error} error - 错误对象
     * @param {string} actionName - 操作名称
     */
    showApiError(containerId, error, actionName = '操作') {
        const container = DOMUtils.getElement(containerId);
        if (container) {
            const errorHtml = `
                <div class="alert alert-danger">
                    <h5><i class="bi bi-exclamation-triangle"></i> ${actionName}失败</h5>
                    <p>${error.message}</p>
                    <p>请检查网络连接并<a href="javascript:location.reload()" class="alert-link">刷新页面</a>重试。</p>
                </div>
            `;
            
            if (container.tagName === 'UL' || container.tagName === 'OL') {
                container.innerHTML = `<li class="list-group-item">${errorHtml}</li>`;
            } else {
                container.innerHTML = errorHtml;
            }
        }
    },
    
    /**
     * 设置加载状态
     * @param {string} loadingElementId - 加载元素ID
     * @param {boolean} isLoading - 是否加载中
     */
    setLoadingState(loadingElementId, isLoading) {
        DOMUtils.setElementDisplay(loadingElementId, isLoading ? 'inline-block' : 'none');
    }
};

// =================================================================================
// 表单处理工具
// =================================================================================

const FormUtils = {
    /**
     * 批量获取表单数据
     * @param {Array} fieldIds - 字段ID数组
     * @returns {Object} 表单数据对象
     */
    getFormData(fieldIds) {
        const data = {};
        fieldIds.forEach(id => {
            data[id] = DOMUtils.getElementValue(id);
        });
        return data;
    },
    
    /**
     * 获取表单对象的所有数据
     * @param {string} formId - 表单ID
     * @returns {Object} 表单数据对象
     */
    getFormDataByForm(formId) {
        const form = DOMUtils.getElement(formId);
        const data = {};
        
        if (form) {
            const formData = new FormData(form);
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
        }
        
        return data;
    },
    
    /**
     * 验证必填字段
     * @param {Object} fields - 字段对象
     * @param {Function} errorCallback - 错误回调函数
     * @returns {boolean} 验证结果
     */
    validateRequired(fields, errorCallback) {
        const emptyFields = [];
        Object.entries(fields).forEach(([key, value]) => {
            if (!value || value.toString().trim() === '') {
                emptyFields.push(key);
            }
        });
        
        if (emptyFields.length > 0) {
            if (errorCallback) {
                errorCallback(`以下字段为必填：${emptyFields.join('、')}`);
            }
            return false;
        }
        return true;
    },
    
    /**
     * 验证邮箱格式
     * @param {string} email - 邮箱地址
     * @returns {boolean} 验证结果
     */
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    /**
     * 重置表单和模态框
     * @param {string} formId - 表单ID
     * @param {Object} modalInstance - 模态框实例
     */
    resetFormAndModal(formId, modalInstance) {
        const form = DOMUtils.getElement(formId);
        if (form) form.reset();
        if (modalInstance) modalInstance.hide();
    },
    
    /**
     * 批量填充表单数据
     * @param {Object} fieldMap - 字段映射对象
     */
    fillFormData(fieldMap) {
        Object.entries(fieldMap).forEach(([fieldId, value]) => {
            DOMUtils.setElementValue(fieldId, value || '');
        });
    },
    
    /**
     * 禁用/启用表单
     * @param {string} formId - 表单ID
     * @param {boolean} disabled - 是否禁用
     */
    setFormDisabled(formId, disabled) {
        const form = DOMUtils.getElement(formId);
        if (form) {
            const elements = form.elements;
            for (let element of elements) {
                element.disabled = disabled;
            }
        }
    }
};

// =================================================================================
// 模态框工具
// =================================================================================

const ModalUtils = {
    /**
     * 设置模态框基本信息
     * @param {string} titleId - 标题元素ID
     * @param {string} title - 标题文本
     * @param {string} editModeId - 编辑模式元素ID
     * @param {string} mode - 模式值
     * @param {string} originalIdId - 原始ID元素ID
     * @param {string} originalId - 原始ID值
     */
    setupModal(titleId, title, editModeId, mode, originalIdId, originalId) {
        DOMUtils.setElementContent(titleId, title);
        DOMUtils.setElementValue(editModeId, mode);
        DOMUtils.setElementValue(originalIdId, originalId || '');
    },
    
    /**
     * 显示确认对话框
     * @param {string} message - 确认消息
     * @param {Function} callback - 确认回调函数
     * @param {string} title - 标题
     */
    showConfirm(message, callback, title = '确认操作') {
        if (window.bootstrap && window.bootstrap.Modal) {
            // 如果有Bootstrap模态框，使用模态框
            // 这里可以扩展实现自定义确认对话框
            const confirmed = confirm(`${title}\n\n${message}`);
            if (confirmed && callback) callback();
        } else {
            // 使用原生确认对话框
            const confirmed = confirm(`${title}\n\n${message}`);
            if (confirmed && callback) callback();
        }
    },
    
    /**
     * 创建并显示模态框
     * @param {Object} options - 模态框配置
     */
    createModal(options = {}) {
        const {
            id = 'dynamicModal',
            title = '提示',
            body = '',
            showFooter = true,
            buttons = [
                { text: '取消', class: 'btn-secondary', dismiss: true },
                { text: '确定', class: 'btn-primary', callback: null }
            ]
        } = options;
        
        // 创建模态框HTML
        const modalHtml = `
            <div class="modal fade" id="${id}" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">${body}</div>
                        ${showFooter ? `
                            <div class="modal-footer">
                                ${buttons.map(btn => `
                                    <button type="button" class="btn ${btn.class}" 
                                            ${btn.dismiss ? 'data-bs-dismiss="modal"' : ''}>
                                        ${btn.text}
                                    </button>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        // 添加到页面
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // 初始化并显示
        const modalElement = DOMUtils.getElement(id);
        const modal = new bootstrap.Modal(modalElement);
        
        // 绑定按钮事件
        buttons.forEach((btn, index) => {
            if (btn.callback) {
                const buttonElement = modalElement.querySelectorAll('.modal-footer .btn')[index];
                buttonElement.addEventListener('click', btn.callback);
            }
        });
        
        // 模态框关闭时清理
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
        });
        
        modal.show();
        return modal;
    }
};

// =================================================================================
// 消息提示工具
// =================================================================================

const MessageUtils = {
    /**
     * 创建消息提示
     * @param {string} message - 消息内容
     * @param {string} type - 消息类型 (success, error, warning, info)
     * @param {number} timeout - 自动关闭时间
     * @param {Object} options - 额外选项
     */
    createAlert(message, type = 'success', timeout = AppConfig.ui.messageTimeout, options = {}) {
        const {
            position = 'top-end',
            closable = true,
            autoClose = true
        } = options;
        
        const alertEl = document.createElement('div');
        const typeClassMap = {
            success: 'alert-success',
            error: 'alert-danger',
            warning: 'alert-warning',
            info: 'alert-info'
        };
        
        const iconMap = {
            success: 'bi-check-circle',
            error: 'bi-exclamation-triangle',
            warning: 'bi-exclamation-triangle',
            info: 'bi-info-circle'
        };
        
        const alertClass = typeClassMap[type] || 'alert-info';
        const icon = iconMap[type] || 'bi-info-circle';
        
        alertEl.className = `alert ${alertClass} ${closable ? 'alert-dismissible' : ''} position-fixed m-3`;
        alertEl.style.zIndex = '9999';
        
        // 设置位置
        const positions = {
            'top-start': { top: '20px', left: '20px' },
            'top-end': { top: '20px', right: '20px' },
            'bottom-start': { bottom: '20px', left: '20px' },
            'bottom-end': { bottom: '20px', right: '20px' },
            'top-center': { top: '20px', left: '50%', transform: 'translateX(-50%)' },
            'bottom-center': { bottom: '20px', left: '50%', transform: 'translateX(-50%)' }
        };
        
        const pos = positions[position] || positions['top-end'];
        Object.assign(alertEl.style, pos);
        
        alertEl.setAttribute('role', 'alert');
        
        const closeButton = closable ? `
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        ` : '';
        
        alertEl.innerHTML = `
            <i class="bi ${icon} me-2"></i>${message}
            ${closeButton}
        `;
        
        document.body.appendChild(alertEl);
        
        // 自动关闭
        if (autoClose && timeout > 0) {
            setTimeout(() => {
                if (alertEl.parentNode) {
                    alertEl.remove();
                }
            }, timeout);
        }
        
        return alertEl;
    },
    
    /**
     * 显示成功消息
     * @param {string} message - 消息内容
     * @param {Object} options - 选项
     */
    showSuccess(message, options = {}) {
        return this.createAlert(message, 'success', AppConfig.ui.messageTimeout, options);
    },
    
    /**
     * 显示错误消息
     * @param {string} message - 消息内容
     * @param {Object} options - 选项
     */
    showError(message, options = {}) {
        return this.createAlert(message, 'error', AppConfig.ui.messageTimeout, options);
    },
    
    /**
     * 显示警告消息
     * @param {string} message - 消息内容
     * @param {Object} options - 选项
     */
    showWarning(message, options = {}) {
        return this.createAlert(message, 'warning', AppConfig.ui.messageTimeout, options);
    },
    
    /**
     * 显示信息消息
     * @param {string} message - 消息内容
     * @param {Object} options - 选项
     */
    showInfo(message, options = {}) {
        return this.createAlert(message, 'info', AppConfig.ui.messageTimeout, options);
    },
    
    /**
     * 清除所有消息
     */
    clearAll() {
        const alerts = document.querySelectorAll('.alert.position-fixed');
        alerts.forEach(alert => alert.remove());
    }
};

// =================================================================================
// 数据处理工具
// =================================================================================

const DataUtils = {
    /**
     * 深度克隆对象
     * @param {any} obj - 要克隆的对象
     * @returns {any} 克隆后的对象
     */
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        
        const cloned = {};
        for (let key in obj) {
            if (obj.hasOwnProperty(key)) {
                cloned[key] = this.deepClone(obj[key]);
            }
        }
        return cloned;
    },
    
    /**
     * 对象数组去重
     * @param {Array} array - 对象数组
     * @param {string} key - 去重依据的键
     * @returns {Array} 去重后的数组
     */
    uniqueByKey(array, key) {
        const seen = new Set();
        return array.filter(item => {
            const keyValue = item[key];
            if (seen.has(keyValue)) {
                return false;
            }
            seen.add(keyValue);
            return true;
        });
    },
    
    /**
     * 格式化文件大小
     * @param {number} bytes - 字节数
     * @returns {string} 格式化后的大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    /**
     * 格式化日期时间
     * @param {Date|string} date - 日期对象或字符串
     * @param {string} format - 格式字符串
     * @returns {string} 格式化后的日期时间
     */
    formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';
        
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    }
};

// =================================================================================
// 工具函数导出（兼容性支持）
// =================================================================================

// 为了向后兼容，保留原来的简单函数
function showSuccess(message) {
    MessageUtils.showSuccess(message);
}

function showError(message) {
    MessageUtils.showError(message);
}

// 全局导出工具对象
window.AppConfig = AppConfig;
window.DOMUtils = DOMUtils;
window.APIUtils = APIUtils;
window.FormUtils = FormUtils;
window.ModalUtils = ModalUtils;
window.MessageUtils = MessageUtils;
window.DataUtils = DataUtils;

// 兼容性函数导出
window.showSuccess = showSuccess;
window.showError = showError;

console.log('通用工具函数库已加载完成'); 