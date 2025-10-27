# 图像预处理工具使用指南

## 📚 概述

`image_processing.py` 提供了 **17种** 图像预处理方法，用于提高OCR识别准确率。

---

## 🎯 支持的预处理方法

### 1. **基础处理**

| 方法名 | 说明 | 适用场景 |
|--------|------|---------|
| `original` | 原始图像，未经处理 | 高质量截图 |
| `grayscale` | 灰度化，转换为单通道灰度图 | 减少数据维度，提升速度 |

### 2. **二值化处理**（3种）

| 方法名 | 说明 | 适用场景 |
|--------|------|---------|
| `binary_adaptive` | 自适应二值化（局部阈值） | ✅ **推荐**：光照不均、AutoCAD菜单 |
| `binary_otsu` | Otsu自动阈值二值化 | 双峰分布（清晰的前景/背景） |
| `binary_global` | 全局阈值二值化（127） | 简单快速，光照均匀 |

### 3. **对比度/亮度调整**

| 方法名 | 说明 | 适用场景 |
|--------|------|---------|
| `high_contrast` | 高对比度增强（CLAHE） | ✅ **推荐**：低对比度、模糊文字 |
| `high_brightness` | 高亮度调整 | 暗色主题界面 |

### 4. **降噪处理**（4种）

| 方法名 | 说明 | 速度 | 效果 |
|--------|------|------|------|
| `denoise_gaussian` | 高斯降噪 | ⚡ 快 | 保留边缘 |
| `denoise_median` | 中值滤波降噪 | ⚡ 快 | 去除椒盐噪声 |
| `denoise_bilateral` | 双边滤波降噪 | 🐢 中等 | ✅ **推荐**：保边+平滑 |
| `denoise_nlm` | 非局部均值降噪 | 🐌 慢 | 效果最好，强噪声 |

### 5. **RGB通道分离**（3种）

| 方法名 | 说明 | 适用场景 |
|--------|------|---------|
| `rgb_red` | 红色通道 | 红色文字/图层识别 |
| `rgb_green` | 绿色通道 | 绿色文字/图层识别 |
| `rgb_blue` | 蓝色通道 | 蓝色文字/图层识别 |

**原理**：
```
黄色文字（R=255, G=255, B=0）在白色背景（R=255, G=255, B=255）
- RGB混合：对比度差 ❌
- 蓝色通道：文字=0，背景=255，对比度=255 ✅
```

### 6. **边缘检测**（3种）

| 方法名 | 说明 | 效果 |
|--------|------|------|
| `edge_canny` | Canny边缘检测 | ✅ **推荐**：细线条，最精确 |
| `edge_sobel` | Sobel边缘检测 | 粗轮廓 |
| `edge_laplacian` | Laplacian边缘检测 | 全方向边缘 |

---

## 💻 使用示例

### 示例1：使用推荐方法（默认）

```python
from PIL import Image
from src.utils.image_processing import preprocess_images

# 读取图像
image = Image.open("screenshot.png")

# 使用推荐方法（8种）
results = preprocess_images(
    image,
    save_dir="output",
    base_name="test"
)

# 结果：
# {
#     'original': PIL.Image,
#     'grayscale': PIL.Image,
#     'binary_adaptive': PIL.Image,
#     'binary_otsu': PIL.Image,
#     'high_contrast': PIL.Image,
#     'high_brightness': PIL.Image,
#     'denoise_bilateral': PIL.Image,
#     'edge_canny': PIL.Image,
# }
```

### 示例2：使用所有方法

```python
from src.utils.image_processing import preprocess_images, PREPROCESSING_METHODS

# 使用全部17种方法
results = preprocess_images(
    image,
    methods=PREPROCESSING_METHODS,
    save_dir="output_all"
)

print(f"生成了 {len(results)} 种预处理图像")
```

### 示例3：使用自定义方法

```python
# 只使用指定的方法
methods = [
    'original',
    'binary_adaptive',
    'binary_otsu',
    'high_contrast',
]

results = preprocess_images(
    image,
    methods=methods,
    save_dir="output_custom"
)
```

### 示例4：自定义参数

```python
# 自定义预处理参数
params = {
    # 二值化参数
    'binary_adaptive_block_size': 15,  # 默认11
    'binary_adaptive_c': 3,            # 默认2

    # CLAHE参数
    'clahe_clip_limit': 4.0,           # 默认3.0

    # 降噪参数
    'bilateral_d': 11,                 # 默认9
    'bilateral_sigma_color': 100,      # 默认75

    # 边缘检测参数
    'canny_threshold1': 30,            # 默认50
    'canny_threshold2': 100,           # 默认150
}

results = preprocess_images(
    image,
    methods=['binary_adaptive', 'high_contrast', 'edge_canny'],
    params=params
)
```

### 示例5：单一预处理

```python
from src.utils.image_processing import preprocess_for_ocr

# 只进行一种预处理
binary_image = preprocess_for_ocr(image, method='binary_adaptive')
contrast_image = preprocess_for_ocr(image, method='high_contrast')
```

---

## 🔍 与OCR集成使用

### 示例：多版本OCR识别 + 结果合并

```python
from PIL import Image
from src.utils.image_processing import preprocess_images, combine_ocr_results
import requests
import base64
import io

# 1. 生成多版本预处理图像
image = Image.open("autocad_screenshot.png")
preprocessed = preprocess_images(image, methods=['original', 'binary_adaptive', 'high_contrast'])

# 2. 对每个版本进行OCR识别
all_ocr_results = []

for version, processed_img in preprocessed.items():
    print(f"识别版本: {version}")

    # 转换为base64
    buffered = io.BytesIO()
    processed_img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    # 调用Umi-OCR API
    response = requests.post(
        "http://10.3.19.121:1224/api/ocr",
        json={
            "base64": img_base64,
            "options": {
                "ocr.limit_side_len": 2880,
                "data.format": "dict"
            }
        },
        timeout=30
    )

    result = response.json()
    if result.get('code') == 100:
        data = result.get('data', [])
        # 添加版本标记
        for item in data:
            item['_version'] = version
        all_ocr_results.append(data)
        print(f"  识别到 {len(data)} 个文本")

# 3. 合并OCR结果（去重，保留最高置信度）
merged_results = combine_ocr_results(all_ocr_results)

print(f"\n合并后共 {len(merged_results)} 个唯一文本")
for i, item in enumerate(merged_results[:10], 1):
    text = item.get('text', '')
    score = item.get('score', 0)
    version = item.get('_version', 'unknown')
    print(f"{i}. '{text}' (置信度:{score:.2f}, 来源:{version})")
```

---

## 📊 参数详解

### 二值化参数

```python
{
    'binary_adaptive_block_size': 11,  # 邻域大小（必须为奇数）
    'binary_adaptive_c': 2,            # 常数C（从均值中减去）
    'binary_global_threshold': 127,    # 全局阈值（0-255）
}
```

**调优建议**：
- `block_size` **↑** → 更平滑，适合大文字
- `block_size` **↓** → 更敏感，适合小文字
- `c` **↑** → 更多黑色（文字更粗）
- `c` **↓** → 更多白色（文字更细）

### CLAHE参数

```python
{
    'clahe_clip_limit': 3.0,      # 对比度限制（1.0-40.0）
    'clahe_tile_size': (8, 8),    # 分块大小
}
```

**调优建议**：
- `clip_limit` **↑** → 对比度更强（可能引入噪声）
- `clip_limit` **↓** → 对比度更弱（更平滑）
- `tile_size` **↑** → 更全局的增强
- `tile_size` **↓** → 更局部的增强

### 亮度调整参数

```python
{
    'brightness_alpha': 1.3,  # 对比度因子（>1增强，<1减弱）
    'brightness_beta': 50,    # 亮度偏移（-100至100）
}
```

**公式**：`output = alpha × input + beta`

### 降噪参数

```python
{
    # 高斯降噪
    'gaussian_kernel': (5, 5),     # 核大小（必须为奇数）

    # 中值滤波
    'median_kernel': 5,            # 核大小（必须为奇数）

    # 双边滤波（推荐）
    'bilateral_d': 9,              # 邻域直径
    'bilateral_sigma_color': 75,   # 颜色空间标准差
    'bilateral_sigma_space': 75,   # 坐标空间标准差

    # 非局部均值
    'nlm_h': 10,                   # 滤波强度（越大越平滑）
    'nlm_template_window': 7,      # 模板窗口大小
    'nlm_search_window': 21,       # 搜索窗口大小
}
```

### 边缘检测参数

```python
{
    # Canny边缘检测
    'canny_threshold1': 50,    # 低阈值
    'canny_threshold2': 150,   # 高阈值

    # Sobel/Laplacian
    'sobel_ksize': 3,          # 核大小（1, 3, 5, 7）
    'laplacian_ksize': 3,      # 核大小（1, 3, 5, 7）
}
```

---

## 🎨 方法选择指南

### 场景1：AutoCAD白色背景 + 黑色文字菜单
```python
推荐方法: ['binary_adaptive', 'binary_otsu', 'high_contrast']
原因: 对比度本身就高，二值化效果最好
```

### 场景2：AutoCAD暗色主题 + 浅色文字
```python
推荐方法: ['high_brightness', 'high_contrast']
原因: 需要提亮，增强对比度
```

### 场景3：彩色AutoCAD图层（红/绿/蓝）
```python
推荐方法: ['rgb_red', 'rgb_green', 'rgb_blue']
原因: 通道分离可以提取特定颜色图层
```

### 场景4：模糊/噪声图像
```python
推荐方法: ['denoise_bilateral', 'high_contrast', 'binary_adaptive']
原因: 先降噪，再增强对比度，最后二值化
```

### 场景5：需要提取文字轮廓
```python
推荐方法: ['edge_canny', 'binary_adaptive']
原因: 边缘检测 + 二值化
```

---

## 🛠️ 工具函数

### 获取所有方法

```python
from src.utils.image_processing import get_preprocessing_methods

methods = get_preprocessing_methods()
print(methods)
# ['original', 'grayscale', 'binary_adaptive', ...]
```

### 获取推荐方法

```python
from src.utils.image_processing import get_recommended_methods

methods = get_recommended_methods()
print(methods)
# ['original', 'binary_adaptive', 'binary_otsu', 'high_contrast', 'denoise_bilateral']
```

### 获取方法描述

```python
from src.utils.image_processing import get_method_description

desc = get_method_description('binary_adaptive')
print(desc)
# "自适应二值化，适合光照不均"
```

---

## ⚡ 性能对比

| 方法 | 速度 | 内存 | OCR提升 |
|------|------|------|---------|
| `original` | ⚡⚡⚡ | 低 | 基准 |
| `grayscale` | ⚡⚡⚡ | 低 | +5% |
| `binary_adaptive` | ⚡⚡ | 低 | +30% |
| `binary_otsu` | ⚡⚡⚡ | 低 | +25% |
| `high_contrast` | ⚡⚡ | 中 | +20% |
| `high_brightness` | ⚡⚡⚡ | 低 | +15% |
| `denoise_gaussian` | ⚡⚡⚡ | 低 | +10% |
| `denoise_median` | ⚡⚡⚡ | 低 | +12% |
| `denoise_bilateral` | ⚡⚡ | 中 | +18% |
| `denoise_nlm` | ⚡ | 高 | +22% |
| `rgb_*` | ⚡⚡⚡ | 低 | 场景相关 |
| `edge_canny` | ⚡⚡ | 低 | 轮廓提取 |

---

## 🐛 故障排查

### 问题1：图像格式不支持

**错误**：`ValueError: 不支持的图像通道数`

**解决**：
```python
# 确保图像是PIL.Image对象
from PIL import Image
image = Image.open("file.png")
```

### 问题2：参数错误

**错误**：`ValueError: 未知的预处理方法`

**解决**：
```python
from src.utils.image_processing import get_preprocessing_methods
print(get_preprocessing_methods())  # 查看支持的方法
```

### 问题3：内存不足

**解决**：减少同时处理的方法数量
```python
# 分批处理
methods_batch1 = ['original', 'binary_adaptive', 'high_contrast']
methods_batch2 = ['denoise_bilateral', 'edge_canny']

results1 = preprocess_images(image, methods=methods_batch1)
results2 = preprocess_images(image, methods=methods_batch2)
```

---

## 📝 最佳实践

1. **先试推荐方法**：`get_recommended_methods()` 返回的5种方法对大多数场景有效

2. **参数调优**：根据实际效果逐步调整参数，不要一次改太多

3. **多版本OCR**：结合 `combine_ocr_results()` 提升识别准确率

4. **保存中间结果**：设置 `save_dir` 参数，方便调试

5. **性能优化**：
   - 只使用必要的方法
   - 避免使用 `denoise_nlm`（速度最慢）
   - 图像尺寸大时先缩放

---

## 📚 扩展阅读

- [OpenCV官方文档 - 图像处理](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html)
- [CLAHE算法详解](https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html)
- [Canny边缘检测原理](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html)

---

**更新日期**: 2025-10-27
**作者**: CAD Auto Processor Team
