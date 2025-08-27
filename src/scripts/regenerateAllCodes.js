/**
 * 重新生成所有编号信息的脚本
 * 使用新的权重规则：英文字母数字权重大，汉字次之，特殊符号权重小
 */

const fs = require('fs');
const path = require('path');
const CodeGenerator = require('../utils/codeGenerator');

class CodeRegenerator {
  constructor() {
    this.generator = new CodeGenerator();
    this.dictPath = path.join(__dirname, '../dict');
  }

  /**
   * 确保目录存在
   */
  ensureDirectoryExists() {
    if (!fs.existsSync(this.dictPath)) {
      fs.mkdirSync(this.dictPath, { recursive: true });
    }
  }

  /**
   * 保存JSON文件
   */
  saveJsonFile(filename, data) {
    const filePath = path.join(this.dictPath, filename);
    const jsonString = JSON.stringify(data, null, 2);
    fs.writeFileSync(filePath, jsonString, 'utf8');
    console.log(`✅ 已生成: ${filename} (${data.length} 条记录)`);
  }

  /**
   * 重新生成材料编码字典
   */
  regenerateMaterialCodes() {
    console.log('🔄 正在生成材料编码字典...');

    // 基础材料编码 (200条，长度5-6)
    const basicCodes = this.generator.generateMaterialCodeDict(200, 6);
    this.saveJsonFile('material_code_dict.json', basicCodes);

    // 扩展材料编码 (700条，长度8-10)
    const extendedCodes = this.generator.generateMaterialCodeDict(700, 9);
    this.saveJsonFile('material_code_extended_dict.json', extendedCodes);
  }

  /**
   * 重新生成业务编号
   */
  regenerateBusinessNumbers() {
    console.log('🔄 正在生成业务编号...');
    const businessNumbers = this.generator.generateBusinessNumberDict(400, 7);
    this.saveJsonFile('businessNumbers.json', businessNumbers);
  }

  /**
   * 重新生成包装编号
   */
  regeneratePackageNumbers() {
    console.log('🔄 正在生成包装编号...');
    
    // 基础包装编号
    const packageNumbers = this.generator.generatePackageNumberDict(200, 8);
    this.saveJsonFile('packageNumbers.json', packageNumbers);
    
    // 扩展包装编号
    const packageNumbersExt = this.generator.generatePackageNumberDict(300, 10);
    this.saveJsonFile('packageNumbers_ext.json', packageNumbersExt);
  }

  /**
   * 重新生成员工编号
   */
  regenerateStaffNumbers() {
    console.log('🔄 正在生成员工编号...');
    const staffNumbers = this.generator.generateStaffNumberDict(150, 6);
    this.saveJsonFile('staffNumbers.json', staffNumbers);
  }

  /**
   * 重新生成图纸编号
   */
  regenerateDrawings() {
    console.log('🔄 正在生成图纸编号...');
    const drawings = this.generator.generateDrawingDict(600);
    this.saveJsonFile('drawings.json', drawings);
  }

  /**
   * 生成示例编号展示
   */
  generateSamples() {
    console.log('\n📋 编号样例展示:');
    console.log('==================');
    
    console.log('\n🏷️  材料编码样例 (长度6):');
    for (let i = 0; i < 10; i++) {
      console.log(`   ${this.generator.generateSingleCode(6)}`);
    }
    
    console.log('\n🏢 业务编号样例 (长度7):');
    for (let i = 0; i < 10; i++) {
      console.log(`   ${this.generator.generateSingleCode(7)}`);
    }
    
    console.log('\n📦 包装编号样例 (长度8):');
    for (let i = 0; i < 10; i++) {
      console.log(`   ${this.generator.generateSingleCode(8)}`);
    }
    
    console.log('\n👥 员工编号样例 (长度6):');
    for (let i = 0; i < 10; i++) {
      console.log(`   ${this.generator.generateSingleCode(6)}`);
    }
    
    console.log('\n🔢 长编号样例 (长度10):');
    for (let i = 0; i < 5; i++) {
      console.log(`   ${this.generator.generateSingleCode(10)}`);
    }

    console.log('\n📐 图纸编号样例:');
    const drawingSamples = this.generator.generateDrawingCodes(10);
    for (let i = 0; i < drawingSamples.length; i++) {
      console.log(`   ${drawingSamples[i]}`);
    }
  }

  /**
   * 执行完整的重新生成流程
   */
  async regenerateAll() {
    console.log('🚀 开始重新生成所有编号信息...');
    console.log('📋 编号规则:');
    console.log('   - 英文字母和数字权重: 70%');
    console.log('   - 汉字权重: 25%');
    console.log('   - 特殊符号权重: 5% (包含: - $ # ( ))');
    console.log('   - 最小长度: 5位');
    console.log('');

    this.ensureDirectoryExists();
    
    try {
      this.regenerateMaterialCodes();
      this.regenerateBusinessNumbers();
      this.regeneratePackageNumbers();
      this.regenerateStaffNumbers();
      this.regenerateDrawings();

      console.log('\n✨ 所有编号文件重新生成完成!');

      this.generateSamples();
      
    } catch (error) {
      console.error('❌ 生成过程中出现错误:', error.message);
      throw error;
    }
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  const regenerator = new CodeRegenerator();
  regenerator.regenerateAll()
    .then(() => {
      console.log('\n🎉 编号重新生成任务完成!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('💥 任务失败:', error);
      process.exit(1);
    });
}

module.exports = CodeRegenerator;
