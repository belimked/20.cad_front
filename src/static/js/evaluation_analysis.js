// 评估分析系统 JavaScript 模块
// 全局变量
let currentTaskId = null;
let fileId = null;
let debugMode = false; // 调试模式开关
let debugLogs = []; // 调试日志数组

// DOM 元素
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const uploadBtn = document.getElementById('uploadBtn');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultContainer = document.getElementById('resultContainer');
const resultSummary = document.getElementById('resultSummary');

// 输入目录文件相关元素
const refreshInputFiles = document.getElementById('refreshInputFiles');
const inputFilesLoading = document.getElementById('inputFilesLoading');
const inputFilesList = document.getElementById('inputFilesList');
const noInputFiles = document.getElementById('noInputFiles');
const inputFileInfo = document.getElementById('inputFileInfo');
const selectedInputFile = document.getElementById('selectedInputFile');
const analyzeInputFileBtn = document.getElementById('analyzeInputFileBtn');

// 全局变量
let selectedInputFileName = null;

// 调试功能
function debugLog(message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
        timestamp,
        message,
        data: data ? JSON.stringify(data, null, 2) : null
    };
    debugLogs.push(logEntry);
    
    if (debugMode) {
        console.log(`[DEBUG ${timestamp}] ${message}`, data);
    }
    
    // 限制日志数量，防止内存泄漏
    if (debugLogs.length > 100) {
        debugLogs = debugLogs.slice(-100);
    }
}

// 切换调试模式
function toggleDebugMode() {
    debugMode = !debugMode;
    console.log(`调试模式 ${debugMode ? '开启' : '关闭'}`);
    
    if (debugMode) {
        // 显示调试面板
        showDebugPanel();
    } else {
        // 隐藏调试面板
        hideDebugPanel();
    }
}

// 显示调试面板
function showDebugPanel() {
    // 如果已存在调试面板，先移除
    const existingPanel = document.getElementById('debugPanel');
    if (existingPanel) {
        existingPanel.remove();
    }

    const debugPanel = document.createElement('div');
    debugPanel.id = 'debugPanel';
    debugPanel.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        width: 400px;
        max-height: 500px;
        background: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        z-index: 9999;
        overflow-y: auto;
        font-family: monospace;
        font-size: 12px;
    `;

    debugPanel.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <strong>调试面板</strong>
            <button onclick="hideDebugPanel()" style="background: none; border: none; font-size: 16px; cursor: pointer;">×</button>
        </div>
        <div>
            <button onclick="clearDebugLogs()" style="margin-right: 5px;">清空日志</button>
            <button onclick="exportDebugLogs()">导出日志</button>
        </div>
        <div id="debugLogContainer" style="margin-top: 10px; max-height: 300px; overflow-y: auto;">
            ${formatDebugLogs()}
        </div>
    `;

    document.body.appendChild(debugPanel);
}

// 隐藏调试面板
function hideDebugPanel() {
    const debugPanel = document.getElementById('debugPanel');
    if (debugPanel) {
        debugPanel.remove();
    }
}

// 格式化调试日志
function formatDebugLogs() {
    if (debugLogs.length === 0) {
        return '<div style="color: #666;">暂无日志</div>';
    }

    return debugLogs.map(log => `
        <div style="margin-bottom: 8px; padding: 5px; background: white; border-radius: 3px;">
            <div style="color: #666; font-size: 10px;">${log.timestamp}</div>
            <div style="margin: 2px 0;">${log.message}</div>
            ${log.data ? `<pre style="font-size: 10px; color: #555; margin: 2px 0;">${log.data}</pre>` : ''}
        </div>
    `).join('');
}

// 清空调试日志
function clearDebugLogs() {
    debugLogs = [];
    updateDebugPanel();
}

// 导出调试日志
function exportDebugLogs() {
    const logText = debugLogs.map(log => 
        `[${log.timestamp}] ${log.message}${log.data ? '\n' + log.data : ''}`
    ).join('\n\n');

    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `debug_logs_${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// 更新调试面板
function updateDebugPanel() {
    const container = document.getElementById('debugLogContainer');
    if (container) {
        container.innerHTML = formatDebugLogs();
        container.scrollTop = container.scrollHeight; // 滚动到底部
    }
}

// 显示错误模态框
function showErrorModal(htmlContent) {
    // 移除现有的错误模态框
    const existingModal = document.getElementById('errorModal');
    if (existingModal) {
        existingModal.remove();
    }

    const modal = document.createElement('div');
    modal.id = 'errorModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;

    modal.innerHTML = `
        <div style="background: white; padding: 20px; border-radius: 10px; max-width: 600px; max-height: 80vh; overflow-y: auto;">
            ${htmlContent}
            <div style="text-align: center; margin-top: 20px;">
                <button onclick="closeErrorModal()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">关闭</button>
                <button onclick="toggleDebugMode()" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px;">开启调试</button>
            </div>
        </div>
    `;

    // 点击模态框背景关闭
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeErrorModal();
        }
    });

    document.body.appendChild(modal);
}

// 关闭错误模态框
function closeErrorModal() {
    const modal = document.getElementById('errorModal');
    if (modal) {
        modal.remove();
    }
}

// 处理选择的文件
function handleFile(file) {
    if (!file.name.endsWith('.json')) {
        alert('请选择JSON格式的文件');
        return;
    }
    if (file.size > 100 * 1024 * 1024) {
        alert('文件大小不能超过100MB');
        return;
    }

    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'block';

    // 保存文件对象
    window.selectedFile = file;
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 更新进度
function updateProgress(step, percentage, text) {
    // 更新步骤状态
    for (let i = 1; i <= 4; i++) {
        const stepElement = document.getElementById(`step${i}`);
        if (i <= step) {
            stepElement.classList.add('active');
        } else {
            stepElement.classList.remove('active');
        }
    }

    // 更新进度条
    progressBar.style.width = percentage + '%';
    progressText.textContent = text;
}

// 获取输入目录文件列表
async function loadInputFiles() {
    debugLog('开始获取输入目录文件列表');
    
    // 显示加载状态
    inputFilesLoading.style.display = 'block';
    inputFilesList.style.display = 'none';
    noInputFiles.style.display = 'none';
    
    try {
        const response = await fetch('/api/evaluation/input-files');
        debugLog('收到输入文件列表响应', { 
            status: response.status, 
            statusText: response.statusText,
            ok: response.ok
        });
        
        if (!response.ok) {
            let errorDetail = '';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || '';
                debugLog('获取文件列表失败 - 解析到错误数据', errorData);
            } catch (e) {
                errorDetail = await response.text();
                debugLog('获取文件列表失败 - 无法解析JSON，获取文本', { errorText: errorDetail });
            }
            throw new Error(`获取文件列表失败 (${response.status}): ${errorDetail}`);
        }
        
        const result = await response.json();
        debugLog('获取文件列表成功', result);
        
        // 隐藏加载状态
        inputFilesLoading.style.display = 'none';
        
        if (!result.files || result.files.length === 0) {
            // 显示无文件提示
            noInputFiles.style.display = 'block';
            inputFilesList.style.display = 'none';
        } else {
            // 显示文件列表
            displayInputFiles(result.files);
            inputFilesList.style.display = 'block';
            noInputFiles.style.display = 'none';
        }
        
    } catch (error) {
        debugLog('获取输入文件列表异常', { 
            error: error.message, 
            name: error.name, 
            stack: error.stack 
        });
        
        // 隐藏加载状态
        inputFilesLoading.style.display = 'none';
        
        // 显示错误信息
        noInputFiles.style.display = 'block';
        noInputFiles.innerHTML = `
            <i class="bi bi-exclamation-triangle text-danger" style="font-size: 2rem;"></i>
            <p class="mt-2 text-danger">获取文件列表失败</p>
            <p class="text-muted small">${error.message}</p>
        `;
        inputFilesList.style.display = 'none';
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            console.error('网络连接失败，请检查服务器状态');
        }
    }
}

// 显示输入文件列表
function displayInputFiles(files) {
    inputFilesList.innerHTML = files.map(file => `
        <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" 
             onclick="selectInputFile('${file.name}')" style="cursor: pointer;">
            <div>
                <i class="bi bi-file-earmark-text text-primary me-2"></i>
                <span>${file.name}</span>
                <small class="text-muted d-block">${formatFileSize(file.size)} • ${formatFileDate(file.modified)}</small>
            </div>
            <i class="bi bi-chevron-right text-muted"></i>
        </div>
    `).join('');
}

// 选择输入文件
function selectInputFile(fileName) {
    selectedInputFileName = fileName;
    selectedInputFile.textContent = fileName;
    inputFileInfo.style.display = 'block';
    
    // 重置文件上传信息（如果有的话）
    fileInfo.style.display = 'none';
    
    debugLog('选择了输入文件', { fileName });
}

// 使用输入文件开始分析
async function analyzeInputFile() {
    if (!selectedInputFileName) {
        alert('请先选择一个文件');
        return;
    }
    
    try {
        progressContainer.style.display = 'block';
        resultContainer.style.display = 'none';
        updateProgress(1, 25, '正在初始化分析...');
        
        // 调用API直接分析输入目录文件
        const response = await fetch('/api/evaluation/analyze-input-file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_name: selectedInputFileName })
        });
        
        if (!response.ok) {
            let errorDetail = '';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || '';
            } catch (e) {
                errorDetail = await response.text();
            }
            throw new Error(`分析请求失败 (${response.status}): ${errorDetail}`);
        }
        
        const result = await response.json();
        currentTaskId = result.task_id;
        
        updateProgress(2, 50, '正在进行失败分析...');
        
        // 等待分析完成
        await waitForAnalysis(currentTaskId);
        
        updateProgress(4, 100, '分析完成！');
        
        // 显示结果
        await showResults(currentTaskId);
        
    } catch (error) {
        debugLog('分析输入文件失败', { error: error.message });
        
        // 显示详细的错误信息
        const errorHtml = `
            <div style="max-width: 500px; text-align: left;">
                <h4>分析失败</h4>
                <p><strong>错误信息:</strong> ${error.message}</p>
                <br>
                <small>请尝试以下解决方案：<br>
                1. 检查输入目录中的文件格式<br>
                2. 确认服务器正在运行<br>
                3. 刷新文件列表重试</small>
            </div>
        `;
        
        showErrorModal(errorHtml);
        progressContainer.style.display = 'none';
    }
}

// 格式化文件日期
function formatFileDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return dateString;
    }
}

// 清理HTML内容，修复可能的格式问题
function cleanHtmlContent(htmlContent) {
    console.log(`开始清理HTML内容，原始长度: ${htmlContent.length}`);
    console.log(`HTML前200字符: ${htmlContent.substring(0, 200)}`);
    
    try {
        let cleanedContent = htmlContent;
        
        // 1. 检测并处理未解析的模板字符串
        const templateStringPattern = /\$\{\{([^}]+)\}\}/g;
        let matches = cleanedContent.match(templateStringPattern);
        if (matches && matches.length > 0) {
            console.log(`检测到 ${matches.length} 个未解析的模板字符串`);
            
            // 对于包含大量模板字符串的内容，采用更激进的修复策略
            if (matches.length > 10) {
                console.warn('检测到大量未解析的模板字符串，采用激进清理策略');
                
                // 完全移除或替换JavaScript代码块中的模板字符串
                cleanedContent = cleanedContent.replace(/<script[^>]*>[\s\S]*?\$\{.*?[\s\S]*?<\/script>/gi, 
                    '<script>// JavaScript代码包含模板字符串错误，已被移除</script>');
                
                // 修复HTML内容中的模板字符串
                cleanedContent = cleanedContent
                    // 移除所有模板字符串，替换为占位符
                    .replace(/\$\{\{[^}]*\}\}/g, '[数据]')
                    .replace(/\$\{[^}]*\}/g, '[值]')
                    // 修复JSON对象中的语法错误
                    .replace(/\}\{/g, '},{')
                    // 修复其他常见问题
                    .replace(/\{\{[^}]*\}\}/g, '{数据}');
            } else {
                // 尝试修复常见的模板字符串模式
                cleanedContent = cleanedContent
                    // 修复双花括号模板语法 ${{variable}} -> ${variable}
                    .replace(/\$\{\{([^}]+)\}\}/g, '${$1}')
                    // 处理嵌套花括号问题
                    .replace(/\{\{([^{}]*)\}\}/g, '{$1}')
                    // 修复JavaScript模板字符串中的语法错误
                    .replace(/\$\{([^}]*)\$\{([^}]*)\}\}/g, '${$1}${$2}')
                    // 处理未闭合的模板字符串
                    .replace(/\$\{([^}]*$)/g, '${$1}')
                    // 修复JSON对象中的语法错误
                    .replace(/\}\{/g, '},{');
            }
            
            console.log(`模板字符串修复完成`);
        }
        
        // 2. 处理JavaScript代码块中的语法错误
        const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
        cleanedContent = cleanedContent.replace(scriptRegex, (match, scriptContent) => {
            try {
                // 如果脚本内容包含模板字符串或其他问题，完全移除或替换
                if (scriptContent.includes('${') || 
                    scriptContent.includes('{{') || 
                    scriptContent.includes('}{') ||
                    scriptContent.includes('Unexpected token')) {
                    
                    console.warn('检测到有问题的JavaScript代码，将其替换为安全的占位符');
                    
                    // 检查是否是图表相关的代码
                    if (scriptContent.includes('Chart') || scriptContent.includes('chart')) {
                        return `<script>
// 原始图表代码被移除以避免语法错误
console.log('图表代码已被安全替换');
// 如果需要图表功能，请检查服务器端模板渲染
</script>`;
                    }
                    
                    // 检查是否是数据处理相关的代码
                    if (scriptContent.includes('data') || scriptContent.includes('records')) {
                        return `<script>
// 原始数据处理代码被移除以避免语法错误
console.log('数据处理代码已被安全替换');
// 数据将从HTML内容中直接读取显示
</script>`;
                    }
                    
                    // 对于其他未知的脚本，完全移除
                    return `<script>
// 原始脚本内容包含语法错误，已被移除
console.log('脚本已被安全替换以避免语法错误');
</script>`;
                }
                
                // 尝试基本的语法修复
                let fixedScript = scriptContent
                    // 修复对象定义中的语法错误
                    .replace(/,(\s*})/g, '$1')
                    // 修复数组定义中的语法错误
                    .replace(/,(\s*])/g, '$1')
                    // 修复字符串连接问题
                    .replace(/\+\s*\+/g, '+')
                    // 修复未闭合的字符串
                    .replace(/(['"])[^'"]*$/gm, '$1$&$1')
                    // 移除明显有问题的行
                    .replace(/.*\$\{.*\n?/g, '// 移除了包含模板字符串的行\n');
                
                // 验证修复后的JavaScript
                try {
                    new Function(fixedScript);
                    return `<script>${fixedScript}</script>`;
                } catch (syntaxError) {
                    console.warn('JavaScript语法验证失败，完全移除脚本:', syntaxError.message);
                    // 如果还是有语法错误，完全移除脚本内容
                    return `<script>
// 原始脚本包含无法修复的语法错误，已被移除
console.warn('脚本内容已被移除：${syntaxError.message}');
</script>`;
                }
            } catch (error) {
                console.warn('JavaScript修复过程出错:', error.message);
                return `<script>
// 脚本处理过程中出现错误，已被安全替换
console.error('脚本处理错误：${error.message}');
</script>`;
            }
        });
        
        // 3. 处理CSS代码块
        const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;
        cleanedContent = cleanedContent.replace(styleRegex, (match, styleContent) => {
            try {
                // 修复CSS语法错误
                let fixedStyle = styleContent
                    // 修复缺失的分号
                    .replace(/([^;{}])\s*}/g, '$1;}')
                    // 修复重复的分号
                    .replace(/;;+/g, ';')
                    // 移除空的CSS规则
                    .replace(/[^{}]+\{\s*\}/g, '');
                
                return `<style>${fixedStyle}</style>`;
            } catch (error) {
                console.warn('CSS修复过程出错:', error.message);
                return match;
            }
        });
        
        // 4. 验证HTML结构
        const parser = new DOMParser();
        const doc = parser.parseFromString(cleanedContent, 'text/html');
        const parserErrors = doc.querySelectorAll('parsererror');
        
        if (parserErrors.length > 0) {
            console.warn('HTML解析发现错误:', parserErrors[0].textContent);
            // 尝试基本的HTML修复
            cleanedContent = cleanedContent
                // 修复未闭合的标签
                .replace(/<([a-z]+)([^>]*)(?<!\/)\s*>/gi, '<$1$2>')
                // 修复属性值引号问题
                .replace(/(\w+)=([^"'\s>]+)/g, '$1="$2"')
                // 移除破损的标签
                .replace(/<[^>]*[<>][^>]*>/g, '');
        }
        
        // 5. 处理HTML中的事件处理器，避免调用不存在的函数
        cleanedContent = cleanedContent.replace(/onclick\s*=\s*["']([^"']*)["']/gi, (match, onclickCode) => {
            // 检查是否调用了可能不存在的函数
            if (onclickCode.includes('showChartData')) {
                // 提取chartType参数
                const chartTypeMatch = onclickCode.match(/showChartData\(["']?([^"'\)]+)["']?\)/);
                const chartType = chartTypeMatch ? chartTypeMatch[1] : 'unknown';
                console.warn('替换showChartData调用:', onclickCode);
                return `onclick="showChartData('${chartType}')"`;
            } else if (onclickCode.includes('toggleDetails')) {
                // 提取ID参数
                const idMatch = onclickCode.match(/toggleDetails\(["']?([^"'\)]+)["']?\)/);
                const targetId = idMatch ? idMatch[1] : 'unknown';
                console.warn('替换toggleDetails调用:', onclickCode);
                return `onclick="toggleDetails('${targetId}')"`;
            } else if (onclickCode.includes('filterData') || 
                       onclickCode.includes('searchData') ||
                       onclickCode.includes('${')) {
                console.warn('移除有问题的onclick事件:', onclickCode);
                return 'onclick="console.log(\'交互功能已被禁用以避免错误\'); event.preventDefault();"';
            }
            return match;
        });
        
        // 6. 添加必要的JavaScript函数定义（作为安全的占位符）
                 const safeFunctionsScript = `
<script>
// 安全的占位符函数，防止引用错误
window.showChartData = function(chartType) {
    console.log('尝试显示图表数据:', chartType);
    
    // 尝试找到相关的图表容器
    const chartContainers = document.querySelectorAll('[data-chart="' + chartType + '"], #' + chartType + ', .' + chartType);
    if (chartContainers.length > 0) {
        chartContainers[0].scrollIntoView({ behavior: 'smooth' });
        showMessage('已定位到 ' + chartType + ' 图表区域', 'info');
    } else {
        showMessage('图表数据查看功能需要完整报告支持，请下载查看详细数据', 'warning');
    }
};

window.toggleDetails = function(id) {
    console.log('切换详情显示:', id);
    const element = document.getElementById(id);
    if (element) {
        const isHidden = element.style.display === 'none' || element.classList.contains('d-none');
        if (isHidden) {
            element.style.display = '';
            element.classList.remove('d-none');
            element.classList.add('show');
        } else {
            element.style.display = 'none';
            element.classList.add('d-none');
            element.classList.remove('show');
        }
    } else {
        console.warn('找不到ID为 ' + id + ' 的元素');
        showMessage('详情面板未找到', 'warning');
    }
};

window.filterData = function(filter) {
    console.log('数据筛选请求:', filter);
    showMessage('数据筛选功能需要完整报告支持，请下载完整版本使用高级功能', 'info');
};

window.searchData = function(term) {
    console.log('数据搜索请求:', term);
    // 简单的页面内搜索
    if (term && term.trim()) {
        const found = window.find(term.trim());
        if (found) {
            showMessage('找到搜索结果: ' + term, 'success');
        } else {
            showMessage('未找到搜索结果: ' + term, 'warning');
        }
    }
};

// 简单的消息显示函数（如果父页面的showMessage不可用）
window.showMessage = window.showMessage || function(message, type) {
    console.log('[' + (type || 'info').toUpperCase() + '] ' + message);
    
    // 创建简单的提示
    const notification = document.createElement('div');
    notification.style.cssText = 'position:fixed;top:20px;right:20px;background:#007bff;color:white;padding:10px 15px;border-radius:4px;z-index:9999;max-width:300px;';
    if (type === 'warning') notification.style.background = '#ffc107';
    if (type === 'error') notification.style.background = '#dc3545';
    if (type === 'success') notification.style.background = '#28a745';
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
};

// 通用的错误处理
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.warn('页面脚本错误已被捕获:', {
        message: msg,
        source: url,
        line: lineNo,
        column: columnNo,
        error: error
    });
    return true; // 阻止默认的错误处理
};

// 未捕获的Promise错误
window.addEventListener('unhandledrejection', function(event) {
    console.warn('未处理的Promise错误已被捕获:', event.reason);
    event.preventDefault();
});

console.log('安全占位符函数已加载 - 报告交互功能已启用');
</script>`;
        
        // 在body结束标签前插入安全函数
        if (cleanedContent.includes('</body>')) {
            cleanedContent = cleanedContent.replace('</body>', safeFunctionsScript + '\n</body>');
        } else {
            cleanedContent += safeFunctionsScript;
        }
        
        console.log(`HTML内容清理完成，清理后长度: ${cleanedContent.length}`);
        return cleanedContent;
        
    } catch (error) {
        console.error('HTML内容清理过程中发生错误:', error);
        console.log('返回原始HTML内容');
        return htmlContent;
    }
}

// 上传文件
async function uploadFile(file) {
    debugLog('开始上传文件', { fileName: file.name, fileSize: file.size });
    
    try {
        const formData = new FormData();
        formData.append('file', file);

        debugLog('发送上传请求', { url: '/api/evaluation/upload' });
        const response = await fetch('/api/evaluation/upload', {
            method: 'POST',
            body: formData
        });

        debugLog('收到上传响应', { 
            status: response.status, 
            statusText: response.statusText,
            ok: response.ok
        });

        if (!response.ok) {
            let errorDetail = '';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || '';
                debugLog('上传失败 - 解析到错误数据', errorData);
            } catch (e) {
                errorDetail = await response.text();
                debugLog('上传失败 - 无法解析JSON，获取文本', { errorText: errorDetail });
            }
            throw new Error(`文件上传失败 (${response.status}): ${errorDetail}`);
        }

        const result = await response.json();
        debugLog('上传成功', result);
        
        if (!result.file_id) {
            throw new Error('服务器未返回文件ID');
        }
        return result.file_id;
    } catch (error) {
        debugLog('上传文件异常', { 
            error: error.message, 
            name: error.name, 
            stack: error.stack 
        });
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('网络连接失败，请检查服务器状态');
        }
        throw error;
    }
}

// 开始分析
async function startAnalysis(fileId) {
    debugLog('开始分析请求', { fileId });
    
    try {
        const requestBody = { file_id: fileId };
        debugLog('发送分析请求', requestBody);
        
        const response = await fetch('/api/evaluation/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        debugLog('收到分析响应', { 
            status: response.status, 
            statusText: response.statusText,
            ok: response.ok
        });

        if (!response.ok) {
            let errorDetail = '';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || '';
                debugLog('分析失败 - 解析到错误数据', errorData);
            } catch (e) {
                errorDetail = await response.text();
                debugLog('分析失败 - 无法解析JSON，获取文本', { errorText: errorDetail });
            }
            throw new Error(`分析请求失败 (${response.status}): ${errorDetail}`);
        }

        const result = await response.json();
        debugLog('分析请求成功', result);
        
        if (!result.task_id) {
            throw new Error('服务器未返回任务ID');
        }
        return result.task_id;
    } catch (error) {
        debugLog('开始分析异常', { 
            error: error.message, 
            name: error.name, 
            stack: error.stack 
        });
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('网络连接失败，请检查服务器状态');
        }
        throw error;
    }
}

// 等待分析完成
async function waitForAnalysis(taskId) {
    debugLog('开始等待分析完成', { taskId });
    
    let attempts = 0;
    const maxAttempts = 300; // 最多等待5分钟
    
    while (attempts < maxAttempts) {
        try {
            debugLog(`状态查询 - 第${attempts + 1}次尝试`);
            
            const response = await fetch(`/api/evaluation/status/${taskId}`);
            
            debugLog('收到状态查询响应', { 
                status: response.status, 
                statusText: response.statusText,
                ok: response.ok
            });
            
            if (!response.ok) {
                let errorDetail = '';
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorData.message || '';
                    debugLog('状态查询失败 - 解析到错误数据', errorData);
                } catch (e) {
                    errorDetail = await response.text();
                    debugLog('状态查询失败 - 无法解析JSON，获取文本', { errorText: errorDetail });
                }
                throw new Error(`状态查询失败 (${response.status}): ${errorDetail}`);
            }
            
            const status = await response.json();
            debugLog('任务状态', status);

            if (status.status === 'completed') {
                debugLog('分析已完成');
                break;
            } else if (status.status === 'failed') {
                const errorMsg = status.message || status.error || '分析过程中发生未知错误';
                debugLog('分析失败', { errorMsg, fullStatus: status });
                throw new Error(`分析失败: ${errorMsg}`);
            }

            // 根据状态更新进度
            if (status.status === 'running') {
                updateProgress(3, 75, '正在计算质量指标...');
            }

            await new Promise(resolve => setTimeout(resolve, 1000));
            attempts++;
        } catch (error) {
            debugLog('等待分析异常', { 
                attempt: attempts + 1,
                error: error.message, 
                name: error.name, 
                stack: error.stack 
            });
            
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('网络连接失败，请检查服务器状态');
            }
            throw error;
        }
    }
    
    if (attempts >= maxAttempts) {
        debugLog('分析超时', { attempts, maxAttempts });
        throw new Error('分析超时，请稍后重试');
    }
}

// 显示结果
async function showResults(taskId) {
    try {
        const response = await fetch(`/api/evaluation/result/${taskId}`);
        
        if (!response.ok) {
            let errorDetail = '';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || '';
            } catch (e) {
                errorDetail = await response.text();
            }
            throw new Error(`获取结果失败 (${response.status}): ${errorDetail}`);
        }
        
        const result = await response.json();
        
        // 调试：打印完整的返回数据
        console.log('API返回的完整数据:', result);
        console.log('数据类型:', typeof result);
        console.log('是否有metrics:', result.metrics);
        console.log('metrics类型:', typeof result.metrics);
        
        // 数据验证和修复
        if (!result || typeof result !== 'object') {
            throw new Error('服务器返回的数据格式无效');
        }
        
        // 设置默认值
        const totalRecords = result.total_records || 0;
        const successRate = result.metrics?.success_rate ?? 0;
        const averageScore = result.metrics?.average_score ?? 0;
        const failurePatterns = result.failure_patterns?.length ?? 0;
        
        // 显示结果摘要
        resultSummary.innerHTML = `
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="bi bi-file-earmark-text"></i>
                    </div>
                    <div class="stat-number">${totalRecords}</div>
                    <div class="stat-label">总记录数</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="bi bi-check-circle text-success"></i>
                    </div>
                    <div class="stat-number">${(successRate * 100).toFixed(1)}%</div>
                    <div class="stat-label">成功率</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="bi bi-star"></i>
                    </div>
                    <div class="stat-number">${averageScore.toFixed(1)}</div>
                    <div class="stat-label">平均分数</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="bi bi-exclamation-triangle text-warning"></i>
                    </div>
                    <div class="stat-number">${failurePatterns}</div>
                    <div class="stat-label">失败模式</div>
                </div>
            </div>
        `;

        resultContainer.style.display = 'block';

        // 设置按钮事件
        document.getElementById('downloadJsonBtn').onclick = () => downloadResult(taskId, 'json');
        document.getElementById('downloadReportBtn').onclick = () => downloadResult(taskId, 'report');
        document.getElementById('viewReportBtn').onclick = () => previewReport(taskId);
        document.getElementById('modalDownloadBtn').onclick = () => downloadResult(taskId, 'report');
        
        // 方案1：自动预加载报告（后台获取，不显示）
        debugLog('开始预加载HTML报告', { taskId });
        console.log('自动预加载报告:', `/api/evaluation/report/${taskId}`);
        
        fetch(`/api/evaluation/report/${taskId}`)
            .then(response => {
                debugLog('报告预加载响应', { 
                    status: response.status, 
                    statusText: response.statusText,
                    ok: response.ok,
                    contentType: response.headers.get('content-type')
                });
                
                if (response.ok) {
                    console.log('报告预加载完成，状态:', response.status);
                    debugLog('报告预加载成功');
                    
                    // 可以选择获取内容大小信息
                    const contentLength = response.headers.get('content-length');
                    if (contentLength) {
                        console.log('报告大小:', Math.round(contentLength / 1024), 'KB');
                        debugLog('报告大小信息', { sizeKB: Math.round(contentLength / 1024) });
                    }
                } else {
                    console.warn('报告预加载失败，状态:', response.status, response.statusText);
                    debugLog('报告预加载失败', { 
                        status: response.status, 
                        statusText: response.statusText 
                    });
                }
            })
            .catch(error => {
                console.log('报告预加载错误:', error.message);
                debugLog('报告预加载异常', { 
                    error: error.message, 
                    name: error.name,
                    type: typeof error
                });
                
                // 预加载失败不影响主流程，只记录日志
                if (error.name === 'TypeError' && error.message.includes('fetch')) {
                    console.log('报告预加载网络错误，可能是服务器连接问题');
                }
            });
        
    } catch (error) {
        console.error('showResults错误:', error);
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('网络连接失败，请检查服务器状态');
        }
        throw error;
    }
}

// 下载结果
async function downloadResult(taskId, type) {
    const url = type === 'json' 
        ? `/api/evaluation/result/${taskId}` 
        : `/api/evaluation/report/${taskId}`;
    
    const response = await fetch(url);
    const blob = await response.blob();
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = type === 'json' 
        ? `analysis_result_${taskId}.json` 
        : `analysis_report_${taskId}.html`;
    link.click();
}

// 预览报告
async function previewReport(taskId, title) {
    debugLog('开始预览报告', { taskId, title });
    
    try {
        // 显示模态框
        const reportModalElement = document.getElementById('reportPreviewModal');
        const modal = showModal(reportModalElement);
        if (!modal) throw new Error('无法显示报告预览窗口');

        // 设置模态框标题
        const modalTitle = document.querySelector('#reportPreviewModal .modal-title');
        if (modalTitle) modalTitle.textContent = title || '评估分析报告';

        const iframe = document.getElementById('reportPreviewFrame');
        if (!iframe) throw new Error('未找到预览 iframe');

        console.log('🔍 开始加载报告诊断...');
        console.log('📋 任务ID:', taskId);
        console.log('📄 标题:', title);
        
        // 显示详细加载状态 - 简化为3步
        iframe.srcdoc = `
            <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100vh;font-family:Arial,sans-serif;">
                <div class="text-center text-primary">
                    <div class="spinner-border" role="status"></div>
                    <h3 class="mt-3">正在加载报告...</h3>
                    <div id="loadingStatus" style="margin-top: 20px; max-width: 600px;">
                        <p><strong>步骤 1/3:</strong> 准备获取报告内容...</p>
                        <p><strong>任务ID:</strong> ${taskId}</p>
                        <p><strong>时间:</strong> ${new Date().toLocaleString()}</p>
                    </div>
                </div>
            </div>
        `;

        const reportUrl = `/api/evaluation/report/${taskId}`;
        console.log('🌐 报告URL:', reportUrl);

        // 步骤2: 获取报告内容
        console.log('📄 步骤2: 获取报告内容...');
        iframe.srcdoc = iframe.srcdoc.replace(
            '<p><strong>步骤 1/3:</strong> 准备获取报告内容...</p>',
            '<p><strong>步骤 2/3:</strong> 正在获取报告内容...</p>'
        );

        let content;
        try {
            const response = await fetch(reportUrl);
            console.log('📊 内容请求响应:', {
                status: response.status,
                statusText: response.statusText,
                contentType: response.headers.get('content-type'),
                contentLength: response.headers.get('content-length')
            });

            if (!response.ok) {
                throw new Error(`获取报告失败: ${response.status} ${response.statusText}`);
            }

            content = await response.text();
            console.log('📏 报告内容长度:', content.length);
            console.log('🎯 内容预览 (前100字符):', content.substring(0, 100));

            // 验证内容格式
            if (!content.includes('<!DOCTYPE html>') && !content.includes('<html')) {
                console.warn('⚠️ 内容可能不是有效的HTML');
                iframe.srcdoc = `
                    <div style="padding:20px;color:orange;font-family:Arial,sans-serif;">
                        <h3>⚠️ 内容格式警告</h3>
                        <p>获取到的内容可能不是有效的HTML格式</p>
                        <p><strong>内容长度:</strong> ${content.length} 字符</p>
                        <p><strong>内容预览:</strong></p>
                        <pre style="background:#f5f5f5;padding:10px;overflow:auto;max-height:200px;">${content.substring(0, 500)}</pre>
                        <button onclick="window.open('${reportUrl}', '_blank')" style="padding:10px 20px;margin-top:10px;">
                            在新窗口中打开报告
                        </button>
                    </div>
                `;
                return;
            }

            console.log('✅ 内容格式验证通过');

        } catch (contentError) {
            console.error('❌ 获取内容失败:', contentError);
            iframe.srcdoc = `
                <div style="padding:20px;color:red;font-family:Arial,sans-serif;">
                    <h3>🚫 获取报告内容失败</h3>
                    <p><strong>错误:</strong> ${contentError.message}</p>
                    <p><strong>URL:</strong> ${reportUrl}</p>
                    <p><strong>时间:</strong> ${new Date().toLocaleString()}</p>
                    <div style="margin-top: 15px;">
                        <button onclick="window.open('${reportUrl}', '_blank')" style="padding:10px 20px;margin-right:10px;">
                            在新窗口中打开
                        </button>
                        <button onclick="window.parent.location.reload()" style="padding:10px 20px;">
                            刷新页面重试
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        // 步骤3: 显示报告内容
        console.log('🖼️ 步骤3: 显示报告内容...');
        iframe.srcdoc = iframe.srcdoc.replace(
            '<p><strong>步骤 2/3:</strong> 正在获取报告内容...</p>',
            '<p><strong>步骤 3/3:</strong> 正在显示报告内容...</p>'
        );

        // 设置加载超时
        const loadTimeout = setTimeout(() => {
            console.warn('⏰ 报告显示超时');
            iframe.srcdoc = `
                <div style="padding:20px;color:orange;font-family:Arial,sans-serif;">
                    <h3>⏰ 报告显示超时</h3>
                    <p>报告内容较大，显示时间过长</p>
                    <p><strong>内容大小:</strong> ${Math.round(content.length / 1024)} KB</p>
                    <p><strong>建议:</strong> 使用下载方式获取报告或在新窗口中打开</p>
                    <div style="margin-top: 15px;">
                        <button onclick="window.open('${reportUrl}', '_blank')" style="padding:10px 20px;margin-right:10px;">
                            在新窗口中打开
                        </button>
                        <button onclick="window.parent.downloadResult('${taskId}', 'report')" style="padding:10px 20px;">
                            下载报告文件
                        </button>
                    </div>
                </div>
            `;
        }, 10000); // 10秒超时

        // 直接设置内容到iframe.srcdoc
        setTimeout(() => {
            try {
                console.log('🚀 开始设置iframe内容...');
                iframe.srcdoc = content;
                
                // 监听iframe加载完成
                iframe.onload = () => {
                    clearTimeout(loadTimeout);
                    console.log('✅ 报告内容显示完成');
                    console.log('🎉 iframe文档状态:', {
                        readyState: iframe.contentDocument?.readyState || 'unknown',
                        title: iframe.contentDocument?.title || 'no title',
                        bodyLength: iframe.contentDocument?.body?.innerHTML?.length || 0
                    });
                };

                // 监听iframe错误
                iframe.onerror = (error) => {
                    clearTimeout(loadTimeout);
                    console.error('❌ iframe显示错误:', error);
                    iframe.srcdoc = `
                        <div style="padding:20px;color:red;font-family:Arial,sans-serif;">
                            <h3>🚫 报告显示失败</h3>
                            <p><strong>错误:</strong> 无法在iframe中显示报告内容</p>
                            <p><strong>可能原因:</strong> 浏览器安全策略限制或内容格式问题</p>
                            <div style="margin-top: 15px;">
                                <button onclick="window.open('${reportUrl}', '_blank')" style="padding:10px 20px;margin-right:10px;">
                                    在新窗口中打开
                                </button>
                                <button onclick="window.parent.downloadResult('${taskId}', 'report')" style="padding:10px 20px;">
                                    下载报告文件
                                </button>
                            </div>
                        </div>
                    `;
                };

                console.log('📱 iframe内容设置完成，等待渲染...');
                
            } catch (setContentError) {
                clearTimeout(loadTimeout);
                console.error('❌ 设置iframe内容失败:', setContentError);
                iframe.srcdoc = `
                    <div style="padding:20px;color:red;font-family:Arial,sans-serif;">
                        <h3>🚫 设置报告内容失败</h3>
                        <p><strong>错误:</strong> ${setContentError.message}</p>
                        <p><strong>内容大小:</strong> ${Math.round(content.length / 1024)} KB</p>
                        <div style="margin-top: 15px;">
                            <button onclick="window.open('${reportUrl}', '_blank')" style="padding:10px 20px;margin-right:10px;">
                                在新窗口中打开
                            </button>
                            <button onclick="window.parent.downloadResult('${taskId}', 'report')" style="padding:10px 20px;">
                                下载报告文件
                            </button>
                        </div>
                    </div>
                `;
            }
        }, 500); // 短暂延时后设置内容

    } catch (err) {
        console.error('💥 预览报告失败:', err);
        debugLog('预览报告失败', { error: err.message, stack: err.stack });
        
        const iframe = document.getElementById('reportPreviewFrame');
        if (iframe) {
            iframe.srcdoc = `
                <div style="padding:20px;color:red;font-family:Arial,sans-serif;">
                    <h3>💥 预览功能异常</h3>
                    <p><strong>错误:</strong> ${err.message}</p>
                    <p><strong>任务ID:</strong> ${taskId}</p>
                    <p><strong>时间:</strong> ${new Date().toLocaleString()}</p>
                    <hr>
                    <p>请尝试下载报告或在新窗口中打开</p>
                    <div style="margin-top: 15px;">
                        <button onclick="window.open('/api/evaluation/report/${taskId}', '_blank')" style="padding:10px 20px;margin-right:10px;">
                            在新窗口中打开
                        </button>
                        <button onclick="window.parent.location.reload()" style="padding:10px 20px;">
                            刷新页面重试
                        </button>
                    </div>
                </div>
            `;
        }
    }
}

// 事件监听器设置函数
function setupEventListeners() {
    // 键盘快捷键：按F12开启/关闭调试模式
    document.addEventListener('keydown', function(e) {
        if (e.key === 'F12') {
            e.preventDefault();
            toggleDebugMode();
        }
    });

    // 文件拖拽处理
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        dropZone.addEventListener('click', () => {
            if (fileInput) {
                fileInput.click();
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
    }

    // 上传和分析文件
    if (uploadBtn) {
        uploadBtn.addEventListener('click', async () => {
            const file = window.selectedFile;
            if (!file) return;

            progressContainer.style.display = 'block';
            resultContainer.style.display = 'none';
            
            try {
                // 步骤1: 上传文件
                updateProgress(1, 25, '正在上传文件...');
                fileId = await uploadFile(file);

                // 步骤2: 开始分析
                updateProgress(2, 50, '正在进行失败分析...');
                currentTaskId = await startAnalysis(fileId);

                // 步骤3: 等待分析完成
                await waitForAnalysis(currentTaskId);

                // 步骤4: 显示结果
                updateProgress(4, 100, '分析完成！');
                await showResults(currentTaskId);

            } catch (error) {
                console.error('分析失败:', error);
                console.error('错误类型:', typeof error);
                console.error('错误详情:', {
                    name: error.name,
                    message: error.message,
                    stack: error.stack,
                    toString: error.toString()
                });
                
                // 提供更详细的错误信息
                let errorMessage = '未知错误';
                let errorDetails = '';
                
                if (error && typeof error === 'object') {
                    if (error.message) {
                        errorMessage = error.message;
                    } else if (error.toString && typeof error.toString === 'function') {
                        errorMessage = error.toString();
                    } else {
                        errorMessage = JSON.stringify(error);
                    }
                    
                    // 收集错误详情
                    errorDetails = `错误类型: ${error.name || 'Unknown'}\n`;
                    if (error.stack) {
                        errorDetails += `堆栈跟踪: ${error.stack.split('\n').slice(0, 3).join('\n')}\n`;
                    }
                    errorDetails += `当前步骤: ${currentTaskId ? '任务ID: ' + currentTaskId : '文件上传阶段'}`;
                } else if (typeof error === 'string') {
                    errorMessage = error;
                } else {
                    errorMessage = String(error);
                }
                
                // 如果错误消息为空，提供默认信息
                if (!errorMessage || errorMessage.trim() === '') {
                    errorMessage = '发生了未知错误，请检查网络连接和服务器状态';
                }
                
                // 显示详细的错误信息
                const errorHtml = `
                    <div style="max-width: 500px; text-align: left;">
                        <h4>分析失败</h4>
                        <p><strong>错误信息:</strong> ${errorMessage}</p>
                        ${errorDetails ? `<details><summary>详细信息</summary><pre style="font-size: 12px; margin-top: 10px;">${errorDetails}</pre></details>` : ''}
                        <br>
                        <small>请尝试以下解决方案：<br>
                        1. 检查网络连接<br>
                        2. 确认服务器正在运行<br>
                        3. 验证文件格式是否正确<br>
                        4. 刷新页面重试</small>
                    </div>
                `;
                
                // 创建自定义错误模态框
                showErrorModal(errorHtml);
                progressContainer.style.display = 'none';
            }
        });
    }

    // 绑定刷新按钮事件
    if (refreshInputFiles) {
        refreshInputFiles.addEventListener('click', loadInputFiles);
    }
    
    // 绑定分析按钮事件
    if (analyzeInputFileBtn) {
        analyzeInputFileBtn.addEventListener('click', analyzeInputFile);
    }
}

// 生成简化报告（当原始报告包含不可修复的错误时）
function generateSimplifiedReport(taskId, originalHtml) {
    console.log('生成简化报告...');
    
    // 尝试从原始HTML中提取一些基本信息
    let extractedInfo = {
        title: '评估分析报告',
        summary: '报告包含格式错误，显示简化版本',
        taskId: taskId,
        timestamp: new Date().toLocaleString()
    };
    
    // 尝试提取一些基本数据（安全地）
    try {
        // 查找可能的数据表格或统计信息
        const tableMatches = originalHtml.match(/<table[^>]*>[\s\S]*?<\/table>/gi);
        const statMatches = originalHtml.match(/\d+[^\d]*(?:records?|failures?|tests?|errors?)/gi);
        
        if (tableMatches) {
            extractedInfo.tablesFound = tableMatches.length;
        }
        
        if (statMatches) {
            extractedInfo.stats = statMatches.slice(0, 5); // 只取前5个统计信息
        }
    } catch (e) {
        console.warn('提取信息时出错:', e.message);
    }
    
    return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${extractedInfo.title}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #007bff;
            margin: 0;
            font-size: 2.5rem;
        }
        .header .subtitle {
            color: #6c757d;
            margin-top: 10px;
            font-size: 1.1rem;
        }
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
            border-left: 4px solid #ffc107;
            background-color: #fff3cd;
            color: #856404;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .info-card {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 20px;
            border-left: 4px solid #007bff;
        }
        .info-card h3 {
            margin: 0 0 10px 0;
            color: #007bff;
        }
        .stats-list {
            list-style: none;
            padding: 0;
        }
        .stats-list li {
            background: #e9ecef;
            margin: 5px 0;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: monospace;
        }
        .download-section {
            background: #e3f2fd;
            border-radius: 6px;
            padding: 20px;
            margin-top: 30px;
            text-align: center;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background: #0056b3;
        }
        .technical-info {
            margin-top: 30px;
            padding: 20px;
            background: #f1f3f4;
            border-radius: 6px;
            font-size: 0.9rem;
            color: #5f6368;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 评估分析报告</h1>
            <div class="subtitle">任务ID: ${extractedInfo.taskId}</div>
            <div class="subtitle">生成时间: ${extractedInfo.timestamp}</div>
        </div>

        <div class="alert">
            <strong>⚠️ 注意：</strong> 原始报告包含格式错误，这是一个简化版本。建议下载完整报告进行详细分析。
        </div>

        <div class="info-grid">
            <div class="info-card">
                <h3>📈 报告状态</h3>
                <p>报告已生成但包含模板渲染错误。数据分析已完成，建议通过下载方式获取完整信息。</p>
            </div>
            
            <div class="info-card">
                <h3>🔍 发现的内容</h3>
                <ul>
                    <li>任务ID: ${extractedInfo.taskId}</li>
                    ${extractedInfo.tablesFound ? `<li>数据表格: ${extractedInfo.tablesFound} 个</li>` : ''}
                    <li>报告类型: 评估分析</li>
                    <li>状态: 需要修复格式</li>
                </ul>
            </div>
        </div>

        ${extractedInfo.stats ? `
        <div class="info-card">
            <h3>📊 提取的统计信息</h3>
            <ul class="stats-list">
                ${extractedInfo.stats.map(stat => `<li>${stat}</li>`).join('')}
            </ul>
        </div>
        ` : ''}

        <div class="download-section">
            <h3>📥 获取完整报告</h3>
            <p>要查看完整的分析结果，请下载原始报告文件：</p>
            <button class="btn" onclick="window.parent.downloadResult('${taskId}', 'report')">
                📄 下载HTML报告
            </button>
            <button class="btn" onclick="window.parent.downloadResult('${taskId}', 'json')">
                📊 下载JSON数据
            </button>
        </div>

        <div class="technical-info">
            <h4>🔧 技术信息</h4>
            <p><strong>问题原因：</strong> 服务器生成的HTML报告包含未处理的模板字符串（如 \${variable}），导致JavaScript语法错误。</p>
            <p><strong>解决方案：</strong> 请检查服务器端模板渲染逻辑，确保所有变量都被正确替换。</p>
            <p><strong>临时方案：</strong> 下载报告文件到本地，使用文本编辑器手动修复或提取数据。</p>
        </div>
    </div>

    <script>
        console.log('简化报告已加载');
        console.log('原始报告包含格式错误，已生成安全的简化版本');
        
        // 提供下载功能的备用方案
        window.downloadResult = function(taskId, type) {
            const url = type === 'json' 
                ? \`/api/evaluation/result/\${taskId}\`
                : \`/api/evaluation/report/\${taskId}\`;
            
            const link = document.createElement('a');
            link.href = url;
            link.download = type === 'json' 
                ? \`analysis_result_\${taskId}.json\` 
                : \`analysis_report_\${taskId}.html\`;
            link.click();
        };
    </script>
</body>
</html>`;
}

// 显示消息（改进实现）
function showMessage(message, type = 'info') {
    console.log(`${type.toUpperCase()}: ${message}`);
    
    // 创建一个简单的Toast消息
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    toast.innerHTML = `
        <strong>${type === 'error' ? '错误' : type === 'success' ? '成功' : '信息'}:</strong> ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()" aria-label="Close"></button>
    `;
    
    document.body.appendChild(toast);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// 模态框管理函数
function showModal(modalElement) {
    if (!modalElement) {
        console.error('模态框元素不存在');
        return null;
    }
    
    try {
        // 移除aria-hidden属性，避免可访问性警告
        modalElement.removeAttribute('aria-hidden');
        
        // 尝试使用Bootstrap的方式
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            return modal;
        } else {
            // 备用方案：手动显示模态框
            modalElement.classList.add('show');
            modalElement.style.display = 'block';
            modalElement.style.backgroundColor = 'rgba(0,0,0,0.5)';
            document.body.classList.add('modal-open');
            
            return {
                show: () => {
                    modalElement.classList.add('show');
                    modalElement.style.display = 'block';
                    modalElement.removeAttribute('aria-hidden');
                },
                hide: () => {
                    modalElement.classList.remove('show');
                    modalElement.style.display = 'none';
                    modalElement.setAttribute('aria-hidden', 'true');
                    document.body.classList.remove('modal-open');
                }
            };
        }
    } catch (error) {
        console.error('显示模态框失败:', error);
        // 简单的后备方案
        modalElement.style.display = 'block';
        modalElement.classList.add('show');
        modalElement.removeAttribute('aria-hidden');
        return {
            show: () => {
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
                modalElement.removeAttribute('aria-hidden');
            },
            hide: () => {
                modalElement.style.display = 'none';
                modalElement.classList.remove('show');
                modalElement.setAttribute('aria-hidden', 'true');
            }
        };
    }
}

function hideModal(modalElement) {
    if (!modalElement) return;
    
    try {
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
            // Bootstrap会自动处理aria-hidden，但为了确保一致性，我们手动添加
            modalElement.setAttribute('aria-hidden', 'true');
        } else {
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
            modalElement.setAttribute('aria-hidden', 'true');
            document.body.classList.remove('modal-open');
        }
    } catch (error) {
        console.error('隐藏模态框失败:', error);
        modalElement.style.display = 'none';
        modalElement.classList.remove('show');
        modalElement.setAttribute('aria-hidden', 'true');
    }
}

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 设置事件监听器
    setupEventListeners();
    
    // 页面加载时自动获取输入文件列表
    loadInputFiles();
    
    debugLog('页面初始化完成');
}); 