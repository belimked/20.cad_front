# 训练数据修正报告

## 📋 问题总结

基于对原始schema和训练数据的对比分析，发现以下关键问题：

### 1. 遗漏的表或字段 ❌
**结论：无遗漏**
- 原始schema包含4张表，训练数据涵盖了所有表
- 所有核心字段都在训练数据中有体现

### 2. 多余的表或字段 ⚠️
**发现问题：**
- **多余表**: `mstb_meterial_project_properties` (不在原始schema中)
- **错误字段**: 
  - `pom_id` (不存在，应为 `mpom_o_id` 和 `o_id`)
  - `material_code` (不存在，应为 `psam_code`)
  - `proj_id` (不存在，应为 `pro_id`)

### 3. 关联关系错误 🔴
**严重问题：**
- 约198个样本使用了错误的关联字段 `pom_id`
- 正确的关联关系应该是：
  ```
  mstb_pms_purchase_order_material.mpom_o_id -> mstb_pms_purchase_order_main.o_id
  ```

### 4. 中文业务属性映射 ✅
**映射正确性：**
- ✅ 项目 -> pro_name, pro_code, pro_id
- ✅ 材料 -> psam_name, psam_code, mpm_id  
- ✅ 采购订单 -> o_order_number, o_id, o_buyer
- ✅ 供应商 -> o_vendorID, o_vendor_companyname
- ✅ 重量/数量/状态/时间等业务属性映射正确

**建议增加的业务术语：**
- 价格 -> pms_po_total_price, mma_pt_cost
- 合同 -> o_con_id
- 阶段 -> o_stageId, o_stageName
- 工艺 -> psam_gyt, psam_jgt
- 规格 -> psam_design_size, psam_process_size
- 单位 -> psam_unit

### 5. 多表查询复杂度 📊
**当前状况：**
- 所有SQL查询最多涉及2张表
- 缺乏3张表及以上的复杂查询

**建议支持的查询类型：**
- 3张表：项目 + 材料 + 采购订单主表
- 4张表：项目 + 材料 + 采购订单主表 + 采购订单材料表

## 🔧 修正方案

### 阶段1：字段名修正
```python
# 需要批量替换的错误字段
replacements = {
    "pom_id": "mpom_o_id",  # 在material表中
    "pom_id": "o_id",       # 在main表中  
    "material_code": "psam_code",
    "proj_id": "pro_id"
}
```

### 阶段2：删除多余表引用
- 移除所有 `mstb_meterial_project_properties` 相关的样本
- 或将其替换为正确的表名

### 阶段3：关联关系修正
```sql
-- 错误的关联 (需要修正)
ON a.pom_id = b.pom_id

-- 正确的关联
ON a.mpom_o_id = b.o_id
```

### 阶段4：增加复杂查询样本
```sql
-- 3张表查询示例
SELECT p.pro_name, pm.psam_name, pom.o_order_number
FROM mstb_project p
JOIN mstb_project_materials pm ON p.pro_id = pm.pro_id
JOIN mstb_pms_purchase_order_main pom ON p.pro_id = pom.o_proId

-- 4张表查询示例  
SELECT p.pro_name, pm.psam_name, pom.o_order_number, pomat.mpom_purchaseNumber
FROM mstb_project p
JOIN mstb_project_materials pm ON p.pro_id = pm.pro_id
JOIN mstb_pms_purchase_order_main pom ON p.pro_id = pom.o_proId
JOIN mstb_pms_purchase_order_material pomat ON pom.o_id = pomat.mpom_o_id
```

## 📈 质量提升建议

### 1. 数据验证脚本
创建自动化脚本验证：
- 字段名是否存在于schema中
- SQL语法是否正确
- 表关联关系是否准确

### 2. 样本平衡
- 增加 negative_relationship 样本（当前仅50个）
- 增加复杂多表查询样本
- 增加业务场景多样性

### 3. 质量控制
- 建立schema一致性检查
- SQL语法验证
- 业务逻辑合理性检查

## 🎯 修正优先级

1. **高优先级** - 字段名错误修正（影响198个样本）
2. **中优先级** - 删除多余表引用
3. **低优先级** - 增加复杂查询样本
4. **持续优化** - 业务术语扩展

## 📊 预期效果

修正后的训练数据将具备：
- ✅ 100%的字段名准确性
- ✅ 正确的表关联关系
- ✅ 支持3-4张表的复杂查询
- ✅ 更丰富的业务场景覆盖
- ✅ 更高的SQL生成准确性

这将显著提升AI模型在数据库查询和分析任务上的表现。
