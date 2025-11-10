import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// 创建icons目录
const iconsDir = path.join(__dirname, 'src-tauri', 'icons');
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

console.log('✅ 图标目录已创建:', iconsDir);
console.log('\n📱 现在需要生成图标文件\n');
console.log('━'.repeat(60));
console.log('\n方法1: 使用在线工具 (最简单,推荐) 🌟\n');
console.log('1. 访问: https://icon.kitchen/');
console.log('2. 上传 icon-source.svg');
console.log('3. 选择 "Tauri" 平台');
console.log('4. 下载生成的图标包');
console.log('5. 解压到 src-tauri/icons/ 目录\n');
console.log('━'.repeat(60));
console.log('\n方法2: 手动转换 + Tauri CLI\n');
console.log('1. 转换SVG为PNG:');
console.log('   访问: https://cloudconvert.com/svg-to-png');
console.log('   上传: icon-source.svg');
console.log('   设置尺寸: 1024x1024');
console.log('   下载为: app-icon.png\n');
console.log('2. 安装Tauri CLI:');
console.log('   npm install --save-dev @tauri-apps/cli@1.5\n');
console.log('3. 生成图标:');
console.log('   npm run tauri icon ./app-icon.png\n');
console.log('━'.repeat(60));
console.log('\n📝 需要的图标文件:\n');
console.log('  - 32x32.png');
console.log('  - 128x128.png');
console.log('  - 128x128@2x.png');
console.log('  - icon.icns (macOS)');
console.log('  - icon.ico (Windows)\n');

// 创建README
const readmeContent = `# 应用图标

## 当前状态
图标目录已创建,等待图标文件。

## 源文件
- \`../icon-source.svg\` - SVG源图标

## 生成方法

### 推荐: 使用 icon.kitchen
1. 访问 https://icon.kitchen/
2. 上传 icon-source.svg
3. 选择平台: Tauri
4. 下载并解压到此目录

### 手动: 使用 Tauri CLI
\`\`\`bash
# 1. 转换SVG为1024x1024的PNG
# 使用在线工具: https://cloudconvert.com/svg-to-png

# 2. 生成图标
npm run tauri icon ./app-icon.png
\`\`\`

## 图标设计说明
当前图标设计:
- 左侧: DWG文件图标 (蓝色)
- 中间: 转换箭头 (绿色)
- 右侧: PDF文件图标 (红色)
- 背景: 蓝色渐变

清晰传达 "DWG → PDF" 转换功能。
`;

fs.writeFileSync(path.join(iconsDir, 'README.md'), readmeContent);

console.log('✅ 已创建图标目录说明文件\n');
