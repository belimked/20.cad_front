# 通用工具函数库使用指南

## 概述

`common-utils.js` 提供了一套完整的JavaScript工具函数，旨在减少代码重复，提高开发效率和代码质量。

## 快速开始

### 1. 引入工具库

在HTML文件中添加以下脚本引用：

```html
<!-- 通用工具函数库 -->
<script src="/static/js/utils/common-utils.js"></script>

<!-- 你的页面脚本 -->
<script src="/static/js/your-script.js"></script>
```

### 2. 基本使用

工具库会自动导出以下全局对象：

- `AppConfig` - 应用配置管理
- `DOMUtils` - DOM操作工具
- `APIUtils` - API调用工具
- `FormUtils` - 表单处理工具
- `ModalUtils` - 模态框工具
- `MessageUtils` - 消息提示工具
- `DataUtils` - 数据处理工具

## 详细使用示例

### DOM操作工具 (DOMUtils)

```javascript
// 替换原来的 document.getElementById
const element = DOMUtils.getElement('myElementId');

// 设置元素内容
DOMUtils.setElementContent('titleId', '新标题');

// 设置元素值
DOMUtils.setElementValue('inputId', 'new value');

// 显示/隐藏元素
DOMUtils.toggleElement('loadingSpinner', true); // 显示
DOMUtils.toggleElement('loadingSpinner', false); // 隐藏

// 添加/移除CSS类
DOMUtils.addClass('buttonId', 'active');
DOMUtils.removeClass('buttonId', 'disabled');
```

### API调用工具 (APIUtils)

```javascript
// 原来的代码：
// fetch('/api/data', {
//     method: 'GET',
//     headers: { 'Content-Type': 'application/json' }
// }).then(response => response.json())

// 使用工具库：
try {
    const data = await APIUtils.get('/api/data');
    console.log(data);
} catch (error) {
    console.error('API调用失败:', error);
}

// POST请求
try {
    const result = await APIUtils.post('/api/users', {
        name: 'John',
        email: 'john@example.com'
    });
} catch (error) {
    APIUtils.showApiError('errorContainer', error, '创建用户');
}

// 设置加载状态
APIUtils.setLoadingState('loadingSpinner', true);
const data = await APIUtils.get('/api/data');
APIUtils.setLoadingState('loadingSpinner', false);
```

### 表单处理工具 (FormUtils)

```javascript
// 批量获取表单数据
const formData = FormUtils.getFormData(['name', 'email', 'phone']);

// 验证必填字段
const isValid = FormUtils.validateRequired(formData, (error) => {
    MessageUtils.showError(error);
});

// 填充表单数据
FormUtils.fillFormData({
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '123-456-7890'
});

// 重置表单和关闭模态框
FormUtils.resetFormAndModal('userForm', modalInstance);
```

### 消息提示工具 (MessageUtils)

```javascript
// 替换原来的简单alert
// alert('操作成功！');

// 使用工具库：
MessageUtils.showSuccess('操作成功！');
MessageUtils.showError('操作失败，请重试');
MessageUtils.showWarning('请检查输入的数据');
MessageUtils.showInfo('正在处理您的请求...');

// 自定义位置和选项
MessageUtils.showSuccess('保存成功！', {
    position: 'top-center',
    timeout: 5000
});

// 清除所有消息
MessageUtils.clearAll();
```

### 模态框工具 (ModalUtils)

```javascript
// 设置模态框信息
ModalUtils.setupModal(
    'modalTitle',      // 标题元素ID
    '编辑用户',         // 标题文本
    'editMode',        // 编辑模式隐藏字段ID
    'edit',            // 模式值
    'originalId',      // 原始ID隐藏字段ID
    user.id            // 原始ID值
);

// 显示确认对话框
ModalUtils.showConfirm('确定要删除这个项目吗？', () => {
    // 确认后的操作
    deleteItem(itemId);
}, '删除确认');

// 创建动态模态框
ModalUtils.createModal({
    title: '操作确认',
    body: '<p>此操作不可撤销，确定要继续吗？</p>',
    buttons: [
        { text: '取消', class: 'btn-secondary', dismiss: true },
        { text: '确定', class: 'btn-danger', callback: confirmAction }
    ]
});
```

### 数据处理工具 (DataUtils)

```javascript
// 深度克隆对象
const userCopy = DataUtils.deepClone(originalUser);

// 数组去重
const uniqueUsers = DataUtils.uniqueByKey(usersArray, 'id');

// 格式化文件大小
const sizeText = DataUtils.formatFileSize(fileInfo.size);

// 格式化日期时间
const formattedDate = DataUtils.formatDateTime(new Date(), 'YYYY-MM-DD HH:mm');
```

### 配置管理 (AppConfig)

```javascript
// 获取API基础URL
const apiUrl = AppConfig.getApiBaseUrl() + '/api/users';

// 设置自定义API基础URL
AppConfig.setApiBaseUrl('https://api.example.com');

// 访问配置选项
console.log('API超时时间:', AppConfig.api.timeout);
console.log('消息显示时间:', AppConfig.ui.messageTimeout);
```

## 在现有项目中的应用

### evaluation_analysis.js 优化示例

```javascript
// 原来的代码：
// function showMessage(message, type = 'info') {
//     const alertDiv = document.createElement('div');
//     alertDiv.className = `alert alert-${type}`;
//     alertDiv.textContent = message;
//     document.body.appendChild(alertDiv);
// }

// 优化后：
// 直接使用工具库的消息功能
// MessageUtils.showSuccess(message);
// MessageUtils.showError(message);
// MessageUtils.showInfo(message);

// 原来的DOM操作：
// document.getElementById('progressBar').style.width = percentage + '%';

// 优化后：
// DOMUtils.getElement('progressBar').style.width = percentage + '%';
```

### report.js 优化示例

```javascript
// 原来的代码：
// const modal = document.getElementById("dataModal");
// const modalTitle = document.getElementById("modalTitle");

// 优化后：
// const modal = DOMUtils.getElement("dataModal");
// const modalTitle = DOMUtils.getElement("modalTitle");

// 原来的内容设置：
// modalTitle.textContent = data.title;

// 优化后：
// DOMUtils.setElementContent("modalTitle", data.title);
```

## 兼容性说明

- 工具库提供了 `showSuccess()` 和 `showError()` 全局函数以保持向后兼容
- 所有工具对象都导出到 `window` 对象，可在任何地方访问
- 原有代码可以逐步迁移，不需要一次性全部更改

## 最佳实践

1. **逐步迁移**：在修改现有功能时逐步使用工具函数
2. **错误处理**：使用 `APIUtils` 的统一错误处理机制
3. **配置集中**：将API URL等配置放在 `AppConfig` 中管理
4. **消息提示**：统一使用 `MessageUtils` 替代 `alert()` 和 `console.log()`
5. **DOM操作**：优先使用 `DOMUtils` 简化DOM操作代码

## 性能优化

- 工具函数经过优化，减少重复的DOM查询
- API调用支持超时控制和错误重试
- 消息提示自动清理，避免内存泄漏
- 配置管理减少硬编码，提高可维护性

## 扩展建议

如需要添加新的工具函数，建议：

1. 在对应的工具对象中添加方法
2. 保持API的一致性
3. 添加适当的JSDoc注释
4. 考虑向后兼容性
5. 更新此文档的使用示例 