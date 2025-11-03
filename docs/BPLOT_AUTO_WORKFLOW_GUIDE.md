# Bplot 全自动化工作流指南

## 📋 文件位置

**主文件：** `research/autocad_com_api/11_bplot_auto_workflow.py`

**类名：** `BplotAutoWorkflow`

---

## 🎯 功能概述

这是一个完全自动化的 AutoCAD Batch Plot (bplot) 工作流，实现从打开文件到提取图纸信息的全流程自动化。

**核心能力：**
- ✅ 自动打开 AutoCAD 和 DWG 文件
- ✅ OCR 识别界面按钮并自动点击
- ✅ 自动键盘输入和命令执行
- ✅ 截图并提取关键信息（选中图纸数、总页数）

---

## 🔄 完整执行流程

### **流程图**

```
┌─────────────────────────────────────────┐
│          BplotAutoWorkflow.run()         │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼          ▼          ▼
  步骤1      步骤2      步骤3      步骤4      步骤5      步骤6
  打开       验证       执行      OCR点击    键盘输入   提取信息
  文件       加载       BPLOT     按钮       all       截图OCR
    │          │          │          │          │          │
    ▼          ▼          ▼          ▼          ▼          ▼
  ✅         ✅         ✅         ✅         ✅         ✅
```

---

## 📝 详细步骤说明

### **步骤 1: `step1_open_cad_file()` - 打开 CAD 和文件**

**操作流程：**
1. 验证 DWG 文件存在
2. 关闭所有现有 AutoCAD 进程
3. 启动 AutoCAD 并打开文件
4. 连接 COM 接口
5. 等待文件加载完成

**等待时间：** 约 10-15 秒

---

### **步骤 2: `step2_verify_loaded()` - 验证文件加载**

**验证项：**
- ✓ AutoCAD 进程存活
- ✓ 文档对象可访问
- ✓ 模型空间实体可读

**超时时间：** 30 秒

---

### **步骤 3: `step3_execute_bplot()` - 执行 BPLOT 命令**

**操作：**
```python
self.current_doc.SendCommand("._BPLOT ")
# ._ = 英文命令前缀
# BPLOT = 批量打印命令
# (空格) = 回车确认
```

**等待时间：** 3 秒（对话框打开）

---

### **步骤 4: `step4_click_select_button()` - OCR 识别并点击按钮** ⭐

**核心逻辑：**

#### 4.1 截取 AutoCAD 窗口
```python
# 查找 AutoCAD 窗口句柄
hwnd = win32gui.FindWindow(含"AutoCAD"的标题)

# 获取窗口坐标
rect = win32gui.GetWindowRect(hwnd)

# 截图
image = ImageGrab.grab(bbox=rect)

# 保存到 screenshots/bplot_auto/
image.save(screenshot_path)
```

#### 4.2 Umi-OCR 识别文本
```python
# 发送 OCR 请求
files = {'image': screenshot_bytes}
response = requests.post(
    "http://10.3.19.121:1224/api/ocr",
    files=files,
    timeout=30
)

# 解析结果
ocr_results = response.json()
```

#### 4.3 查找目标按钮
```python
button_texts = [
    "选择批量打印图纸",   # 中文版
    "选择图纸",          # 简化中文
    "Select Drawings",   # 英文版
    "Add Sheets"         # 备用英文
]

# 遍历 OCR 结果
for item in ocr_results['data']:
    if target_text in item['text']:
        # 找到匹配项
        box = item['box']  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
```

#### 4.4 计算点击坐标
```python
# 计算文本框中心点
center_x = (box[0][0] + box[2][0]) // 2
center_y = (box[0][1] + box[2][1]) // 2

# 转换为屏幕坐标
screen_x = window_left + center_x
screen_y = window_top + center_y
```

#### 4.5 执行点击
```python
pyautogui.moveTo(screen_x, screen_y, duration=0.3)  # 移动 0.3 秒
time.sleep(0.2)                                      # 等待 0.2 秒
pyautogui.click()                                    # 点击
time.sleep(1)                                        # 等待响应
```

**截图示例：** `screenshots/bplot_auto/bplot_dialog_{timestamp}.png`

---

### **步骤 5: `step5_input_all()` - 输入 all 并回车** ⭐

**操作流程：**

#### 5.1 键盘输入
```python
# 逐字符输入（每个字符间隔 0.1 秒）
pyautogui.typewrite("all", interval=0.1)
# 输出: a -> l -> l
```

#### 5.2 发送回车
```python
time.sleep(0.5)          # 等待输入稳定
pyautogui.press("enter") # 按下回车键
time.sleep(2)            # 等待处理完成
```

**总耗时：** 约 3 秒

---

### **步骤 6: `step6_extract_sheet_info()` - 提取图纸信息** ⭐

**操作流程：**

#### 6.1 再次截图
```python
image = self._capture_autocad_window()
screenshot_path = f"bplot_info_{timestamp}.png"
image.save(screenshot_path)
```

#### 6.2 OCR 全文识别
```python
ocr_results = self._ocr_image(image)

# 提取所有文本
all_text = "\n".join([
    item['text']
    for item in ocr_results['data']
])
```

#### 6.3 正则表达式提取信息
```python
# 提取选中图纸数量
match_selected = re.search(r'选中图纸[:\s]*(\d+)', all_text)
if match_selected:
    selected_sheets = match_selected.group(1)  # 例如: "15"

# 提取总页数（支持多种格式）
patterns = [
    r'共\s*(\d+)\s*页',      # "共 15 页"
    r'Total[:\s]*(\d+)',      # "Total: 15"
    r'(\d+)\s*sheets',        # "15 sheets"
    r'页数[:\s]*(\d+)'        # "页数: 15"
]
for pattern in patterns:
    match = re.search(pattern, all_text, re.IGNORECASE)
    if match:
        total_pages = match.group(1)
        break
```

#### 6.4 返回结果
```python
{
    'selected_sheets': '15',  # 选中图纸数
    'total_pages': '15'       # 总页数
}
```

**截图示例：** `screenshots/bplot_auto/bplot_info_{timestamp}.png`

---

## 🛠️ 技术实现细节

### **1. 窗口截图机制**

```python
def _capture_autocad_window(self) -> Optional[Image.Image]:
    """截取AutoCAD窗口"""
    # 枚举所有窗口
    def find_window(hwnd, param):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'AutoCAD' in title or 'acad' in title.lower():
                return hwnd  # 找到目标窗口

    hwnd = win32gui.EnumWindows(find_window, None)

    # 获取窗口矩形区域
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    # PIL ImageGrab 截图
    image = ImageGrab.grab(bbox=(left, top, right, bottom))

    return image
```

**特点：**
- 只截取 AutoCAD 窗口区域（不含其他窗口）
- 包含对话框、菜单等所有可见内容
- 保存为 PNG 格式，便于 OCR 识别

---

### **2. Umi-OCR 服务调用**

```python
def _ocr_image(self, image: Image.Image) -> Optional[Dict]:
    """使用Umi-OCR识别图像"""
    # 图像转字节流
    from io import BytesIO
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # HTTP POST 请求
    files = {'image': ('screenshot.png', img_byte_arr, 'image/png')}
    response = requests.post(
        "http://10.3.19.121:1224/api/ocr",
        files=files,
        timeout=30
    )

    # 解析响应
    if response.status_code == 200:
        result = response.json()
        if result['code'] == 100:  # 成功
            return result
```

**返回格式：**
```json
{
    "code": 100,
    "data": [
        {
            "text": "选择批量打印图纸",
            "score": 0.95,
            "box": [[100, 200], [300, 200], [300, 230], [100, 230]]
        },
        {
            "text": "选中图纸: 15",
            "score": 0.92,
            "box": [[50, 300], [200, 300], [200, 330], [50, 330]]
        }
    ]
}
```

---

### **3. 文本查找与坐标计算**

```python
def _find_text_position(self, image, target_text):
    """在图像中查找文本位置"""
    ocr_results = self._ocr_image(image)

    for item in ocr_results['data']:
        text = item['text']

        # 模糊匹配（支持包含关系）
        if target_text in text or text in target_text:
            box = item['box']  # 四个顶点坐标

            # 计算边界框中心
            center_x = (box[0][0] + box[2][0]) // 2
            center_y = (box[0][1] + box[2][1]) // 2

            # 窗口坐标 → 屏幕坐标
            hwnd = find_autocad_window()
            window_rect = win32gui.GetWindowRect(hwnd)

            screen_x = window_rect[0] + center_x
            screen_y = window_rect[1] + center_y

            return (screen_x, screen_y)

    return None  # 未找到
```

**坐标系转换：**
```
截图坐标 (相对于窗口左上角)
    ↓
窗口坐标 (相对于窗口)
    ↓
屏幕坐标 (相对于显示器) → pyautogui.click()
```

---

### **4. 正则表达式提取**

```python
# 示例文本
ocr_text = """
批量打印设置
选中图纸: 15
共 15 页
输出路径: C:\Output
"""

# 提取选中图纸数
import re
match = re.search(r'选中图纸[:\s]*(\d+)', ocr_text)
# match.group(0) = "选中图纸: 15"
# match.group(1) = "15"

# 提取总页数
match = re.search(r'共\s*(\d+)\s*页', ocr_text)
# match.group(1) = "15"
```

**支持的格式：**
- 中文：`选中图纸: 15`、`共 15 页`
- 英文：`Selected: 15`、`Total: 15`
- 混合：`15 sheets`、`页数:15`

---

## 📸 截图存储

**目录结构：**
```
screenshots/
└── bplot_auto/
    ├── bplot_dialog_1730523456.png    # 对话框截图
    ├── bplot_info_1730523461.png      # 信息截图
    └── ...
```

**文件命名：**
- 格式：`{阶段}_{时间戳}.png`
- 时间戳：Unix 时间戳（10位数字）
- 自动创建目录，便于管理

---

## ⚙️ 配置参数

```python
class BplotAutoWorkflow:
    def __init__(
        self,
        umi_ocr_url: str = "http://10.3.19.121:1224/api/ocr"
    ):
        self.umi_ocr_url = umi_ocr_url
        self.screenshot_dir = Path("screenshots/bplot_auto")
```

**可配置项：**
- `umi_ocr_url`: Umi-OCR 服务地址
- `screenshot_dir`: 截图保存目录

---

## 🎯 使用示例

### **方式 1: 直接运行（测试）**

```python
from research.autocad_com_api.bplot_auto_workflow import BplotAutoWorkflow

# 创建工作流
workflow = BplotAutoWorkflow()

# 运行
success = workflow.run(dwg_file_path=r"C:\path\to\your\file.dwg")

if success:
    print("✅ 自动化完成！")
else:
    print("❌ 执行失败")
```

### **方式 2: 集成到 API**

```python
# 在 api/services/task_processor.py 中
from research.autocad_com_api.bplot_auto_workflow import BplotAutoWorkflow

def _run_autocad_workflow(self, ...):
    if use_bplot:
        # 使用全自动化 bplot 工作流
        workflow = BplotAutoWorkflow()
        success = workflow.run(dwg_file_path=dwg_file_path)

        # 获取提取的信息
        # sheet_info = workflow.last_sheet_info

        return success
```

---

## ⏱️ 性能指标

| 阶段 | 操作 | 耗时 |
|------|------|------|
| 步骤1 | 启动 AutoCAD + 打开文件 | 10-15 秒 |
| 步骤2 | 验证加载 | 2-5 秒 |
| 步骤3 | 执行 BPLOT | 3 秒 |
| 步骤4 | 截图 + OCR + 点击 | 3-5 秒 |
| 步骤5 | 键盘输入 | 3 秒 |
| 步骤6 | 截图 + OCR + 提取 | 3-5 秒 |
| **总计** | **完整流程** | **25-35 秒** |

---

## 🚧 已知限制

### **当前版本（v1.0）**

**✅ 已实现：**
- 打开文件
- 执行 BPLOT 命令
- OCR 识别按钮
- 点击按钮
- 键盘输入 all
- 提取图纸信息

**❌ 未实现：**
- 自动设置打印机/绘图仪
- 自动设置输出路径
- 自动点击"发布"按钮
- 批量处理多个文件

### **改进方向**

1. **完整自动化发布流程**
   - 继续 OCR 识别"发布"按钮
   - 自动配置输出设置
   - 监控发布进度

2. **错误处理增强**
   - 重试机制
   - 超时处理
   - 日志记录

3. **性能优化**
   - 并发处理
   - 缓存机制
   - 更快的 OCR

---

## 🔍 调试技巧

### **1. 查看截图**

所有截图保存在 `screenshots/bplot_auto/`，可直接打开查看 OCR 识别效果。

### **2. OCR 识别日志**

```python
# 在 step4 和 step6 中会打印 OCR 识别结果
print(f"  📄 识别到的文本:\n{all_text}\n")
```

### **3. 坐标验证**

```python
# 点击前先移动鼠标，观察位置是否正确
pyautogui.moveTo(x, y, duration=0.3)
time.sleep(2)  # 增加等待时间，观察鼠标位置
```

---

## 📚 相关文件

- **主实现：** `research/autocad_com_api/11_bplot_auto_workflow.py`
- **基础版：** `research/autocad_com_api/10_bplot_workflow.py` （仅执行 BPLOT）
- **标准工作流：** `research/autocad_com_api/9_configurable_workflow.py` （PDF 提取）

---

## 📞 技术支持

**依赖服务：**
- Umi-OCR: `http://10.3.19.121:1224/`
- 数据库: `10.3.19.189:3313`

**环境要求：**
- Windows 10+
- AutoCAD 2014+
- Python 3.8+
- Umi-OCR 服务运行中

---

**文档版本：** v1.0
**最后更新：** 2025-11-02
**作者：** CAD Auto Processor Team
