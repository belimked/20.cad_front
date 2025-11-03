# Tesseract OCR 安装指南

## 🎯 为什么选择Tesseract？

经过测试，**Tesseract对中文UI小字体的识别效果最好**！

对比其他方案：
- **EasyOCR**: 识别质量差，中文字符经常错误（'视罔()'而不是'视图()'）
- **PaddleOCR**: 质量最好但需要500MB+的paddlepaddle框架
- **Tesseract**: ⭐⭐⭐⭐⭐ 轻量、快速、中文识别准确

---

## 📦 安装步骤

### 步骤1：安装Python库

```bash
# 激活虚拟环境
venv\Scripts\activate

# 安装pytesseract
pip install pytesseract
```

### 步骤2：下载并安装Tesseract引擎

#### Windows系统

**下载地址**:
https://github.com/UB-Mannheim/tesseract/wiki

**推荐版本**:
`tesseract-ocr-w64-setup-5.3.3.20231005.exe` (或更新版本)

**安装步骤**:

1. 双击安装程序
2. **重要**：选择安装组件时，勾选：
   - ✅ **Chinese (Simplified) - chi_sim** (简体中文)
   - ✅ **Chinese (Traditional) - chi_tra** (可选，繁体中文)
   - ✅ **English - eng** (英文，默认已选)

   ![安装界面示例](https://user-images.githubusercontent.com/example/tesseract-install.png)

3. 选择安装路径（默认：`C:\Program Files\Tesseract-OCR\`）
4. 完成安装

### 步骤3：配置环境变量（推荐）

**方式一：添加到系统PATH**（推荐）

1. 右键"此电脑" → "属性" → "高级系统设置"
2. 点击"环境变量"
3. 在"系统变量"中找到"Path"，点击"编辑"
4. 点击"新建"，添加Tesseract安装路径：
   ```
   C:\Program Files\Tesseract-OCR
   ```
5. 确定保存

**方式二：在Python代码中指定**（备选）

如果不想修改系统PATH，可以在代码中指定：
```python
import pytesseract

# 设置Tesseract路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 步骤4：验证安装

打开命令提示符（CMD），输入：

```bash
tesseract --version
```

**预期输出**：
```
tesseract 5.3.3
 leptonica-1.84.1
  libgif 5.2.1 : libjpeg 8d (libjpeg-turbo 3.0.1) : libpng 1.6.40 : libtiff 4.6.0 : zlib 1.3 : libwebp 1.3.2 : libopenjp2 2.5.0
 Found AVX2
 Found AVX
 Found FMA
 Found SSE4.1
 Found OpenMP 201107
 Found libarchive 3.7.2 zlib/1.3 liblzma/5.4.5 bz2/1.0.8 libzstd/1.5.5
 Found libcurl/8.4.0 (Schannel) zlib/1.3 zstd/1.5.5 libidn2/2.3.4 libpsl/0.21.2 (+libidn2/2.3.4) libssh2/1.11.0 nghttp2/1.58.0 libgsasl/2.2.0
```

检查中文语言包：
```bash
tesseract --list-langs
```

**预期输出**（应包含）：
```
List of available languages in "C:\Program Files\Tesseract-OCR\tessdata/" (3):
chi_sim
chi_tra
eng
```

---

## 🧪 快速测试

### 测试1：验证Tesseract可用

```bash
venv\Scripts\activate
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

**预期输出**: `5.3.3` (或你安装的版本号)

### 测试2：测试AutoCAD菜单识别

```bash
# 确保AutoCAD已运行并打开了DWG文件
python scripts\test_tesseract_ocr.py
```

**输入**: `依云` (或其他菜单文字)

**预期输出**:
```
✅ 识别到 156 个文本区域

【调试】所有识别到的文字 (前30个):
================================================================================
  1. 'AutoCAD' (置信度:96%)
  2. '经典' (置信度:91%)
  3. 'Autodesk' (置信度:93%)
  4. 'AutoCAD' (置信度:95%)
  5. '2014' (置信度:88%)
  6. 'PCX20.01' (置信度:90%)
  7. '主体钢结构' (置信度:87%)
  8. '文件' (置信度:92%)
  9. '编辑' (置信度:94%)
  10. '视图' (置信度:93%)
  ...
  25. '依云' (置信度:89%)    # 找到了！
================================================================================

✅ 找到匹配文本: '依云' (置信度:89%)
   窗口内位置: (856, 234)
   屏幕位置: (1856, 334)

是否点击该位置? (y/n，默认n): y
✅ 已点击
```

---

## 🚀 集成到工作流程

Tesseract已经作为首选OCR方案集成到工作流程中。

### 使用方式

1. **添加OCR菜单操作**：
```bash
python scripts\add_menu_operations.py 1
# 选择 [3] OCR文字识别
# 输入: 依云
```

2. **运行工作流程**：
```bash
python research\autocad_com_api\configurable_workflow.py
```

**系统会自动**：
- 优先尝试Tesseract OCR（识别质量最好）
- 如果Tesseract不可用，回退到EasyOCR
- 如果EasyOCR也不可用，回退到PaddleOCR

---

## 🔧 故障排查

### 问题1：`TesseractNotFoundError`

**现象**：
```
pytesseract.pytesseract.TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**解决**：
1. 确认Tesseract已安装
2. 检查安装路径是否正确（默认：`C:\Program Files\Tesseract-OCR\`）
3. 检查PATH环境变量
4. 或在代码中指定路径（见上文"配置环境变量"）

### 问题2：未找到中文语言包

**现象**：
```
Error opening data file \Program Files\Tesseract-OCR\tessdata/chi_sim.traineddata
```

**解决**：
1. 重新运行Tesseract安装程序
2. 在安装组件中勾选 **Chinese (Simplified) - chi_sim**
3. 或手动下载语言包：
   - 下载地址: https://github.com/tesseract-ocr/tessdata/blob/main/chi_sim.traineddata
   - 放到: `C:\Program Files\Tesseract-OCR\tessdata\`

### 问题3：识别效果不佳

**优化建议**：

1. **提高图像质量**：
```python
# 增强对比度
import cv2
gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
enhanced = cv2.equalizeHist(gray)
```

2. **调整PSM模式**：
```python
# PSM 3: 全页自动分割（默认）
# PSM 6: 单行文本
# PSM 11: 稀疏文本
data = pytesseract.image_to_data(gray, lang='chi_sim+eng',
                                  config='--psm 3',
                                  output_type=pytesseract.Output.DICT)
```

3. **二值化处理**：
```python
# 自适应阈值二值化
binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 11, 2)
```

---

## 📊 性能对比

基于AutoCAD 2014界面测试：

| OCR方案 | 安装难度 | 识别准确度 | 速度 | 内存占用 | 推荐度 |
|---------|---------|-----------|------|---------|--------|
| **Tesseract** | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 极高 | ⭐⭐⭐⭐ 快 | ~100MB | ⭐⭐⭐⭐⭐ |
| EasyOCR | ⭐ 简单 | ⭐⭐ 差 | ⭐⭐⭐ 中等 | ~200MB | ⭐⭐ |
| PaddleOCR | ⭐⭐⭐⭐ 复杂 | ⭐⭐⭐⭐⭐ 极高 | ⭐⭐⭐⭐⭐ 很快 | ~600MB | ⭐⭐⭐ |

**测试结果**（识别"依云"菜单）：
- **Tesseract**: ✅ 成功识别，置信度89%
- **EasyOCR**: ❌ 未识别到，识别为其他字符
- **PaddleOCR**: ✅ 成功识别，置信度94%（但需要大量依赖）

---

## 💡 推荐配置

**桌面开发环境**（推荐Tesseract）：
```bash
pip install pytesseract
# 安装Tesseract引擎 + chi_sim语言包
```

**服务器/CI环境**（推荐Docker）：
```dockerfile
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    python3-pip
RUN pip3 install pytesseract
```

**轻量级环境**（无法安装Tesseract）：
```bash
pip install easyocr  # 备选方案
```

---

## 📚 参考资源

- **Tesseract官方文档**: https://tesseract-ocr.github.io/
- **Windows安装包**: https://github.com/UB-Mannheim/tesseract/wiki
- **语言包下载**: https://github.com/tesseract-ocr/tessdata
- **pytesseract文档**: https://pypi.org/project/pytesseract/

---

## 🎉 总结

使用Tesseract OCR的优势：

1. ✅ **识别准确**: 中文UI小字体识别准确率高达90%+
2. ✅ **轻量快速**: 安装包~50MB，运行内存~100MB
3. ✅ **免费开源**: Google维护，社区活跃
4. ✅ **易于集成**: 已集成到工作流程，自动fallback
5. ✅ **跨平台**: Windows/Linux/Mac都支持

**3步开始使用**：
```bash
# 1. 安装pytesseract
pip install pytesseract

# 2. 安装Tesseract引擎（记得选中文语言包）
# 下载: https://github.com/UB-Mannheim/tesseract/wiki

# 3. 测试
python scripts\test_tesseract_ocr.py
```

就这么简单！Tesseract会自动成为你的OCR首选方案！🚀
