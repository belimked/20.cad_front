// 评估分析报告JavaScript功能

// 图表数据（将由模板替换）
// 使用条件声明避免与模板中的内联脚本冲突
let chartData;
if (typeof window.chartData !== 'undefined') {
    chartData = window.chartData;
} else {
    chartData = {};
}

// 获取模态框元素
const modal = document.getElementById("dataModal");
const modalTitle = document.getElementById("modalTitle");
const modalVisual = document.getElementById("modalVisual");
const modalData = document.getElementById("modalData");
const modalStats = document.getElementById("modalStats");

// 初始化图表数据
function initChartData(data) {
    chartData = data;
}

// 显示图表数据
function showChartData(chartType) {
    const data = chartData[chartType];
    if (!data) return;
    
    // 设置标题
    modalTitle.textContent = data.title;
    
    // 设置可视化内容
    modalVisual.innerHTML = `<img src="${document.querySelector(`img[data-chart="${chartType}"]`).src}" alt="${data.title}" style="max-width:100%;">`;
    
    // 设置原始数据
    modalData.textContent = JSON.stringify(data.data, null, 2);
    
    // 设置统计信息
    let statsHTML = '<table class="stats-table">';
    for (const [key, value] of Object.entries(data.stats)) {
        statsHTML += `<tr><th>${formatKey(key)}</th><td>${value}</td></tr>`;
    }
    statsHTML += '</table>';
    modalStats.innerHTML = statsHTML;
    
    // 设置记录数据（如果有的话）
    if (data.records && Object.keys(data.records).length > 0) {
        // 存储所有记录以供搜索和分类
        window.allRecordsData = [];
        
        // 生成所有记录的HTML
        let allRecordsHTML = '<div class="records-container">';
        let successRecordsHTML = '<div class="records-container">';
        let failedRecordsHTML = '<div class="records-container">';
        
        for (const [objectName, records] of Object.entries(data.records)) {
            // 添加到全局记录数组
            records.forEach(record => {
                window.allRecordsData.push({
                    ...record,
                    businessObject: objectName
                });
            });
            
            // 为每个业务对象创建分区
            const successRecords = records.filter(r => r.status === 'success');
            const failedRecords = records.filter(r => r.status === 'failed');
            
            // 全部记录部分
            allRecordsHTML += generateBusinessObjectSection(objectName, records);
            
            // 成功记录部分
            if (successRecords.length > 0) {
                successRecordsHTML += generateBusinessObjectSection(objectName, successRecords);
            }
            
            // 失败记录部分
            if (failedRecords.length > 0) {
                failedRecordsHTML += generateBusinessObjectSection(objectName, failedRecords);
            }
        }
        
        allRecordsHTML += '</div>';
        successRecordsHTML += '</div>';
        failedRecordsHTML += '</div>';
        
        // 填充各个标签页
        document.getElementById('allRecords').innerHTML = allRecordsHTML;
        document.getElementById('successRecords').innerHTML = successRecordsHTML;
        document.getElementById('failedRecords').innerHTML = failedRecordsHTML;
    } else {
        document.getElementById('allRecords').innerHTML = '<p>无可用的详细记录。</p>';
        document.getElementById('successRecords').innerHTML = '<p>无可用的成功记录。</p>';
        document.getElementById('failedRecords').innerHTML = '<p>无可用的失败记录。</p>';
    }
    
    // 显示模态框
    modal.style.display = "block";
}

// 格式化键名
function formatKey(key) {
    return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// 格式化JSON字符串
function formatJson(jsonString) {
    try {
        if (!jsonString) return 'N/A';
        const parsed = JSON.parse(jsonString);
        return JSON.stringify(parsed, null, 2);
    } catch (e) {
        return jsonString || 'Invalid JSON';
    }
}

// 生成业务对象部分的HTML（全局函数）
function generateBusinessObjectSection(objectName, records) {
    let html = `<div class="business-object-section" data-object="${objectName}">`;
    html += `<h4>${objectName} <span class="record-count">(${records.length} 条记录)</span></h4>`;
    html += `<div class="records-list">`;
    
    records.forEach((record, index) => {
        html += `<div class="record-item" data-id="${record.id}" data-status="${record.status}" data-score="${record.score}">`;
        html += `<div class="record-header">`;
        html += `<span class="record-id">ID: ${record.id}</span>`;
        html += `<span class="record-status status-${record.status}">${record.status}</span>`;
        html += `<span class="record-score">Score: ${record.score}</span>`;
        html += `</div>`;
        html += `<div class="record-details">`;
        html += `<div class="record-question"><strong>问题:</strong> ${record.question}</div>`;
        html += `<details class="record-answers">`;
        html += `<summary>查看答案和评估</summary>`;
        html += `<div class="answer-section">`;
        html += `<div><strong>期望答案:</strong><pre class="json-display">${formatJson(record.expected_answer)}</pre></div>`;
        html += `<div><strong>实际答案:</strong><pre class="json-display">${formatJson(record.actual_answer)}</pre></div>`;
        if (record.evaluation && record.evaluation.comparison_result) {
            html += `<div><strong>差异:</strong><pre class="json-display">${JSON.stringify(record.evaluation.comparison_result.value_differences || [], null, 2)}</pre></div>`;
        }
        if (record.evaluation && record.evaluation.failure_reason) {
            html += `<div><strong>失败原因:</strong> ${record.evaluation.failure_reason}</div>`;
        }
        html += `<div><strong>处理时间:</strong> ${record.processing_time.toFixed(3)}s</div>`;
        html += `</div>`;
        html += `</details>`;
        html += `</div>`;
        html += `</div>`;
    });
    
    html += `</div>`;
    html += `</div>`;
    return html;
}

// 关闭模态框
function closeModal() {
    modal.style.display = "none";
}

// 切换标签页
function showTab(tabId) {
    // 隐藏所有标签页内容
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 取消所有标签页按钮的活动状态
    document.querySelectorAll('.modal-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 显示选中的标签页内容
    document.getElementById(tabId).classList.add('active');
    
    // 设置选中的标签页按钮为活动状态
    document.querySelector(`.modal-tab[onclick="showTab('${tabId}')"]`).classList.add('active');
}

// 切换记录标签页
function showRecordTab(tabId) {
    // 隐藏所有记录标签页内容
    document.querySelectorAll('.record-tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 取消所有记录标签页按钮的活动状态
    document.querySelectorAll('.record-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 显示选中的记录标签页内容
    document.getElementById(tabId).classList.add('active');
    
    // 设置选中的记录标签页按钮为活动状态
    document.querySelector(`.record-tab[onclick="showRecordTab('${tabId}')"]`).classList.add('active');
}

// 搜索记录
function searchRecords() {
    const searchTerm = document.getElementById('recordsSearchInput').value.toLowerCase();
    if (!window.allRecordsData || !searchTerm) return;
    
    // 过滤记录
    const filteredRecords = window.allRecordsData.filter(record => {
        // 在多个字段中搜索
        return (
            (record.question && record.question.toLowerCase().includes(searchTerm)) ||
            (record.expected_answer && record.expected_answer.toLowerCase().includes(searchTerm)) ||
            (record.actual_answer && record.actual_answer.toLowerCase().includes(searchTerm)) ||
            (record.businessObject && record.businessObject.toLowerCase().includes(searchTerm)) ||
            (record.id && record.id.toString().includes(searchTerm)) ||
            (record.score && record.score.toString().includes(searchTerm))
        );
    });
    
    // 按业务对象分组
    const groupedRecords = {};
    filteredRecords.forEach(record => {
        if (!groupedRecords[record.businessObject]) {
            groupedRecords[record.businessObject] = [];
        }
        groupedRecords[record.businessObject].push(record);
    });
    
    // 生成搜索结果HTML
    let searchResultsHTML = '<div class="records-container">';
    if (Object.keys(groupedRecords).length > 0) {
        searchResultsHTML += `<h3>搜索结果: "${searchTerm}" (${filteredRecords.length} 条匹配记录)</h3>`;
        for (const [objectName, records] of Object.entries(groupedRecords)) {
            searchResultsHTML += generateBusinessObjectSection(objectName, records);
        }
    } else {
        searchResultsHTML += `<h3>搜索结果: "${searchTerm}"</h3><p>没有找到匹配的记录</p>`;
    }
    searchResultsHTML += '</div>';
    
    // 显示搜索结果
    document.getElementById('allRecords').innerHTML = searchResultsHTML;
    showRecordTab('allRecords');
}

// 点击模态框外部时关闭
window.onclick = function(event) {
    if (event.target == modal) {
        closeModal();
    }
}

// 训练指南相关功能
let trainingGuideData = null;

// 新增包装，兼容旧按钮
function showTrainingGuide() {
    generateTrainingGuide();
}

async function generateTrainingGuide() {
    const loader = document.getElementById('trainingGuideContainer');
    loader.innerHTML = '<div class="text-center my-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-3">正在生成训练指南，请稍候...</p></div>';
    loader.style.display = 'block';
    
    try {
        // 获取任务ID
        const urlParams = new URLSearchParams(window.location.search);
        const taskId = urlParams.get('task_id');
        
        if (!taskId) {
            throw new Error('无法获取任务ID');
        }
        
        // 发送请求获取训练指南
        const response = await fetch(`/evaluation/training-guide/${taskId}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`获取训练指南失败: ${response.status} - ${errorText}`);
        }
        
        // 获取响应文本
        const responseText = await response.text();
        
        // 尝试解析JSON
        try {
            trainingGuideData = JSON.parse(responseText);
        } catch (jsonError) {
            console.error("JSON解析错误:", jsonError);
            console.error("原始响应内容:", responseText);
            throw new Error(`JSON解析失败: ${jsonError.message}. 请检查服务器响应格式。`);
        }
        
        // 检查数据结构
        if (!trainingGuideData || typeof trainingGuideData !== 'object') {
            throw new Error('无效的训练指南数据结构');
        }
        
        // 启用下载按钮
        document.getElementById('downloadDropdown').disabled = false;
        
        // 渲染训练指南
        renderTrainingGuide(trainingGuideData);
    } catch (error) {
        console.error("生成训练指南错误:", error);
        loader.innerHTML = `<div class="alert alert-danger my-4">
            <h5>生成训练指南失败</h5>
            <p>${error.message}</p>
            <details>
                <summary>详细错误信息</summary>
                <pre>${error.stack || '无堆栈信息'}</pre>
            </details>
        </div>`;
    }
}

function renderTrainingGuide(data) {
    // 显示容器
    const container = document.getElementById('trainingGuideContainer');
    container.style.display = 'block';
    
    // 显示摘要
    document.getElementById('guideSummary').textContent = data.summary;
    
    // 渲染总体统计
    renderTotalStats(data);
    
    // 渲染建议类型统计
    renderRecommendationStats(data);
    
    // 渲染高优先级建议
    renderHighPriorityRecommendations(data);
    
    // 渲染业务对象分析
    renderBusinessObjects(data);
    
    // 渲染规则分析
    renderRules(data);
    
    // 渲染业务对象下载列表
    renderBusinessObjectDownloadList(data);
}

function renderTotalStats(data) {
    const container = document.getElementById('guideTotalStats');
    
    container.innerHTML = `
        <tr>
            <th>总记录数</th>
            <td>${data.total_records}</td>
        </tr>
        <tr>
            <th>失败记录数</th>
            <td>${data.total_failures}</td>
        </tr>
        <tr>
            <th>整体失败率</th>
            <td>${data.overall_failure_percentage.toFixed(1)}%</td>
        </tr>
        <tr>
            <th>业务对象数量</th>
            <td>${Object.keys(data.business_object_guides).length}</td>
        </tr>
    `;
}

function renderRecommendationStats(data) {
    // 统计不同类型的建议数量
    let trainingCount = 0;
    let promptCount = 0;
    let bothCount = 0;
    let highPriorityCount = 0;
    
    for (const bo in data.business_object_guides) {
        const guide = data.business_object_guides[bo];
        
        guide.recommendations.forEach(rec => {
            if (rec.recommendation_type === 'training') trainingCount++;
            else if (rec.recommendation_type === 'prompt') promptCount++;
            else if (rec.recommendation_type === 'both') bothCount++;
            
            if (rec.priority === 'high') highPriorityCount++;
        });
    }
    
    const totalRecommendations = trainingCount + promptCount + bothCount;
    
    const container = document.getElementById('guideRecommendationStats');
    container.innerHTML = `
        <tr>
            <th>训练建议总数</th>
            <td>${totalRecommendations}</td>
        </tr>
        <tr>
            <th>需要训练</th>
            <td>${trainingCount} (${(trainingCount / totalRecommendations * 100).toFixed(1)}%)</td>
        </tr>
        <tr>
            <th>改进提示词</th>
            <td>${promptCount} (${(promptCount / totalRecommendations * 100).toFixed(1)}%)</td>
        </tr>
        <tr>
            <th>两者都需要</th>
            <td>${bothCount} (${(bothCount / totalRecommendations * 100).toFixed(1)}%)</td>
        </tr>
        <tr>
            <th>高优先级建议</th>
            <td>${highPriorityCount}</td>
        </tr>
    `;
}

function downloadTrainingGuide(format, businessObject) {
    // 获取任务ID
    const urlParams = new URLSearchParams(window.location.search);
    const taskId = urlParams.get('task_id');
    
    if (!taskId) {
        alert('无法获取任务ID');
        return;
    }
    
    // 构建下载URL
    let url = `/evaluation/training-guide/${taskId}/download?format=${format}`;
    if (businessObject) {
        url += `&business_object=${encodeURIComponent(businessObject)}`;
    }
    
    // 触发下载
    window.open(url, '_blank');
} 