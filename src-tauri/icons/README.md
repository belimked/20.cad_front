# 应用图标

## 当前状态
图标目录已创建,等待图标文件。

## 源文件
- `../icon-source.svg` - SVG源图标

## 生成方法

### 推荐: 使用 icon.kitchen
1. 访问 https://icon.kitchen/
2. 上传 icon-source.svg
3. 选择平台: Tauri
4. 下载并解压到此目录

### 手动: 使用 Tauri CLI
```bash
# 1. 转换SVG为1024x1024的PNG
# 使用在线工具: https://cloudconvert.com/svg-to-png

# 2. 生成图标
npm run tauri icon ./app-icon.png
```

## 图标设计说明
当前图标设计:
- 左侧: DWG文件图标 (蓝色)
- 中间: 转换箭头 (绿色)
- 右侧: PDF文件图标 (红色)
- 背景: 蓝色渐变

清晰传达 "DWG → PDF" 转换功能。
