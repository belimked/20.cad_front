#!/usr/bin/env node

console.log('\n🎨 图标生成指南\n');
console.log('━'.repeat(60));
console.log('\n由于没有图像转换工具,请使用以下在线服务:\n');

console.log('📍 方法1: CloudConvert (推荐)\n');
console.log('1. 访问: https://cloudconvert.com/svg-to-png');
console.log('2. 点击 "Select File" 按钮 (大蓝色按钮)');
console.log('3. 选择 app-icon.svg 文件');
console.log('4. 点击右边的 "⚙️ Settings" (设置)');
console.log('5. 设置 Width: 1024, Height: 1024');
console.log('6. 点击 "Convert" 按钮');
console.log('7. 下载生成的 PNG 文件,保存为 app-icon.png');
console.log('8. 运行: npm run tauri icon ./app-icon.png\n');

console.log('━'.repeat(60));
console.log('\n📍 方法2: Convertio\n');
console.log('1. 访问: https://convertio.co/svg-png/');
console.log('2. 点击红色 "Choose Files" 按钮');
console.log('3. 选择 app-icon.svg');
console.log('4. 点击 "Convert" 按钮');
console.log('5. 下载PNG文件,保存为 app-icon.png');
console.log('6. 运行: npm run tauri icon ./app-icon.png\n');

console.log('━'.repeat(60));
console.log('\n📍 方法3: 在线SVG编辑器\n');
console.log('1. 访问: https://www.photopea.com/');
console.log('2. File → Open → 选择 app-icon.svg');
console.log('3. Image → Image Size → 设置 1024x1024');
console.log('4. File → Export as → PNG');
console.log('5. 保存为 app-icon.png');
console.log('6. 运行: npm run tauri icon ./app-icon.png\n');

console.log('━'.repeat(60));
console.log('\n✅ Tauri CLI 已安装,等待PNG文件...\n');

