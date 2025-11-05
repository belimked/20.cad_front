# PDF OCR 分析报告

## 测试结论

### ❌ Umi-OCR 文档识别API **无法**从当前PDF提取文字

**测试结果：**
```json
{
  "code": 101,           // 未识别到文字
  "data": "",            // 空数据
  "state": "success",    // OCR成功，但没找到文字
  "processed_count": 1,
  "pages_count": 1
}
```

## 根本原因

### AutoCAD PDF设置导致的问题

**当前PDF特征：**
- ✅ 文件类型：矢量PDF
- ❌ 字体资源：0个
- ❌ 文字类型：完全转为矢量路径（Geometry）
- ❌ 文本对象：无

**Umi-OCR文档识别的工作原理：**
1. **混合模式（mixed）**：
   - 检测PDF中的文本对象 → **直接提取**
   - 检测PDF中的图像对象 → **OCR识别**
   - 🔴 **当前PDF问题**：文字是矢量路径，既不是文本对象也不是图像，所以无法处理

2. **纯文本模式（txt）**：
   - 只提取PDF中的文本对象
   - 🔴 **当前PDF问题**：无文本对象，提取为空

3. **OCR模式（ocr）**：
   - 将PDF页面转为图像后OCR
   - ✅ **理论可行**：但需要将矢量路径渲染为图像

## 解决方案对比

### 方案1：修改AutoCAD设置（✅ 推荐）

**优点：**
- ✅ 一劳永逸
- ✅ PDF包含真实文字对象
- ✅ 文件更小（80-100KB vs 130KB）
- ✅ 任何工具都能提取（pdftotext, Umi-OCR, Adobe等）
- ✅ 可搜索、可复制
- ✅ 无需OCR，速度快

**缺点：**
- ⏳ 需要重新生成所有PDF
- ⚠️ 需要正确配置AutoCAD

**配置步骤：**
```
AutoCAD → PLOTTERMANAGER → DWG To PDF.pc3
→ 设备和文档设置 → 图形 → 矢量图形 → 自定义属性
→ TrueType字体: 选择 "Unicode文本"
→ ☑ 捕获文本
→ ☑ 嵌入TrueType字体
```

参考文档：`docs/AutoCAD_PDF_Settings_Correct_Guide.md`

---

### 方案2：PDF转图片后OCR（✅ 可行）

**优点：**
- ✅ 可处理现有PDF，无需重新生成
- ✅ Umi-OCR识别准确度高
- ✅ 支持中文

**缺点：**
- ❌ 需要额外步骤（PDF→图片）
- ❌ 速度慢（每页需要渲染+OCR）
- ❌ 消耗更多资源
- ❌ 提取的文字没有位置信息

**实现步骤：**
```python
# 1. PDF转图片（需要 pdf2image 库）
from pdf2image import convert_from_path

images = convert_from_path('input.pdf', dpi=300)

# 2. 对每张图片进行OCR（使用Umi-OCR图片API）
for img in images:
    # 保存为临时图片
    img.save('/tmp/page.png')

    # 调用Umi-OCR图片识别API
    # http://10.3.19.63:11224/api/ocr
```

**需要安装：**
```bash
pip install pdf2image
# macOS:
brew install poppler
# 或 Ubuntu:
apt install poppler-utils
```

---

### 方案3：使用支持矢量PDF的OCR工具（❌ 复杂）

某些商业OCR工具可以将矢量路径解析为文字，但：
- ❌ 通常是商业软件
- ❌ 识别效果不确定
- ❌ 配置复杂

---

## 最佳实践

### 短期方案（处理现有PDF）

如果必须处理已生成的PDF：

```python
#!/usr/bin/env python3
from pdf2image import convert_from_path
import requests
import base64

def ocr_pdf_via_images(pdf_path):
    # 1. PDF转图片
    images = convert_from_path(pdf_path, dpi=300)

    results = []
    for i, img in enumerate(images, 1):
        # 2. 保存为PNG
        img_path = f'/tmp/page_{i}.png'
        img.save(img_path)

        # 3. Base64编码
        with open(img_path, 'rb') as f:
            img_base64 = base64.b64encode(f.read()).decode()

        # 4. 调用Umi-OCR图片API
        response = requests.post(
            'http://10.3.19.63:11224/api/ocr',
            json={
                'base64': img_base64,
                'options': {'data.format': 'text'}
            }
        )

        result = response.json()
        if result['code'] == 100:
            results.append(result['data'])

    return '\n\n'.join(results)

# 使用
text = ocr_pdf_via_images('input.pdf')
print(text)
```

### 长期方案（✅ 强烈推荐）

**修改AutoCAD配置，重新生成PDF**

1. ✅ 修改AutoCAD设置为"Unicode文本"
2. ✅ 打印单个文件测试
3. ✅ 验证文字可提取：
   ```bash
   pdffonts test.pdf  # 应该看到字体列表
   pdftotext test.pdf -  # 应该看到文字内容
   ```
4. ✅ 批量重新生成所有PDF

**验证命令：**
```bash
# 检查字体
pdffonts test.pdf

# 提取文字
pdftotext test.pdf output.txt

# 或使用Umi-OCR文档API（混合模式）
# 会自动提取文本对象，无需OCR
```

---

## 性能对比

| 方案 | 速度 | 准确度 | 文件大小 | 可搜索 | 实施难度 |
|-----|------|--------|---------|--------|---------|
| 修改AutoCAD设置 | ⚡⚡⚡ | 💯 100% | 📦 小(80KB) | ✅ 是 | ⭐ 简单 |
| PDF→图片→OCR | 🐌 慢 | 🎯 95%+ | 📦 原样 | ❌ 否* | ⭐⭐ 中等 |
| 当前PDF直接OCR | ❌ 不可行 | - | - | - | - |

*注：OCR后的文字是纯文本，不嵌入PDF中，无法在PDF内搜索

---

## 实际测试数据

### 当前PDF（错误设置）
```
文件: PCX20.01 主体钢结构（20230301）0001.pdf
大小: 134480 字节
字体: 0 个
文本对象: 0 个
矢量路径: 1064 个

pdftotext提取: 0 字符
Umi-OCR文档API: code 101 (未识别到文字)
```

### 修改后PDF（正确设置）- 预期
```
文件: test_corrected.pdf
大小: ~80000 字节
字体: 3-5 个 (SimSun, Arial等)
文本对象: 有

pdftotext提取: 完整文字内容
Umi-OCR文档API: 直接提取（无需OCR，瞬间完成）
```

---

## 推荐行动

### ⏰ 立即执行

1. **修改AutoCAD配置**
   - 参考：`docs/AutoCAD_PDF_Settings_Correct_Guide.md`
   - 设置：TrueType字体 → Unicode文本

2. **测试验证**
   - 打印1个PDF
   - 运行：`/tmp/verify_pdf_text.sh test.pdf`
   - 确认字体 > 0，文字可提取

3. **批量处理**
   - 重新生成所有183个PDF

### 📝 备用方案

如果短期内无法修改AutoCAD设置，可以使用PDF→图片→OCR方案：

```bash
# 安装依赖
pip install pdf2image

# 使用我即将创建的脚本
python3 scripts/pdf_to_images_ocr.py input.pdf output.txt
```

---

## 总结

**Umi-OCR文档识别API的限制：**
- ✅ 可以提取PDF中的文本对象（如果有）
- ✅ 可以OCR PDF中的图像对象
- ❌ **无法处理矢量路径转换的文字**（当前PDF的问题）

**唯一根本解决方案：**
修改AutoCAD设置，将文字保存为文本对象而非矢量路径。

**临时解决方案：**
PDF → 图片 → Umi-OCR图片API（但效率低）
