# PDF文字提取 - 快速开始指南

## 🚀 5分钟快速开始

### 测试单个PDF（验证可行性）

```bash
cd /Users/saul/IdeaProjects/100.AI.TrainData

# 测试单个文件
python3 scripts/pdf_to_images_ocr.py \
    "data/pdf/PCX20.01%20主体钢结构（20230301）0001.pdf" \
    /tmp/test_result.txt

# 查看结果
cat /tmp/test_result.txt
```

**预期结果：**
- ✅ 看到完整的技术要求、图号、公司名称等
- ✅ 约600+字符
- ✅ 处理时间 ~5秒

---

### 批量处理所有PDF（15分钟）

```bash
cd /Users/saul/IdeaProjects/100.AI.TrainData

# 运行批量处理脚本
./scripts/batch_pdf_ocr.sh
```

**输出位置：**
- `data/pdf_ocr_text/*.txt` - 183个文本文件
- `data/pdf_ocr_text/summary.txt` - 处理摘要报告

**预计时间：** 15分钟（183个PDF × 5秒）

---

## 📋 完整文档

### 问题诊断
- **docs/PDF_EXTRACTION_FINAL_REPORT.md** - 完整诊断报告

### 解决方案
- **docs/PDF_TEXT_EXTRACTION_SOLUTIONS.md** - 两种方案对比
- **docs/PDF_OCR_Analysis.md** - 技术分析

### AutoCAD配置（长期优化）
- **docs/AutoCAD_PDF_Settings_Correct_Guide.md** - 详细配置步骤
- **docs/AutoCAD_PDF_Settings_Visual_Guide.txt** - 可视化说明

---

## 🔧 工具说明

### 单文件处理
```bash
python3 scripts/pdf_to_images_ocr.py <PDF文件> [输出TXT] [DPI]
```

**示例：**
```bash
# 默认DPI 300
python3 scripts/pdf_to_images_ocr.py input.pdf output.txt

# 高精度DPI 600
python3 scripts/pdf_to_images_ocr.py input.pdf output.txt 600
```

### 批量处理
```bash
./scripts/batch_pdf_ocr.sh
```

**配置修改：**
编辑 `scripts/batch_pdf_ocr.sh` 文件头部：
```bash
PDF_DIR="..."      # PDF源目录
OUTPUT_DIR="..."   # 输出目录
DPI=300           # 分辨率
```

### PDF质量验证
```bash
/tmp/verify_pdf_text.sh <PDF文件>
```

**用途：** 验证AutoCAD设置修改后的PDF是否正确

---

## ⚠️ 注意事项

### 依赖检查

**必需：poppler-utils**
```bash
# macOS安装
brew install poppler

# Ubuntu安装
sudo apt install poppler-utils

# 验证安装
pdftoppm -v
```

### Umi-OCR服务

**地址：** `http://10.3.19.63:11224`

**验证可用：**
```bash
curl -s http://10.3.19.63:11224/api/ocr/get_options | head -20
```

---

## 🎯 两种方案选择

### 方案A：OCR方案（立即可用）
- ✅ **优点：** 无需等待，15分钟获得所有文本
- ⏱️ **速度：** 5秒/页
- 🎯 **准确度：** 95%+
- 📦 **工具：** `batch_pdf_ocr.sh`

### 方案B：修改AutoCAD（长期最佳）
- ✅ **优点：** 100%准确，文件更小，可搜索
- ⏱️ **速度：** <0.1秒/页（提取）
- 🎯 **准确度：** 100%
- 📚 **文档：** `AutoCAD_PDF_Settings_Correct_Guide.md`

### 推荐策略：两者结合
1. **现在：** 运行OCR方案，立即获得数据
2. **本周：** 修改AutoCAD配置，重新生成PDF
3. **未来：** 使用高质量PDF，无需OCR

---

## 📞 快速帮助

### 常见问题

**Q1: 脚本报错 "pdftoppm: command not found"**
```bash
# 安装 poppler
brew install poppler  # macOS
```

**Q2: Umi-OCR连接失败**
```bash
# 检查服务状态
curl http://10.3.19.63:11224/api/ocr/get_options
```

**Q3: 批量处理中断了怎么办？**
- ✅ 再次运行脚本会自动跳过已处理文件
- ✅ 检查 `data/pdf_ocr_text/` 目录已有结果

**Q4: 想提高识别准确度**
```bash
# 修改脚本中的DPI为600
# 编辑 batch_pdf_ocr.sh
DPI=600  # 原来是300
```

---

## 📊 预期效果

### OCR方案输出示例

**文件名：** `PCX20.01 主体钢结构（20230301）0001.txt`

**内容示例：**
```
# 第 1 页

技术要求：
1，表面处理：喷漆前除锈要除干净，金属表面呈现金属光泽...
2.未注公差长度方向按士2mm,对角线方向士3mm...
3.未注明焊高均为板厚的80%，皆为满焊；焊后校平...

图号：PCX20-01-01-D1
公司：深圳市奇见科技有限公司
设备：PCX型11层垂直循环类机械式停车设备
材料：Q235B
...
```

### 批量处理摘要示例

**文件：** `data/pdf_ocr_text/summary.txt`

```
批量PDF OCR处理报告
==========================================

处理时间: 2025-10-31 01:45:00
PDF源目录: /Users/saul/.../data/pdf
输出目录: /Users/saul/.../data/pdf_ocr_text

处理结果:
- 成功: 183
- 失败: 0
- 跳过: 0
- 总计: 183

耗时: 15分23秒
平均速度: 0.20 文件/秒

输出文件: 183 个TXT文件
总大小: 2.3M
==========================================
```

---

## ✅ 成功检查清单

运行完成后检查：

- [ ] `data/pdf_ocr_text/` 目录包含183个TXT文件
- [ ] 随机抽查5个文件，内容完整
- [ ] `summary.txt` 显示全部成功
- [ ] 没有报错信息

---

**最后更新：** 2025-10-31
**版本：** 1.0
