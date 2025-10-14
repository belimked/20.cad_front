# CAD Drawing Processor

简体中文命令行工具，帮助工程师批量完成 DWG→DXF 转换，并基于矩形方框拆分 DXF 文件生成子图纸。

## 环境要求

- Python 3.10 及以上
- 已安装 [ODAFileConverter](https://www.opendesign.com/guestfiles/oda_file_converter)（或兼容的本地 DWG→DXF 转换工具）
- 依赖:
  - `typer`
  - `rich`
  - `ezdxf`
  - `shapely`
  - `numpy`
  - 开发测试依赖：`pytest`

## 安装

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .  # 可选，便于全局使用 `cad-dxftool`
```

若系统无法直接找到 `ODAFileConverter`，可通过环境变量或命令参数指定：

```bash
export PATH="/opt/ODA/bin:$PATH"
# 或在命令中添加 --oda-path /opt/ODA/ODAFileConverter
```

## 使用说明

### DWG → DXF 批量转换

```bash
cad-dxftool convert ./input-dwg --output-dir ./output-dxf --overwrite
```

- `--output-dir`：DXF 输出目录
- `--overwrite`：可选，允许覆盖已存在 DXF
- `--oda-path`：可选，指定 ODAFileConverter 可执行文件

执行完成后，会输出成功/失败摘要，失败项会显示详细原因。

### DXF 矩形拆分

```bash
cad-dxftool split ./output-dxf/sample.dxf --output-dir ./splits \
  --include-frame --naming-pattern "{name}_block_{index}.dxf"
```

- `--include-frame/--exclude-frame`：是否保留原方框实体
- `--naming-pattern`：子文件命名模板，支持 `{name}`（原文件名，不含扩展名）、`{index}`（序号）、`{id}`（方框实体 handle）

若 DXF 中不存在矩形方框，命令会给出警告但仍返回成功。

## 测试

```bash
pip install -r requirements.txt
pip install -e .[dev]
pytest
```

测试主要覆盖：
- 矩形识别逻辑
- 拆分服务的调用与错误处理

## 目录结构

```
src/caddxftool/
  cli.py               # Typer 命令行入口
  models.py            # 配置与报告数据模型
  exceptions.py        # 自定义异常
  adapters/            # 外部工具适配器
  services/            # 业务服务（转换、拆分）
  dxf/                 # DXF 解析、矩形检测、写入工具
```

## 常见问题

- **找不到 ODAFileConverter**：使用 `--oda-path` 指定执行文件，或将其加入 `PATH`。
- **拆分后文件为空**：确认 DXF 中矩形是闭合多段线，且为轴对齐。旋转矩形目前暂不支持。
- **测试无法运行**：确保安装开发依赖 `pytest`，并在命令前设置 `PYTHONPATH=src`（或使用 `pip install -e .`）。

欢迎按需扩展命名规则、矩形识别策略或导出逻辑，但请保持代码模块化与简洁。MD
