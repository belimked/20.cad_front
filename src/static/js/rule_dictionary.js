// Rule Dictionary 页面JavaScript代码
// 使用外部通用工具函数库，无需重复定义工具函数

// =================================================================================
// 页面配置
// =================================================================================

// 配置API基础URL（使用工具库的配置管理）
const API_BASE_URL = AppConfig.getApiBaseUrl();

// =================================================================================
// 全局变量
// =================================================================================
        let currentRuleType = null;
        let currentRuleTypeName = null;
        let currentRules = [];
        let displayedRules = []; // 新增：当前显示的规则
        let ruleModalInstance = null;
        let deleteModalInstance = null;
        let relationshipModalInstance = null; // 新增：关系规则模态框实例
        let ruleDetailModalInstance = null; // 新增：规则详情模态框实例
        let connectionsModalInstance = null; // 新增：连接符管理模态框实例
        let ruleToDelete = null;
        const RULES_PER_PAGE = 15; // 每页显示的规则数量
        
        // 关系规则相关变量
        let currentRelationshipType = null;
        let currentRelationshipTypeName = null;
        let currentRelationshipRules = [];
        let displayedRelationshipRules = [];
        
        // 连接符管理相关变量
        let currentConnectionsBusinessObject = null;
        let currentConnections = [];
        let originalConnections = []; // 用于比较是否有更改


        
        // 示例规则类型数据 (实际中将从API获取)
        const mockRuleTypes = [
            { id: "relationship", name: "关系规则", description: "定义实体间的关系规则", itemCount: 12 },
            { id: "transformation", name: "转换规则", description: "定义数据转换规则", itemCount: 8 },
            { id: "validation", name: "验证规则", description: "用于数据验证的规则", itemCount: 15 },
            { id: "business", name: "业务规则", description: "特定业务领域的规则", itemCount: 10 }
        ];
        
        // 示例规则数据 (实际中将从API获取)
        const mockRules = {
            "relationship": [
                {
                    id: "rel001",
                    name: "部门经理关系",
                    description: "定义部门和经理之间的关系",
                    condition: "当部门对象存在且有员工对象时",
                    action: "识别部门负责人并建立'管理'关系",
                    priority: 8,
                    status: "active",
                    tags: ["department", "manager", "organization"]
                },
                {
                    id: "rel002",
                    name: "项目成员关系",
                    description: "定义项目和团队成员之间的关系",
                    condition: "当项目对象存在且有人员分配信息时",
                    action: "为每个人员建立'参与'关系，并记录角色信息",
                    priority: 7,
                    status: "active",
                    tags: ["project", "team", "role"]
                }
            ],
            "transformation": [
                {
                    id: "trans001",
                    name: "日期格式统一",
                    description: "将不同格式的日期转换为标准格式",
                    condition: "当遇到日期字段时",
                    action: "转换为YYYY-MM-DD格式",
                    priority: 5,
                    status: "active",
                    tags: ["date", "format", "normalization"]
                }
            ],
            "validation": [
                {
                    id: "val001",
                    name: "员工ID验证",
                    description: "验证员工ID的格式是否正确",
                    condition: "当处理员工ID字段时",
                    action: "检查是否符合EMP-NNNNNN格式，不符合则标记错误",
                    priority: 9,
                    status: "active",
                    tags: ["employee", "validation", "id"]
                },
                {
                    id: "val002",
                    name: "电子邮件验证",
                    description: "验证电子邮件格式",
                    condition: "当处理电子邮件字段时",
                    action: "验证格式是否符合标准电子邮件格式",
                    priority: 6,
                    status: "active",
                    tags: ["email", "validation", "format"]
                }
            ],
            "business": [
                {
                    id: "bus001",
                    name: "审批流程规则",
                    description: "定义审批流程中的权限和顺序",
                    condition: "当创建审批请求时",
                    action: "按照组织结构确定审批链，并设置每级审批的时限",
                    priority: 10,
                    status: "active",
                    tags: ["approval", "workflow", "permission"]
                }
            ]
        };
        
        // 文档加载完成后执行
        document.addEventListener('DOMContentLoaded', function() {
            // 初始化模态框 - 使用新的DOM工具
            ruleModalInstance = new bootstrap.Modal(DOMUtils.getElement('ruleModal'));
            deleteModalInstance = new bootstrap.Modal(DOMUtils.getElement('deleteConfirmModal'));
            relationshipModalInstance = new bootstrap.Modal(DOMUtils.getElement('relationshipModal'));
            ruleDetailModalInstance = new bootstrap.Modal(DOMUtils.getElement('ruleDetailModal')); // 初始化规则详情模态框
            connectionsModalInstance = new bootstrap.Modal(DOMUtils.getElement('connectionsModal')); // 初始化连接符管理模态框
            
            // 直接加载关系规则类型，不加载标准规则类型
            loadRelationshipTypes();
            
            // 初始化规则类型导航
            initRuleTypeNav();
            
            // 搜索按钮事件 - 使用新的DOM工具
            DOMUtils.getElement('search-button').addEventListener('click', function() {
                const searchValue = DOMUtils.getElementValue('search-input').toLowerCase();
                filterRules(searchValue);
            });
            
            // 搜索输入框回车事件 - 使用新的DOM工具
            DOMUtils.getElement('search-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const searchValue = DOMUtils.getElementValue('search-input').toLowerCase();
                    filterRules(searchValue);
                }
            });
            
            // 添加规则按钮事件 - 使用新的DOM工具
            DOMUtils.getElement('add-rule-btn').addEventListener('click', function() {
                showAddRuleModal();
            });
            
            // 保存规则按钮事件 - 使用新的DOM工具
            DOMUtils.getElement('save-rule-btn').addEventListener('click', function() {
                saveRule();
            });
            
            // 保存关系规则按钮事件 - 使用新的DOM工具
            DOMUtils.getElement('save-relationship-btn').addEventListener('click', function() {
                saveRelationshipRule();
            });
            
            // 确认删除按钮事件 - 使用新的DOM工具
            DOMUtils.getElement('confirm-delete-btn').addEventListener('click', function() {
                if (ruleToDelete) {
                    deleteRule(ruleToDelete.ruleType, ruleToDelete.id);
                }
            });
            
            // 加载更多按钮事件 - 使用新的DOM工具
            const loadMoreBtn = DOMUtils.getElement('load-more-btn');
            if (loadMoreBtn) {
                loadMoreBtn.addEventListener('click', function() {
                    loadMoreRules();
                });
            }
            
            // 自动生成代码列表复选框事件 - 使用新的DOM工具
            DOMUtils.getElement('auto-generate-codes').addEventListener('change', function() {
                DOMUtils.setElementDisplay('manual-codes-container', this.checked ? 'none' : 'block');
            });
            
            // 管理连接符按钮事件 - 使用新的DOM工具
            DOMUtils.getElement('manage-connections-btn').addEventListener('click', function() {
                showConnectionsModal();
            });
            
            // 连接符管理相关事件 - 使用新的DOM工具
            DOMUtils.getElement('add-connection-btn').addEventListener('click', function() {
                addNewConnection();
            });
            
            DOMUtils.getElement('new-connection-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    addNewConnection();
                }
            });
            
            DOMUtils.getElement('save-connections-btn').addEventListener('click', function() {
                saveConnections();
            });
        });
        
        // 初始化规则类型导航 - 使用新的DOM工具
        function initRuleTypeNav() {
            const relationshipRulesLink = DOMUtils.getElement('relationship-rules-link');
            
            // 关系规则链接事件
            relationshipRulesLink.addEventListener('click', function(e) {
                e.preventDefault();
                
                // 确保关系规则链接保持激活状态
                relationshipRulesLink.classList.add('active');
                
                // 显示关系规则部分
                DOMUtils.setElementDisplay('relationship-rules-section', 'block');
                
                // 隐藏规则列表和详情
                DOMUtils.setElementDisplay('rules-section', 'none');
                DOMUtils.setElementDisplay('rule-detail-section', 'none');
                DOMUtils.setElementDisplay('search-section', 'none');
                DOMUtils.setElementDisplay('current-type-section', 'none');
                
                // 加载关系规则类型
                loadRelationshipTypes();
            });
        }
        
        // 加载关系规则类型 - 使用新的API工具
        async function loadRelationshipTypes() {
            console.log("开始加载关系规则类型");
            
            APIUtils.setLoadingState('relationship-types-loading', true);
            
            try {
                const data = await APIUtils.call(`${API_BASE_URL}/api/relationship/`);
                renderRelationshipTypes(data);
            } catch (error) {
                showError('获取关系规则类型失败: ' + error.message);
                APIUtils.showApiError('relationship-types-container', error, '加载关系规则类型');
            } finally {
                APIUtils.setLoadingState('relationship-types-loading', false);
            }
        }
        
        // 渲染关系规则类型 - 使用新的DOM工具
        function renderRelationshipTypes(data) {
            const costContainer = DOMUtils.getElement('cost-relationship-types-container');
            const vpoContainer = DOMUtils.getElement('vpo-relationship-types-container');
            DOMUtils.setElementHTML(costContainer.id, '');
            DOMUtils.setElementHTML(vpoContainer.id, '');

            const rulesMaps = data.rulesMaps || [];
            
            if (rulesMaps.length === 0) {
                DOMUtils.setElementHTML('cost-relationship-types-container', 
                    '<div class="col-12 text-center"><p>没有可用的关系规则类型</p></div>');
                return;
            }

            const costRules = rulesMaps.filter(type => !type.id.includes('vpo'));
            const vpoRules = rulesMaps.filter(type => type.id.includes('vpo'));

            const renderToContainer = (container, rules) => {
                if (rules.length === 0) {
                    DOMUtils.setElementHTML(container.id, '<div class="col-12 text-center mt-3"><p>没有该类型的规则</p></div>');
                    return;
                }
                rules.forEach(type => {
                    const card = document.createElement('div');
                    card.className = 'col-md-4 mb-3';
                    card.innerHTML = `
                        <div class="card h-100">
                            <div class="card-body">
                                <h5 class="card-title">${type.description}</h5>
                                <p class="card-text"><small class="text-muted">ID: ${type.id}</small></p>
                                <p class="card-text"><small class="text-muted">文件: ${type.fileName}</small></p>
                                <button class="btn btn-primary btn-sm view-relationship-btn" data-type="${type.id}" data-name="${type.description}">
                                    <i class="bi bi-eye"></i> 查看规则
                                </button>
                            </div>
                        </div>
                    `;
                    container.appendChild(card);
                });
            };

            renderToContainer(costContainer, costRules);
            renderToContainer(vpoContainer, vpoRules);
            
            // 为所有"查看规则"按钮添加事件监听
            DOMUtils.getElements('.view-relationship-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const relationshipType = this.getAttribute('data-type');
                    const typeName = this.getAttribute('data-name');
                    loadRelationshipRules(relationshipType, typeName);
                });
            });
        }
        
        // 加载指定类型的关系规则 - 使用新的工具函数
        async function loadRelationshipRules(relationshipType, typeName) {
            currentRelationshipType = relationshipType;
            currentRelationshipTypeName = typeName || relationshipType;
            
            console.log("开始加载关系规则:", relationshipType, typeName);
            
            // 显示当前规则类型标签
            DOMUtils.setElementDisplay('current-type-section', 'flex');
            DOMUtils.setElementContent('current-type-tag', currentRelationshipTypeName);
            
            // 设置搜索区域和添加按钮
            DOMUtils.setElementDisplay('search-section', 'flex');
            const addBtn = DOMUtils.getElement('add-rule-btn');
            if (addBtn) {
                addBtn.innerHTML = '<i class="bi bi-plus-circle"></i> 添加关系规则';
                addBtn.onclick = function() {
                    showAddRelationshipModal();
                };
            }
            
            // 设置页面区域显示状态
            DOMUtils.setElementDisplay('rules-section', 'block');
            DOMUtils.setElementHTML('rules-list', '');
            DOMUtils.setElementDisplay('rule-detail-section', 'none');
            
            // 开始API调用
            APIUtils.setLoadingState('rules-loading', true);
            
            try {
                const apiUrl = `${API_BASE_URL}/api/relationship/${relationshipType}/rules`;
                console.log("调用关系规则API:", apiUrl);
                
                const data = await APIUtils.call(apiUrl);
                currentRelationshipRules = data.rules || [];
                renderRelationshipRules(currentRelationshipRules);
            } catch (error) {
                showError('获取关系规则失败: ' + error.message);
                
                // 显示错误信息在规则列表中
                DOMUtils.setElementHTML('rules-list', `
                    <li class="list-group-item">
                        <div class="alert alert-danger mb-0">
                            <h5><i class="bi bi-exclamation-triangle"></i> 加载关系规则失败</h5>
                            <p>${error.message}</p>
                            <p>请检查网络连接并<a href="javascript:location.reload()" class="alert-link">刷新页面</a>重试。</p>
                        </div>
                    </li>
                `);
            } finally {
                APIUtils.setLoadingState('rules-loading', false);
            }
        }
        
        // 渲染关系规则列表 - 使用新的DOM工具
        function renderRelationshipRules(rules) {
            DOMUtils.setElementHTML('rules-list', '');
            DOMUtils.setElementContent('rule-count', rules.length);
            
            if (rules.length === 0) {
                DOMUtils.setElementHTML('rules-list', '<li class="list-group-item text-center">没有关系规则数据</li>');
                return;
            }
            
            // 存储所有规则
            currentRelationshipRules = rules;
            
            // 直接显示所有规则，不进行分页
            displayedRelationshipRules = rules;
            
            // 渲染所有规则
            renderRelationshipRuleItems(displayedRelationshipRules);
            
            // 隐藏"加载更多"按钮，因为已经显示了所有规则
            DOMUtils.setElementDisplay('load-more-btn', 'none');
        }
        
        // 渲染关系规则项 - 使用新的DOM工具
        function renderRelationshipRuleItems(rules) {
            const container = DOMUtils.getElement('rules-list');
            
            rules.forEach((rule, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item rule-row';
                
                listItem.innerHTML = `
                    <div class="row align-items-center">
                        <div class="col-md-1">${index + 1}</div>
                        <div class="col-md-2">${rule.id || ''}</div>
                        <div class="col-md-3">${rule.name || ''}</div>
                        <div class="col-md-4">基础代码: ${rule.codebase || ''}</div>
                        <div class="col-md-2">
                            <button class="btn btn-sm btn-outline-info me-1 view-relationship-detail-btn" title="查看详情"><i class="bi bi-eye"></i></button>
                            <button class="btn btn-sm btn-outline-primary me-1 edit-relationship-btn" title="编辑"><i class="bi bi-pencil"></i></button>
                            <button class="btn btn-sm btn-outline-danger delete-relationship-btn" title="删除"><i class="bi bi-trash"></i></button>
                        </div>
                    </div>
                `;
                
                // 添加点击事件
                listItem.addEventListener('click', function(e) {
                    if (!e.target.closest('button')) {
                        showRelationshipDetail(rule);
                    }
                });
                
                // 添加查看按钮点击事件
                const viewBtn = listItem.querySelector('.view-relationship-detail-btn');
                viewBtn.addEventListener('click', function() {
                    showRelationshipDetail(rule);
                });
                
                // 添加编辑按钮点击事件
                const editBtn = listItem.querySelector('.edit-relationship-btn');
                editBtn.addEventListener('click', function() {
                    showEditRelationshipModal(rule);
                });
                
                // 添加删除按钮点击事件
                const deleteBtn = listItem.querySelector('.delete-relationship-btn');
                deleteBtn.addEventListener('click', function() {
                    showDeleteRelationshipConfirm(rule.id);
                });
                
                container.appendChild(listItem);
            });
        }
        
        // 显示关系规则详情
        function showRelationshipDetail(rule) {
            const container = document.getElementById('rule-detail-modal-container');
            
            let codeListHtml = '';
            if (rule.codeList && rule.codeList.length > 0) {
                codeListHtml = `
                <div class="mb-3">
                    <h6>代码组合列表 (共${rule.codeList.length}项):</h6>
                    <div class="code-list-scroll">
                        <ul class="list-unstyled mb-0">
                            ${rule.codeList.map(code => `<li>${code}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                `;
            }
            
            container.innerHTML = `
                <div class="detail-card">
                    <h4>
                        ${rule.name || '未命名'} 
                        <span class="badge bg-secondary">ID: ${rule.id || ''}</span>
                    </h4>
                    
                    <div class="mb-3">
                        <h6>基础代码:</h6>
                        <div class="highlight-code">${rule.codebase || '无基础代码'}</div>
                        <small class="text-muted">格式: "01;02|03|04" 其中 ";" 表示固定顺序，"|" 表示可交换顺序</small>
                    </div>
                    
                    <div class="mb-3">
                        <h6>代码数量:</h6>
                        <p>${rule.codecount || 0}</p>
                    </div>
                    
                    ${codeListHtml}
                </div>
            `;
            
            // 设置模态框标题
            document.getElementById('ruleDetailModalLabel').textContent = `规则详情: ${rule.name || '未命名'}`;
            
            // 显示模态框
            ruleDetailModalInstance.show();
        }
        
        // 显示添加关系规则模态框 - 使用新的工具函数
        function showAddRelationshipModal() {
            if (!currentRelationshipType) {
                showError('请先选择一个关系规则类型');
                return;
            }
            
            ModalUtils.setupModal('relationshipModalLabel', '添加关系规则', 'relationship-edit-mode', 'add', 'relationship-original-id', '');
            
            // 清空表单
            const form = DOMUtils.getElement('relationship-form');
            if (form) form.reset();
            
            // 生成新ID (找到最大ID + 1)
            let maxId = 0;
            currentRelationshipRules.forEach(rule => {
                const id = parseInt(rule.id);
                if (!isNaN(id) && id > maxId) {
                    maxId = id;
                }
            });
            
            DOMUtils.setElementValue('relationship-id', maxId + 1);
            
            // 显示模态框
            relationshipModalInstance.show();
        }
        
        // 显示编辑关系规则模态框 - 使用新的工具函数
        function showEditRelationshipModal(rule) {
            ModalUtils.setupModal('relationshipModalLabel', '编辑关系规则', 'relationship-edit-mode', 'edit', 'relationship-original-id', rule.id);
            
            // 填充表单数据
            const formData = {
                'relationship-id': rule.id || '',
                'relationship-name': rule.name || '',
                'relationship-codebase': rule.codebase || ''
            };
            FormUtils.fillFormData(formData);
            
            // 设置代码列表选项
            const autoGenerateElement = DOMUtils.getElement('auto-generate-codes');
            if (autoGenerateElement) autoGenerateElement.checked = true;
            DOMUtils.setElementDisplay('manual-codes-container', 'none');
            
            if (rule.codeList && rule.codeList.length > 0) {
                DOMUtils.setElementValue('relationship-codes', rule.codeList.join('\n'));
            }
            
            // 显示模态框
            relationshipModalInstance.show();
        }
        
        // 保存关系规则 - 使用新的工具函数
        async function saveRelationshipRule() {
            if (!currentRelationshipType) {
                showError('请先选择一个关系规则类型');
                return;
            }
            
            // 获取表单数据
            const formData = FormUtils.getFormData([
                'relationship-edit-mode', 'relationship-original-id', 'relationship-id',
                'relationship-name', 'relationship-codebase'
            ]);
            
            const editMode = formData['relationship-edit-mode'];
            const originalId = formData['relationship-original-id'];
            const id = parseInt(formData['relationship-id']);
            const name = formData['relationship-name'];
            const codebase = formData['relationship-codebase'];
            const autoGenerateCodes = DOMUtils.getElement('auto-generate-codes').checked;
            
            // 验证必填字段
            const requiredFields = { id, name, codebase };
            if (!FormUtils.validateRequired(requiredFields, showError)) {
                return;
            }
            
            // 生成代码列表或使用手动输入的代码列表
            let codeList = [];
            let codecount = 0;
            
            if (autoGenerateCodes) {
                // 自动生成代码列表
                codeList = generateCodeList(codebase);
                codecount = codeList.length;
            } else {
                // 使用手动输入的代码列表
                const codesText = DOMUtils.getElementValue('relationship-codes');
                codeList = codesText.split('\n').filter(line => line.trim() !== '');
                codecount = codeList.length;
            }
            
            // 构建规则数据
            const ruleData = {
                id: id,
                name: name,
                codebase: codebase,
                codecount: codecount,
                codeList: codeList
            };
            
            try {
                // 获取当前关系规则文件
                const data = await APIUtils.call(`${API_BASE_URL}/api/relationship/${currentRelationshipType}`);
                
                // 获取当前规则文件的所有规则
                const rulesMap = data.rules.rulesMap || [];
                
                if (editMode === 'add') {
                    // 添加新规则
                    rulesMap.push(ruleData);
                } else {
                    // 更新现有规则
                    const index = rulesMap.findIndex(r => r.id == originalId);
                    if (index !== -1) {
                        rulesMap[index] = ruleData;
                    } else {
                        rulesMap.push(ruleData);
                    }
                }
                
                // 更新规则文件
                const updatedData = { rulesMap: rulesMap };
                
                await APIUtils.call(`${API_BASE_URL}/api/relationship/${currentRelationshipType}`, {
                    method: 'POST',
                    body: JSON.stringify(updatedData)
                });
                
                showSuccess(editMode === 'add' ? '规则添加成功' : '规则更新成功');
                
                // 隐藏模态框
                relationshipModalInstance.hide();
                
                // 重新加载规则列表
                loadRelationshipRules(currentRelationshipType, currentRelationshipTypeName);
                
            } catch (error) {
                console.error('保存规则出错:', error);
                showError('保存规则失败: ' + error.message);
            }
        }
        


        // 显示连接符管理模态框 - 基于当前关系规则类型
        function showConnectionsModal() {
            if (!currentRelationshipType) {
                showError('请先选择一个关系规则类型');
                return;
            }
            
            currentConnectionsBusinessObject = currentRelationshipType;
            
            // 设置业务对象显示
            const displayName = currentRelationshipTypeName || currentRelationshipType;
            DOMUtils.setElementContent('current-business-object', displayName);
            
            // 清空输入框
            DOMUtils.setElementValue('new-connection-input', '');
            
            // 显示模态框
            connectionsModalInstance.show();
            
            // 加载连接符数据
            loadConnections(currentRelationshipType);
        }
        
        // 加载连接符数据 - 使用新的API工具
        async function loadConnections(businessObject) {
            APIUtils.setLoadingState('connections-loading', true);
            DOMUtils.setElementHTML('connections-table-body', '');
            DOMUtils.setElementDisplay('no-connections-message', 'none');
            
            try {
                const data = await APIUtils.call(`${API_BASE_URL}/api/connection/${businessObject}`);
                console.log('连接符数据:', data);
                
                // 提取连接符列表
                let connections = [];
                if (data.connectionList && data.connectionList.length > 0) {
                    connections = data.connectionList[0].connections || [];
                }
                
                currentConnections = [...connections];
                originalConnections = [...connections];
                
                renderConnections(connections);
            } catch (error) {
                console.error('加载连接符出错:', error);
                showError('加载连接符失败: ' + error.message);
                DOMUtils.setElementHTML('connections-table-body', `
                    <tr>
                        <td colspan="3" class="text-center text-danger">
                            <i class="bi bi-exclamation-triangle"></i> 
                            加载失败: ${error.message}
                        </td>
                    </tr>
                `);
            } finally {
                APIUtils.setLoadingState('connections-loading', false);
            }
        }
        
        // 渲染连接符列表 - 使用新的DOM工具
        function renderConnections(connections) {
            const tableBody = DOMUtils.getElement('connections-table-body');
            
            DOMUtils.setElementHTML('connections-table-body', '');
            DOMUtils.setElementContent('connections-count', connections.length);
            
            if (connections.length === 0) {
                DOMUtils.setElementDisplay('no-connections-message', 'block');
                return;
            }
            
            DOMUtils.setElementDisplay('no-connections-message', 'none');
            
            connections.forEach((connection, index) => {
                const row = document.createElement('tr');
                row.className = 'connection-item';
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>
                        <input type="text" class="connection-edit-input" 
                               value="${connection}" data-index="${index}"
                               pattern="^\\d{2},\\d{2}$">
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-danger delete-connection-btn" 
                                data-index="${index}" title="删除">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                
                tableBody.appendChild(row);
            });
            
            // 为删除按钮添加事件
            DOMUtils.getElements('.delete-connection-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const index = parseInt(this.getAttribute('data-index'));
                    deleteConnection(index);
                });
            });
            
            // 为编辑输入框添加验证事件
            document.querySelectorAll('.connection-edit-input').forEach(input => {
                input.addEventListener('blur', function() {
                    validateConnectionInput(this);
                });
                
                input.addEventListener('input', function() {
                    const index = parseInt(this.getAttribute('data-index'));
                    currentConnections[index] = this.value;
                });
            });
        }
        
        // 添加新连接符 - 使用新的工具函数
        function addNewConnection() {
            const value = DOMUtils.getElementValue('new-connection-input').trim();
            
            if (!value) {
                showError('请输入连接符');
                return;
            }
            
            if (!validateConnectionFormat(value)) {
                showError('连接符格式错误，请使用格式：01,02');
                return;
            }
            
            if (currentConnections.includes(value)) {
                showError('该连接符已存在');
                return;
            }
            
            currentConnections.push(value);
            renderConnections(currentConnections);
            
            // 清空输入框
            DOMUtils.setElementValue('new-connection-input', '');
            
            showSuccess('连接符添加成功');
        }
        
        // 删除连接符
        function deleteConnection(index) {
            if (index >= 0 && index < currentConnections.length) {
                const connection = currentConnections[index];
                
                if (confirm(`确定要删除连接符 "${connection}" 吗？`)) {
                    currentConnections.splice(index, 1);
                    renderConnections(currentConnections);
                    showSuccess('连接符删除成功');
                }
            }
        }
        
        // 验证连接符格式
        function validateConnectionFormat(value) {
            const pattern = /^\d{2},\d{2}$/;
            return pattern.test(value);
        }
        
        // 验证连接符输入框
        function validateConnectionInput(input) {
            const value = input.value.trim();
            
            if (!validateConnectionFormat(value)) {
                input.classList.add('connection-validation-error');
                return false;
            } else {
                input.classList.remove('connection-validation-error');
                return true;
            }
        }
        
        // 保存连接符
        function saveConnections() {
            if (!currentConnectionsBusinessObject) {
                showError('无效的业务对象');
                return;
            }
            
            // 验证所有连接符
            let hasError = false;
            document.querySelectorAll('.connection-edit-input').forEach(input => {
                if (!validateConnectionInput(input)) {
                    hasError = true;
                }
            });
            
            if (hasError) {
                showError('请修正格式错误的连接符');
                return;
            }
            
            // 检查是否有重复
            const uniqueConnections = [...new Set(currentConnections)];
            if (uniqueConnections.length !== currentConnections.length) {
                showError('存在重复的连接符，请检查');
                return;
            }
            
            // 构建更新数据
            const updateData = {
                businessObject: currentConnectionsBusinessObject,
                connectionList: [
                    {
                        id: 1,
                        description: "业务对象连接",
                        connections: currentConnections
                    }
                ]
            };
            
            // 发送保存请求
            fetch(`${API_BASE_URL}/api/connection/${currentConnectionsBusinessObject}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { 
                        throw new Error(err.detail || '保存连接符失败'); 
                    });
                }
                return response.json();
            })
            .then(result => {
                showSuccess('连接符保存成功');
                originalConnections = [...currentConnections];
                
                // 隐藏模态框
                connectionsModalInstance.hide();
            })
            .catch(error => {
                console.error('保存连接符出错:', error);
                showError('保存连接符失败: ' + error.message);
            });
        }
        
        // 生成代码列表
        function generateCodeList(codebase) {
            // 分割基础代码
            const segments = codebase.split(';');
            const codeList = [];
            
            // 解析每个片段，检查是否有可交换部分
            const segmentOptions = segments.map(segment => {
                if (segment.includes('|')) {
                    // 可交换部分，返回所有可能选项
                    return segment.split('|');
                } else {
                    // 固定部分，返回单一选项
                    return [segment];
                }
            });
            
            // 生成所有可能的组合
            function generateCombinations(current, index) {
                if (index === segmentOptions.length) {
                    codeList.push(current.join(';'));
                    return;
                }
                
                for (const option of segmentOptions[index]) {
                    const newCurrent = [...current];
                    newCurrent.push(option);
                    generateCombinations(newCurrent, index + 1);
                }
            }
            
            generateCombinations([], 0);
            
            return codeList;
        }
        
        // 显示删除关系规则确认
        function showDeleteRelationshipConfirm(ruleId) {
            ruleToDelete = { ruleType: currentRelationshipType, id: ruleId };
            deleteModalInstance.show();
        }
        
        // 加载规则类型列表
        function loadRuleTypes() {
            const loadingElement = document.getElementById('rule-types-loading');
            if (loadingElement) {
                loadingElement.style.display = 'inline-block';
            }
            
            // 实际项目中，这里会使用fetch调用API
            // 现在使用模拟数据
            setTimeout(() => {
                renderRuleTypes(mockRuleTypes);
                const loadingElement = document.getElementById('rule-types-loading');
                if (loadingElement) {
                    loadingElement.style.display = 'none';
                }
            }, 500);
        }
        
        // 渲染规则类型列表
        function renderRuleTypes(ruleTypes) {
            const container = document.getElementById('rule-types-container');
            container.innerHTML = '';
            
            if (ruleTypes.length === 0) {
                container.innerHTML = '<div class="col-12 text-center"><p>没有可用的规则类型</p></div>';
                return;
            }
            
            ruleTypes.forEach(type => {
                const card = document.createElement('div');
                card.className = 'col-md-3 mb-3';
                card.innerHTML = `
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">${type.name}</h5>
                            <p class="card-text">${type.description}</p>
                            <p class="card-text"><small class="text-muted">规则数量: ${type.itemCount || 0}</small></p>
                            <button class="btn btn-primary btn-sm view-rules-btn" data-type="${type.id}" data-name="${type.name}">
                                <i class="bi bi-eye"></i> 查看规则
                            </button>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
            
            // 为所有"查看规则"按钮添加事件监听
            document.querySelectorAll('.view-rules-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const ruleType = this.getAttribute('data-type');
                    const typeName = this.getAttribute('data-name');
                    loadRules(ruleType, typeName);
                });
            });
        }
        
        // 加载指定类型的规则
        function loadRules(ruleType, typeName) {
            currentRuleType = ruleType;
            currentRuleTypeName = typeName || ruleType;
            
            // 获取DOM元素
            const currentTypeSection = document.getElementById('current-type-section');
            const currentTypeTag = document.getElementById('current-type-tag');
            const searchSection = document.getElementById('search-section');
            const rulesSection = document.getElementById('rules-section');
            const rulesLoading = document.getElementById('rules-loading');
            const rulesList = document.getElementById('rules-list');
            const ruleDetailSection = document.getElementById('rule-detail-section');
            
            // 显示当前规则类型标签
            if (currentTypeSection) currentTypeSection.style.display = 'flex';
            if (currentTypeTag) currentTypeTag.textContent = currentRuleTypeName;
            
            // 确保元素存在后再访问其属性
            if (searchSection) searchSection.style.display = 'flex';
            if (rulesSection) rulesSection.style.display = 'block';
            if (rulesLoading) rulesLoading.style.display = 'inline-block';
            if (rulesList) rulesList.innerHTML = '';
            
            // 隐藏详情区域
            if (ruleDetailSection) ruleDetailSection.style.display = 'none';
            
            // 实际项目中，这里会使用fetch调用API
            // 现在使用模拟数据
            setTimeout(() => {
                currentRules = mockRules[ruleType] || [];
                renderRules(currentRules);
                if (rulesLoading) rulesLoading.style.display = 'none';
            }, 300);
        }
        
        // 渲染规则列表
        function renderRules(rules) {
            const container = document.getElementById('rules-list');
            container.innerHTML = '';
            document.getElementById('rule-count').textContent = rules.length;
            
            if (rules.length === 0) {
                container.innerHTML = '<li class="list-group-item text-center">没有规则数据</li>';
                return;
            }
            
            // 存储所有规则
            currentRules = rules;
            
            // 直接显示所有规则，不进行分页
            displayedRules = rules;
            
            // 渲染所有规则
            renderRuleItems(displayedRules);
            
            // 隐藏"加载更多"按钮，因为已经显示了所有规则
            const loadMoreBtn = document.getElementById('load-more-btn');
            if (loadMoreBtn) {
                loadMoreBtn.style.display = 'none';
            }
        }
        
        // 渲染规则项
        function renderRuleItems(rules) {
            const container = document.getElementById('rules-list');
            
            rules.forEach((rule, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item rule-row';
                
                const statusBadge = rule.status === 'active' 
                    ? '<span class="badge bg-success me-1">激活</span>' 
                    : '<span class="badge bg-secondary me-1">未激活</span>';
                
                listItem.innerHTML = `
                    <div class="row align-items-center">
                        <div class="col-md-1">${index + 1}</div>
                        <div class="col-md-2">${rule.id || ''}</div>
                        <div class="col-md-3">${rule.name || ''} ${statusBadge}</div>
                        <div class="col-md-4">${rule.description || ''}</div>
                        <div class="col-md-2">
                            <button class="btn btn-sm btn-outline-info me-1 view-detail-btn" title="查看详情"><i class="bi bi-eye"></i></button>
                            <button class="btn btn-sm btn-outline-primary me-1 edit-rule-btn" title="编辑"><i class="bi bi-pencil"></i></button>
                            <button class="btn btn-sm btn-outline-danger delete-rule-btn" title="删除"><i class="bi bi-trash"></i></button>
                        </div>
                    </div>
                `;
                
                // 添加点击事件
                listItem.addEventListener('click', function(e) {
                    if (!e.target.closest('button')) {
                        showRuleDetail(rule);
                    }
                });
                
                // 添加查看按钮点击事件
                const viewBtn = listItem.querySelector('.view-detail-btn');
                viewBtn.addEventListener('click', function() {
                    showRuleDetail(rule);
                });
                
                // 添加编辑按钮点击事件
                const editBtn = listItem.querySelector('.edit-rule-btn');
                editBtn.addEventListener('click', function() {
                    showEditRuleModal(rule);
                });
                
                // 添加删除按钮点击事件
                const deleteBtn = listItem.querySelector('.delete-rule-btn');
                deleteBtn.addEventListener('click', function() {
                    showDeleteConfirm(currentRuleType, rule.id);
                });
                
                container.appendChild(listItem);
            });
        }
        
        // 显示规则详情
        function showRuleDetail(rule) {
            const container = document.getElementById('rule-detail-modal-container');
            
            const statusBadge = rule.status === 'active' 
                ? '<span class="badge bg-success me-1">激活</span>' 
                : '<span class="badge bg-secondary me-1">未激活</span>';
            
            let tagsHtml = '';
            if (rule.tags && rule.tags.length > 0) {
                tagsHtml = `
                <div class="mb-3">
                    <h6>标签:</h6>
                    <div>
                        ${rule.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                </div>
                `;
            }
            
            container.innerHTML = `
                <div class="detail-card">
                    <h4>
                        ${rule.name || '未命名'} 
                        <span class="badge bg-secondary">${rule.id || ''}</span>
                        ${statusBadge}
                    </h4>
                    
                    ${rule.description ? `
                    <div class="mb-3">
                        <h6>描述:</h6>
                        <p>${rule.description}</p>
                    </div>
                    ` : ''}
                    
                    <div class="mb-3">
                        <h6>条件:</h6>
                        <div class="highlight-code">${rule.condition || '无条件'}</div>
                    </div>
                    
                    <div class="mb-3">
                        <h6>行为:</h6>
                        <div class="highlight-code">${rule.action || '无行为'}</div>
                    </div>
                    
                    <div class="mb-3">
                        <h6>优先级:</h6>
                        <div class="progress">
                            <div class="progress-bar" role="progressbar" 
                                style="width: ${rule.priority * 10}%;" 
                                aria-valuenow="${rule.priority}" 
                                aria-valuemin="0" 
                                aria-valuemax="10">
                                ${rule.priority}/10
                            </div>
                        </div>
                    </div>
                    
                    ${tagsHtml}
                </div>
            `;
            
            // 设置模态框标题
            document.getElementById('ruleDetailModalLabel').textContent = `规则详情: ${rule.name || '未命名'}`;
            
            // 显示模态框
            ruleDetailModalInstance.show();
        }
        
        // 过滤规则
        function filterRules(searchValue) {
            if (!searchValue) {
                renderRules(currentRules);
                return;
            }
            
            const filtered = currentRules.filter(rule => {
                return (
                    (rule.name && rule.name.toLowerCase().includes(searchValue)) || 
                    (rule.id && rule.id.toLowerCase().includes(searchValue)) ||
                    (rule.description && rule.description.toLowerCase().includes(searchValue)) ||
                    (rule.condition && rule.condition.toLowerCase().includes(searchValue)) ||
                    (rule.action && rule.action.toLowerCase().includes(searchValue)) ||
                    (rule.tags && rule.tags.some(tag => tag.toLowerCase().includes(searchValue)))
                );
            });
            
            renderRules(filtered);
        }
        
        // 显示添加规则模态框
        function showAddRuleModal() {
            if (!currentRuleType) {
                showError('请先选择一个规则类型');
                return;
            }
            
            document.getElementById('ruleModalLabel').textContent = '添加规则';
            document.getElementById('edit-mode').value = 'add';
            document.getElementById('original-id').value = '';
            
            // 清空表单
            document.getElementById('rule-form').reset();
            
            // 生成新ID (根据当前规则类型的前缀 + 序号)
            let maxNum = 0;
            let prefix = '';
            
            switch (currentRuleType) {
                case 'relationship':
                    prefix = 'rel';
                    break;
                case 'transformation':
                    prefix = 'trans';
                    break;
                case 'validation':
                    prefix = 'val';
                    break;
                case 'business':
                    prefix = 'bus';
                    break;
                default:
                    prefix = 'rule';
            }
            
            currentRules.forEach(rule => {
                if (rule.id && rule.id.startsWith(prefix)) {
                    const numStr = rule.id.substring(prefix.length);
                    const num = parseInt(numStr);
                    if (!isNaN(num) && num > maxNum) {
                        maxNum = num;
                    }
                }
            });
            
            const nextId = prefix + (maxNum + 1).toString().padStart(3, '0');
            document.getElementById('rule-id').value = nextId;
            document.getElementById('rule-priority').value = 5;
            document.getElementById('rule-status').value = 'active';
            
            // 显示模态框
            ruleModalInstance.show();
        }
        
        // 显示编辑规则模态框
        function showEditRuleModal(rule) {
            document.getElementById('ruleModalLabel').textContent = '编辑规则';
            document.getElementById('edit-mode').value = 'edit';
            document.getElementById('original-id').value = rule.id;
            
            // 填充表单
            document.getElementById('rule-id').value = rule.id || '';
            document.getElementById('rule-name').value = rule.name || '';
            document.getElementById('rule-description').value = rule.description || '';
            document.getElementById('rule-condition').value = rule.condition || '';
            document.getElementById('rule-action').value = rule.action || '';
            document.getElementById('rule-priority').value = rule.priority || 5;
            document.getElementById('rule-status').value = rule.status || 'active';
            
            // 标签
            document.getElementById('rule-tags').value = 
                rule.tags && rule.tags.length > 0 
                ? rule.tags.join(', ') 
                : '';
            
            // 显示模态框
            ruleModalInstance.show();
        }
        
        // 保存规则
        function saveRule() {
            if (!currentRuleType) {
                showError('请先选择一个规则类型');
                return;
            }
            
            // 获取表单数据
            const editMode = document.getElementById('edit-mode').value;
            const originalId = document.getElementById('original-id').value;
            const id = document.getElementById('rule-id').value;
            const name = document.getElementById('rule-name').value;
            const description = document.getElementById('rule-description').value;
            const condition = document.getElementById('rule-condition').value;
            const action = document.getElementById('rule-action').value;
            const priority = parseInt(document.getElementById('rule-priority').value) || 5;
            const status = document.getElementById('rule-status').value;
            const tagsText = document.getElementById('rule-tags').value;
            
            // 验证必填字段
            if (!id || !name || !condition || !action) {
                showError('ID、名称、条件和行为为必填字段');
                return;
            }
            
            // 解析标签
            const tags = tagsText ? tagsText.split(',').map(tag => tag.trim()).filter(tag => tag) : [];
            
            // 构建规则数据
            const ruleData = {
                id: id,
                name: name,
                description: description,
                condition: condition,
                action: action,
                priority: priority,
                status: status,
                tags: tags
            };
            
            // 模拟保存操作 (实际中将调用API)
            if (editMode === 'add') {
                // 模拟添加
                if (!mockRules[currentRuleType]) {
                    mockRules[currentRuleType] = [];
                }
                mockRules[currentRuleType].push(ruleData);
                showSuccess('规则添加成功');
            } else {
                // 模拟更新
                const index = mockRules[currentRuleType].findIndex(r => r.id === originalId);
                if (index !== -1) {
                    mockRules[currentRuleType][index] = ruleData;
                    showSuccess('规则更新成功');
                } else {
                    showError('未找到要更新的规则');
                }
            }
            
            // 重新加载规则列表
            loadRules(currentRuleType);
            
            // 隐藏模态框
            ruleModalInstance.hide();
        }
        
        // 显示删除确认
        function showDeleteConfirm(ruleType, ruleId) {
            ruleToDelete = { ruleType, id: ruleId };
            deleteModalInstance.show();
        }
        
        // 删除规则
        function deleteRule(ruleType, ruleId) {
            // 模拟删除操作 (实际中将调用API)
            const index = mockRules[ruleType].findIndex(r => r.id === ruleId);
            if (index !== -1) {
                mockRules[ruleType].splice(index, 1);
                showSuccess('规则删除成功');
                
                // 隐藏删除确认模态框
                deleteModalInstance.hide();
                
                // 重新加载规则列表
                loadRules(ruleType);
                
                // 隐藏详情区域
                document.getElementById('rule-detail-section').style.display = 'none';
            } else {
                showError('未找到要删除的规则');
                deleteModalInstance.hide();
            }
        }
        
        // 显示成功消息 - 使用新的工具函数
        // 成功和错误消息函数已由工具库提供，直接使用：
        // MessageUtils.showSuccess(message) 或 showSuccess(message)
        // MessageUtils.showError(message) 或 showError(message)
