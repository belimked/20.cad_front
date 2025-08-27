/**
 * 编号生成器 - 根据权重规则生成新的编号
 * 规则：
 * - 英文字母和数字权重大
 * - 汉字权重次之  
 * - 特殊符号权重小 [-$#()]
 * - 长度至少5位
 */

class CodeGenerator {
  constructor() {
    // 英文字母和数字 (权重大)
    this.alphaNumeric = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    
    // 汉字库 (权重次之)
    this.chineseChars = [
      '材', '料', '设', '备', '工', '程', '项', '目', '管', '理',
      '生', '产', '制', '造', '质', '量', '检', '测', '安', '全',
      '技', '术', '开', '发', '维', '护', '运', '营', '服', '务',
      '电', '力', '网', '络', '系', '统', '控', '制', '监', '测',
      '配', '送', '仓', '储', '物', '流', '采', '购', '销', '售'
    ];
    
    // 特殊符号 (权重小)
    this.specialChars = '-$#()';
    
    // 权重配置
    this.weights = {
      alphaNumeric: 0.7,  // 70%
      chinese: 0.25,      // 25%
      special: 0.05       // 5%
    };
  }

  /**
   * 根据权重随机选择字符类型
   */
  getRandomCharType() {
    const rand = Math.random();
    if (rand < this.weights.alphaNumeric) {
      return 'alphaNumeric';
    } else if (rand < this.weights.alphaNumeric + this.weights.chinese) {
      return 'chinese';
    } else {
      return 'special';
    }
  }

  /**
   * 从指定类型中获取随机字符
   */
  getRandomChar(type) {
    switch (type) {
      case 'alphaNumeric':
        return this.alphaNumeric[Math.floor(Math.random() * this.alphaNumeric.length)];
      case 'chinese':
        return this.chineseChars[Math.floor(Math.random() * this.chineseChars.length)];
      case 'special':
        return this.specialChars[Math.floor(Math.random() * this.specialChars.length)];
      default:
        return this.alphaNumeric[Math.floor(Math.random() * this.alphaNumeric.length)];
    }
  }

  /**
   * 生成单个编号
   * @param {number} length - 编号长度 (最小5)
   * @returns {string} 生成的编号
   */
  generateSingleCode(length = 8) {
    const minLength = Math.max(5, length);
    let code = '';
    
    // 确保至少有一些英文字母或数字
    const minAlphaNumeric = Math.ceil(minLength * 0.6);
    let alphaNumericCount = 0;
    
    for (let i = 0; i < minLength; i++) {
      let charType;
      
      // 如果还需要更多英文字母数字字符
      if (alphaNumericCount < minAlphaNumeric && (minLength - i) <= (minAlphaNumeric - alphaNumericCount)) {
        charType = 'alphaNumeric';
      } else {
        charType = this.getRandomCharType();
      }
      
      if (charType === 'alphaNumeric') {
        alphaNumericCount++;
      }
      
      code += this.getRandomChar(charType);
    }
    
    return code;
  }

  /**
   * 生成多个编号
   * @param {number} count - 生成数量
   * @param {number} length - 每个编号长度
   * @returns {Array} 编号数组
   */
  generateCodes(count = 100, length = 8) {
    const codes = new Set(); // 使用Set避免重复
    
    while (codes.size < count) {
      const code = this.generateSingleCode(length);
      codes.add(code);
    }
    
    return Array.from(codes);
  }

  /**
   * 生成材料编码字典格式
   * @param {number} count - 生成数量
   * @param {number} length - 编号长度
   * @returns {Array} 字典格式数组
   */
  generateMaterialCodeDict(count = 100, length = 8) {
    const codes = this.generateCodes(count, length);
    return codes.map((code, index) => ({
      id: index + 1,
      itemCode: code
    }));
  }

  /**
   * 生成业务编号字典格式
   * @param {number} count - 生成数量
   * @param {number} length - 编号长度
   * @returns {Array} 字典格式数组
   */
  generateBusinessNumberDict(count = 100, length = 7) {
    const codes = this.generateCodes(count, length);
    return codes.map((code, index) => ({
      number: code,
      id: index + 1
    }));
  }

  /**
   * 生成包装编号字典格式
   * @param {number} count - 生成数量
   * @param {number} length - 编号长度
   * @returns {Array} 字典格式数组
   */
  generatePackageNumberDict(count = 100, length = 9) {
    const codes = this.generateCodes(count, length);
    return codes.map((code, index) => ({
      packageNumber: code,
      id: index + 1
    }));
  }

  /**
   * 生成员工编号字典格式
   * @param {number} count - 生成数量
   * @param {number} length - 编号长度
   * @returns {Array} 字典格式数组
   */
  generateStaffNumberDict(count = 100, length = 6) {
    const codes = this.generateCodes(count, length);
    return codes.map((code, index) => ({
      staffNumber: code,
      id: index + 1
    }));
  }

  /**
   * 生成图纸编号（专门的格式）
   * @param {number} count - 生成数量
   * @returns {Array} 图纸编号数组
   */
  generateDrawingCodes(count = 100) {
    const drawings = new Set(); // 使用Set避免重复

    // 图纸编号的前缀模式
    const prefixPatterns = [
      () => this.getRandomChar('alphaNumeric'), // 单个字符或数字
      () => this.getRandomChar('alphaNumeric') + this.getRandomChar('alphaNumeric'), // 两个字符
      () => this.getRandomChar('alphaNumeric') + this.getRandomChar('chinese'), // 字符+汉字
      () => this.getRandomChar('chinese') + this.getRandomChar('alphaNumeric'), // 汉字+字符
    ];

    // 中间部分的模式（类似BLJG, CDSC等）
    const middlePatterns = [
      'BLJG', 'CDSC', 'JGTU', 'XLBG', 'QTJG', 'JGTX', 'JGBG', 'JGSC',
      'BLTX', 'CDTX', 'JGQT', 'XLSC', 'QTBG', 'JGXL', 'BGJG', 'SCTX'
    ];

    // 生成自定义中间部分（使用权重规则）
    const generateCustomMiddle = () => {
      const length = Math.random() < 0.7 ? 4 : (Math.random() < 0.8 ? 3 : 5); // 70%概率4位，20%概率3位，10%概率5位
      let middle = '';
      for (let i = 0; i < length; i++) {
        middle += this.getRandomChar('alphaNumeric');
      }
      return middle;
    };

    while (drawings.size < count) {
      // 随机选择前缀模式
      const prefixGenerator = prefixPatterns[Math.floor(Math.random() * prefixPatterns.length)];
      const prefix = prefixGenerator();

      // 随机选择中间部分（70%使用预定义，30%生成自定义）
      const middle = Math.random() < 0.7
        ? middlePatterns[Math.floor(Math.random() * middlePatterns.length)]
        : generateCustomMiddle();

      // 生成后缀数字（01-99或1001-9999）
      const suffixType = Math.random();
      let suffix;
      if (suffixType < 0.6) {
        // 60%概率：01-99格式
        suffix = String(Math.floor(Math.random() * 99) + 1).padStart(2, '0');
      } else if (suffixType < 0.9) {
        // 30%概率：1-99格式（不补零）
        suffix = String(Math.floor(Math.random() * 99) + 1);
      } else {
        // 10%概率：1001-9999格式
        suffix = String(Math.floor(Math.random() * 8999) + 1001);
      }

      // 随机选择连接符（70%使用短横线，20%不使用，10%使用汉字）
      const connectorType = Math.random();
      let connector;
      if (connectorType < 0.7) {
        connector = '-';
      } else if (connectorType < 0.9) {
        connector = '';
      } else {
        connector = this.getRandomChar('chinese');
      }

      // 组合图纸编号
      const drawingCode = `${prefix}${connector}${middle}${connector}${suffix}`;
      drawings.add(drawingCode);
    }

    return Array.from(drawings);
  }

  /**
   * 生成图纸编号字典格式
   * @param {number} count - 生成数量
   * @returns {Array} 字典格式数组
   */
  generateDrawingDict(count = 100) {
    const codes = this.generateDrawingCodes(count);
    return codes.map((code, index) => ({
      drawname: code,
      drawid: index + 1
    }));
  }
}

module.exports = CodeGenerator;
