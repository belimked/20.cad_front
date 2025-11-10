# 文档索引

**项目**: CAD PDF Converter
**更新日期**: 2025-11-10
**总文档数**: 30+

本文档提供项目所有文档的索引和快速导航。

---

## 核心文档

### [产品需求文档 (PRD)](./prd.md)

完整的产品需求文档,包含项目目标、用户场景、功能需求、技术假设和5个Epic共27个Story的详细拆分。当前版本 v1.4,完整度88%。

### [项目简介](./project-brief.md)

项目概述文档,介绍技术栈(Tauri + Svelte + TypeScript + Rust)和核心功能(文件上传、远程接口调用、状态进度显示、PDF预览等)。

### [系统架构文档](./architecture.md)

完整的系统架构设计,包含整体架构、前端设计、Rust后端、数据流、状态管理、API集成、性能优化、安全考虑等17个章节。基于PRD v1.4编写。

---

## 开发指南

### [开发环境设置](./DEVELOPMENT_SETUP.md)

详细的开发环境配置指南,包含前置要求、环境安装步骤、项目配置、IDE设置和常见问题解决方案。

### [构建与打包指南](./BUILD_AND_PACKAGE.md)

Tauri应用打包完整指南,覆盖Windows、macOS、Linux三个平台的打包命令、产物位置、跨平台构建配置和故障排查。

### [跨平台构建指南](./CROSS_PLATFORM_BUILD.md)

详细说明如何在不同操作系统上进行跨平台构建,包含各平台特定的依赖安装和配置要求。

---

## 项目状态报告

### [项目完成报告](./PROJECT_COMPLETION_REPORT.md)

架构设计阶段完成报告,总结了需求分析、架构设计、脚手架创建、首次打包成功(macOS DMG 4.4MB)、CI/CD配置等成果。

### [脚手架摘要](./SCAFFOLD_SUMMARY.md)

项目脚手架创建摘要,列出已生成的42+文件的完整目录结构和各组件说明。

### [脚手架验证报告](./SCAFFOLD_VERIFICATION.md)

脚手架代码质量验证报告,包含编译检查、代码规范验证和构建测试结果。

### [构建进度报告](./build-progress-report.md)

详细的构建过程记录和问题解决报告。

### [构建进度摘要](./build-progress-summary.md)

构建进度的简要摘要和关键节点记录。

### [构建状态](./build-status.md)

当前构建状态和版本信息。

---

## API与集成

### [API迁移总结](./api-migration-summary.md)

记录API服务器迁移到 `http://10.3.19.63:8000` 的完整过程,包含接口变更、请求参数变化和响应格式更新。

### [API响应格式更新](./api-response-format-update.md)

详细说明新的标准API响应格式 `{code, message, data}` 的实现和兼容性处理方案。

### [DWG URL测试指南](./dwg-url-test-guide.md)

DWG文件URL测试面板使用指南,包含预设文件配置和测试流程说明。

### [Epic 2 实现总结](./epic2-implementation-summary.md)

Epic 2(异步任务处理与状态监控)的实现总结文档。

---

## CI/CD与发布

### [GitHub Actions配置](./github-actions.md)

GitHub Actions自动构建配置说明,包含CI workflow(代码质量检查)和Release Build workflow(多平台构建)的详细配置。

### [GitHub Actions修复记录](./github-actions-fixes.md)

GitHub Actions构建过程中遇到的问题和修复方案记录。

### [GitHub Token设置](./github-token-setup.md)

GitHub Token配置指南,用于CI/CD流程中的身份验证。

### [移除Linux构建总结](./remove-linux-build-summary.md)

记录移除Linux平台构建配置的原因和变更内容(仅保留macOS和Windows构建)。

---

## 架构评审

### [架构评审清单](./architecture-review-checklist.md)

架构评审检查清单,用于系统性评估架构设计的完整性和合理性。

### [架构评审决策点](./architecture-review-decision-points.md)

架构评审过程中的关键决策点记录和决策理由说明。

### [架构评审总结](./architecture-review-summary.md)

完整的架构评审会议总结,包含评审结论、改进建议和后续行动计划。

---

## Git配置

### [Git双远程配置](./git-dual-remote.md)

配置Git双远程仓库(GitHub和Gitee)的完整指南,包含推送策略和常用命令。

---

## Stories (用户故事)

开发任务以Story形式组织,位于 `stories/` 子目录。

### [Stories索引](./stories/STORIES_INDEX.md)

完整的用户故事索引,包含5个Epic共27个Story的规划。当前Epic 1的6个Story已创建(22%完成度)。

**Epic 1: 项目基础设施与核心文件上传** (6个Story已创建):

- [Story 1.1: 项目初始化与开发环境配置](./stories/epic-1-story-1.1-project-init.md) - Status: Ready for Review
- [Story 1.2: 基础UI框架与主界面布局](./stories/epic-1-story-1.2-ui-framework.md) - Status: Draft
- [Story 1.3: 文件选择对话框实现](./stories/epic-1-story-1.3-file-dialog.md) - Status: Draft
- [Story 1.4: 拖拽上传功能实现](./stories/epic-1-story-1.4-drag-drop.md) - Status: Draft
- [Story 1.5: 文件信息展示与验证](./stories/epic-1-story-1.5-file-info.md) - Status: Draft
- [Story 1.6: API调用服务层与文件上传](./stories/epic-1-story-1.6-api-upload.md) - Status: Draft

**其他Epic** (待创建):
- Epic 2: 异步任务处理与状态监控 (5个Story)
- Epic 3: PDF生成集成与文件关系可视化 (5个Story)
- Epic 4: PDF预览与文件下载 (6个Story)
- Epic 5: 任务历史管理与持久化 (5个Story)

---

## 文档分类

### 按阶段分类

**规划阶段**:
- 产品需求文档 (PRD)
- 项目简介
- 系统架构文档
- 架构评审文档(3个)

**开发阶段**:
- 开发环境设置
- Stories (27个用户故事)
- API迁移与集成文档(3个)

**构建与部署**:
- 构建与打包指南
- 跨平台构建指南
- GitHub Actions配置(3个)
- 构建报告(3个)

**项目管理**:
- 项目完成报告
- 脚手架验证(2个)
- Git配置

### 按受众分类

**产品经理**: PRD, 项目简介, Stories索引

**架构师**: 系统架构文档, 架构评审文档(3个)

**开发工程师**: 开发环境设置, Stories (27个), API文档(3个), Git配置

**DevOps工程师**: 构建与打包指南, 跨平台构建, GitHub Actions配置(3个)

**测试工程师**: Stories中的测试章节, DWG测试指南

**所有团队成员**: 项目完成报告, 构建状态

---

## 快速链接

- 🎯 **开始开发**: [开发环境设置](./DEVELOPMENT_SETUP.md) → [Story 1.1](./stories/epic-1-story-1.1-project-init.md)
- 📦 **构建应用**: [构建与打包指南](./BUILD_AND_PACKAGE.md)
- 🏗️ **理解架构**: [系统架构文档](./architecture.md)
- 📋 **查看需求**: [产品需求文档](./prd.md) → [Stories索引](./stories/STORIES_INDEX.md)
- 🔧 **配置CI/CD**: [GitHub Actions配置](./github-actions.md)

---

## 文档维护

本索引由自动化工具维护。如需更新:

1. 添加新文档后运行 `/index-docs` 命令
2. 文档移动或删除后重新生成索引
3. 定期检查并更新文档描述的准确性

**最后扫描**: 2025-11-10
**文档总数**: 30个 (24个根文档 + 6个Story文档)
**目录结构**: 根目录 + stories子目录
