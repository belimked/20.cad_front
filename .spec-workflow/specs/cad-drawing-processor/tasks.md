# cad-drawing-processor 任务拆解

- [x] 1. 初始化项目骨架与依赖管理
  - 文件: `pyproject.toml`, `requirements.txt`, `src/caddxftool/__init__.py`, `src/caddxftool/cli.py`, `src/caddxftool/utils/logging.py`
  - 内容: 建立 Python 包结构，配置 Typer 入口、logging 初始化、引入所需依赖（typer、rich、ezdxf、shapely、numpy）
  - 目的: 为后续模块提供统一入口与环境
  - _Leverage: `.spec-workflow/specs/cad-drawing-processor/design.md`, `.spec-workflow/specs/cad-drawing-processor/requirements.md`_
  - _Requirements: 功能性需求 1-5, 非功能性需求 1-3_
  - _Prompt: Implement the task for spec cad-drawing-processor, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python 工程师熟悉 CLI 架构 | Task: 创建基础包结构与 Typer CLI 入口，配置 logging 与依赖清单，满足功能性需求 1-5 及非功能性需求 1-3 | Restrictions: 不引入未列出的依赖，保持 CLI 简洁，遵守项目目录规范 | _Leverage: `.spec-workflow/specs/cad-drawing-processor/design.md`, `.spec-workflow/specs/cad-drawing-processor/requirements.md`_ | _Requirements: 功能性需求 1-5, 非功能性需求 1-3_ | Success: CLI 可执行且输出帮助信息，logging 初始化可用，依赖文件完整，开始任务前将对应条目标记为 `[-]`，完成后改为 `[x]`_

- [x] 2. 实现配置与结果数据模型
  - 文件: `src/caddxftool/models.py`
  - 内容: 定义 ConvertConfig/SplitConfig/ConvertReport/SplitReport/RectangleRegion 等 dataclass
  - 目的: 提供服务层的参数与结果结构，确保类型一致性
  - _Leverage: `src/caddxftool/cli.py`, `.spec-workflow/specs/cad-drawing-processor/design.md`_
  - _Requirements: 功能性需求 1-4_
  - _Prompt: Implement the task for spec cad-drawing-processor, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python 后端工程师擅长数据建模 | Task: 根据设计文档实现配置与报告 dataclass，支撑转换与拆分流程 | Restrictions: 避免业务逻辑混入模型层，类型命名保持简洁 | _Leverage: `src/caddxftool/cli.py`, `.spec-workflow/specs/cad-drawing-processor/design.md`_ | _Requirements: 功能性需求 1-4_ | Success: 单元测试可导入模型且字段齐全，开始任务前将条目标记为 `[-]`，完成后改为 `[x]`_

- [x] 3. 完成 DWG→DXF 转换适配器与服务
  - 文件: `src/caddxftool/adapters/oda_converter.py`, `src/caddxftool/services/convert_service.py`
  - 内容: 调用 ODAFileConverter CLI、处理目录遍历、失败收集、覆盖策略
  - 目的: 满足批量转换需求并输出转换报告
  - _Leverage: `src/caddxftool/models.py`, `src/caddxftool/utils/logging.py`_
  - _Requirements: 功能性需求 1, 4, 非功能性需求 1-3
  - _Prompt: Implement the task for spec cad-drawing-processor, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python 工程师擅长系统集成 | Task: 实现 ODAFileConverter 适配器与批量转换服务，正确处理外部命令、错误与日志 | Restrictions: 不硬编码外部工具路径，失败需写入报告列表 | _Leverage: `src/caddxftool/models.py`, `src/caddxftool/utils/logging.py`_ | _Requirements: 功能性需求 1, 4, 非功能性需求 1-3_ | Success: 服务可被调用并返回报告对象，错误路径具备清晰日志，开始任务前标记 `[-]`，完成后改为 `[x]`_

- [x] 4. 实现 DXF 解析、矩形识别与子文件写入
  - 文件: `src/caddxftool/dxf/reader.py`, `src/caddxftool/dxf/rectangle_detector.py`, `src/caddxftool/dxf/writer.py`
  - 内容: 使用 ezdxf 读写，借助 numpy/shapely 识别方框并过滤实体
  - 目的: 支持按矩形区域拆分 DXF
  - _Leverage: `src/caddxftool/models.py`, `.spec-workflow/specs/cad-drawing-processor/design.md`_
  - _Requirements: 功能性需求 2-3, 非功能性需求 2-3
  - _Prompt: Implement the task for spec cad-drawing-processor, first run spec-workflow-guide to get the workflow guide then implement the task: Role: 几何算法方向的 Python 工程师 | Task: 构建 DXF 读取/矩形检测/子文件写入模块，确保矩形合法判断和实体过滤准确 | Restrictions: 避免代码重复，矩形识别需容差控制 | _Leverage: `src/caddxftool/models.py`, `.spec-workflow/specs/cad-drawing-processor/design.md`_ | _Requirements: 功能性需求 2-3, 非功能性需求 2-3_ | Success: 模块函数被单元测试覆盖并能导出正确的子 DXF，开始任务前标记 `[-]`，完成后改为 `[x]`_

- [x] 5. 编排 CLI 子命令与流程集成
  - 文件: `src/caddxftool/cli.py`
  - 内容: 将 `convert`、`split` 子命令接入服务层，处理参数、日志和退出码
  - 目的: 提供最终用户可执行的命令行体验
  - _Leverage: `src/caddxftool/services/convert_service.py`, `src/caddxftool/services/split_service.py`, `src/caddxftool/models.py`_
  - _Requirements: 功能性需求 1-5
  - _Prompt: Implement the task for spec cad-drawing-processor, first run spec-workflow-guide to get the workflow guide then implement the task: Role: CLI 工具专家 | Task: 将转换与拆分服务通过 Typer 子命令暴露，处理日志配置、参数验证与退出码 | Restrictions: 子命令必须有中文帮助说明，错误处理统一捕获并返回非零码 | _Leverage: `src/caddxftool/services/convert_service.py`, `src/caddxftool/services/split_service.py`, `src/caddxftool/models.py`_ | _Requirements: 功能性需求 1-5_ | Success: 两个子命令可运行并按需求输出信息，开始任务前标记 `[-]`，完成后改为 `[x]`_

- [x] 6. 编写测试与使用文档
  - 文件: `tests/test_rectangle_detector.py`, `tests/test_split_service.py`, `tests/conftest.py`, `README.md`
  - 内容: 使用 pytest 编写单元/集成测试，提供示例 DXF fixture，更新 README 说明安装与使用
  - 目的: 确保核心逻辑可靠并提供用户指导
  - _Leverage: `src/caddxftool/dxf/rectangle_detector.py`, `src/caddxftool/services/split_service.py`, `.spec-workflow/specs/cad-drawing-processor/requirements.md`_
  - _Requirements: 功能性需求 2-5, 非功能性需求 2-3, 验收标准 1-3
  - _Prompt: Implement the task for spec cad-drawing-processor, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python QA 工程师 | Task: 为矩形识别和拆分流程编写 pytest 测试并补充 README 使用说明，覆盖验收标准 | Restrictions: 测试需可在无真实 ODA 环境下运行（使用假数据/模拟），README 需提供中文步骤 | _Leverage: `src/caddxftool/dxf/rectangle_detector.py`, `src/caddxftool/services/split_service.py`, `.spec-workflow/specs/cad-drawing-processor/requirements.md`_ | _Requirements: 功能性需求 2-5, 非功能性需求 2-3, 验收标准 1-3_ | Success: 测试全部通过，README 包含安装与命令示例，开始任务前标记 `[-]`，完成后改为 `[x]`_
