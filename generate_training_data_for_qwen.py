#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练数据生成脚本 - 专为qwen2.5-3b模型设计
生成业务意图识别的训练数据

作者: Claude 4.0 sonnet
日期: 2025-08-20
"""

import json
import os
import sys
from typing import List, Dict, Any
from collections import Counter
import random

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.service.qwen_api_service import generate_dialogs_and_raw_data


class TrainingDataGenerator:
    """训练数据生成器"""
    
    def __init__(self):
        # 业务对象到业务意图的映射 - 合并货单查询
        self.business_object_mapping = {
            'searchContract': {
                'intent': '查询',
                'object': '合同信息审核单',
                'description': '合同查询'
            },
            'searchPo': {
                'intent': '查询',
                'object': '订单预结算审核单',
                'description': '订单查询'
            },
            'searchStaff': {
                'intent': '查询',
                'object': '人员安排',
                'description': '人员查询'
            },
            'updateCargo': {
                'intent': '更新',
                'object': '货单信息审核单',
                'description': '货单更新'
            },
            'updateStaff': {
                'intent': '更新',
                'object': '人员安排',
                'description': '人员更新'
            },
            # 使用searchCargo作为货单查询的代表
            'searchCargo': {
                'intent': '查询',
                'object': '货单信息审核单',
                'description': '货单查询'
            }
        }

        # 每个业务对象的目标数据量 - 增加到333条，总计2000条
        self.target_samples_per_object = 333

        # 专门为searchCargo增加大量训练数据模板 - 增强泛化能力
        self.searchcargo_templates = [
            # 基础查询模式 - 使用动态货单对象
            "查询{cargo_object}",
            "查看{cargo_object}",
            "查{cargo_object}",
            "看{cargo_object}",
            "帮我查下{cargo_object}",
            "列出{cargo_object}",
            "显示{cargo_object}",
            "找出{cargo_object}",
            "我要查{cargo_object}",
            "需要{cargo_object}",
            "想看{cargo_object}",

            # 时间+货单组合
            "看{time_range}的{cargo_object}",
            "查询{time_range}的{cargo_object}",
            "帮我查下{time_range}的{cargo_object}",
            "查{time_range}的{cargo_object}",
            "查看{time_range}提交的{cargo_object}",
            "查询提交时间在{time_range}的{cargo_object}",

            # 状态+货单组合
            "看{status}的{cargo_object}",
            "查询{status}的{cargo_object}",
            "查{status}{cargo_object}",
            "查询状态为{status}的{cargo_object}",
            "查看{status}状态的{cargo_object}",
            "帮我查下{status}的{cargo_object}",

            # 状态+时间+货单组合
            "看{time_range}{status}的{cargo_object}",
            "查询{time_range}{status}的{cargo_object}",
            "帮我查下{time_range}{status}的{cargo_object}",
            "查{time_range}{status}的{cargo_object}",
            "查看{time_range}{status}状态的{cargo_object}",

            # 逗号分隔语法 - 解决未识别问题的关键
            "看{cargo_object},{status}",
            "查{cargo_object},{time_range}",
            "帮我查下{cargo_object},{status}",
            "查询{cargo_object},{time_range}",
            "看{cargo_object},{time_range}{status}",
            "帮我查下{cargo_object},{time_range}{status}",

            # 特殊时间格式 - 通过时间、处理时间
            "查询{action_time}的{cargo_object}",
            "看{cargo_object},{action_time}",
            "帮我查下{cargo_object},{action_time}",
            "查{action_time}的{cargo_object}",
            "查询{process_time}的{cargo_object}",

            # 带材料类型的货单查询 - 使用动态对象
            "查询{cargo_object}，{material_type}",
            "查看{material_type}的{cargo_object}",
            "查询{material_type}材料的{cargo_object}",
            "查看{material_type}的{cargo_object}",
            "帮我查下{material_type}的{cargo_object}",
            "列出{material_type}材料的{cargo_object}",

            # 🎯 订单混合表述 - 重点丰富（提问货单时关联订单，但业务对象仍是货单）
            "查询{cargo_object}，含有订单编号{order_no}",
            "查看含有订单编号{order_no}的{cargo_object}",
            "查询包含订单{order_no}的{cargo_object}",
            "查看订单编号{order_no}的{cargo_object}",
            "帮我查下订单{order_no}的{cargo_object}",
            "列出订单{order_no}相关的{cargo_object}",

            # 🎯 更多订单+货单混合表述
            "看订单{order_no}的{cargo_object}",
            "查订单{order_no}对应的{cargo_object}",
            "查询订单{order_no}关联的{cargo_object}",
            "查看订单{order_no}相关{cargo_object}",
            "帮我找订单{order_no}的{cargo_object}",
            "需要订单{order_no}的{cargo_object}",
            "想看订单{order_no}的{cargo_object}",
            "订单{order_no}的{cargo_object}在哪",
            "订单{order_no}对应{cargo_object}",

            # 带项目和供应商的货单查询 - 使用动态对象
            "看项目是{project}，供应商是{supplier}的{cargo_object}",
            "查询项目{project}，供应商{supplier}的{cargo_object}",
            "查看{project}项目{supplier}的{cargo_object}",
            "查询{supplier}在{project}的{cargo_object}",
            "帮我查下{project}项目{supplier}的{cargo_object}",

            # 复合查询模式 - 使用动态对象
            "查询{cargo_object}，{material_type},含有订单编号{order_no}",
            "看项目是{project}，供应商是{supplier},{material_type}的{cargo_object}",
            "查询{material_type},含有订单编号{order_no},工程属性是{property}的{cargo_object}",
            "查看{project}项目，{supplier}，{material_type}材料的{cargo_object}",

            # 🎯 订单+项目+供应商混合查询（丰富订单关联）
            "查询{project}项目订单{order_no}的{cargo_object}",
            "看{supplier}供应商订单{order_no}的{cargo_object}",
            "查看{project}项目{supplier}订单{order_no}的{cargo_object}",
            "帮我查下{project}项目订单{order_no}相关的{cargo_object}",
            "查询{supplier}的订单{order_no}对应{cargo_object}",

            # 带材料编号的货单查询 - 使用动态对象
            "查询{cargo_object}，材料编号是{material_code}",
            "查看含材料编号{material_code}的{cargo_object}",
            "查询材料编号{material_code}的{cargo_object}",
            "帮我查下材料编号{material_code}的{cargo_object}",

            # 带工程属性的货单查询 - 使用动态对象
            "查询{cargo_object}，工程属性是{property}",
            "查看工程属性{property}的{cargo_object}",
            "查询{property}工程属性的{cargo_object}",
            "帮我查下{property}的{cargo_object}",

            # 基于验证失败案例的真实表述 - 使用动态对象
            "看{supplier}的，{time_range},{project}项目的{cargo_object}",
            "看状态是{status}，{supplier}的，提交时间在{time_range},是{project}项目的{cargo_object}",
            "看项目是{project}，供应商是{supplier},{material_type}的{cargo_object}",
            "看项目是{project}，供应商是{supplier},工程属性是{property}的{cargo_object}",

            # 复杂组合查询 - 使用动态对象
            "查询{cargo_object}，{material_type},含有订单编号{order_no},工程属性是含材料编号是{material_code}",
            "看项目是{project}，供应商是{supplier},工程属性是{property}的{cargo_object}",
            "查询{project}项目，{supplier}，{material_type}，订单{order_no}的{cargo_object}",
            "查看{material_type}材料，含订单{order_no}，工程属性{property}的{cargo_object}",

            # 🎯 更多订单混合复杂查询
            "查询{project}项目{supplier}订单{order_no}的{material_type}{cargo_object}",
            "看{supplier}的订单{order_no}相关{material_type}材料{cargo_object}",
            "查看{project}项目订单{order_no}对应的{cargo_object}状态",
            "帮我查下{supplier}订单{order_no}的{cargo_object}详情",

            # 增加更多泛化表述 - 使用动态对象
            "我要查{project}的{cargo_object}",
            "帮我找{supplier}的{cargo_object}",
            "需要{material_type}的{cargo_object}",
            "想看{project}项目的{cargo_object}",
            "请查询{supplier}的{cargo_object}",
            "麻烦查下{project}的{cargo_object}",
            "能否查看{material_type}材料的{cargo_object}",
            "请帮忙查询{project}项目{supplier}的{cargo_object}",

            # 不同语序的表述 - 使用动态对象
            "{project}项目的{cargo_object}查询",
            "{supplier}的{cargo_object}查看",
            "{material_type}材料{cargo_object}查询",
            "关于{project}的{cargo_object}",
            "有关{supplier}的{cargo_object}",
            "涉及{material_type}的{cargo_object}"
            "涉及{material_type}的货单结算单"
        ]

        # 数据字典
        self.material_types = ["玻璃", "铝型材", "铝板", "钢材", "不锈钢", "石材", "辅材", "常规附件", "非常规附件", "型材", "附件", "铝合金"]
        self.projects = ["中外运项目一期C区幕墙和铝合金工程", "巴拉瑞特BBHR_Main _Works医院", "前海金融控股大厦", "坂田街道文体中心项目", "51号视觉样板", "32号视觉样板"]
        self.suppliers = ["广东百聚鑫钢构有限公司", "东莞市紧鑫五金有限公司", "广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司"]
        self.order_numbers = ["TUVW012", "ABC123", "DEF456", "GHI789", "JKL012", "MNO345"]
        self.material_codes = ["BL372", "AL123", "ST456", "GL789", "FC012", "AT345"]
        self.properties = ["150x100x15mm角钢", "200x150x20mm角钢", "厚度5mm", "厚度8mm", "规格1200x800", "规格1500x1000"]

        # 专门为人员安排增加大量训练数据模板
        self.staff_query_templates = [
            # 查询人员项目权限 - 增强泛化表述
            "{person}被安排在哪些项目里？",
            "{person}有哪些项目的权限？",
            "{person}以及{person2}和{person3}被安排在哪些项目里？",
            "{person}和{person2}有哪些项目的权限？",
            "查询{person}的项目权限",
            "查看{person}被分配到哪些项目",
            "列出{person}负责的项目",
            "{person}参与了哪些项目？",
            "{person}在哪些项目中有角色？",

            # 增加更多自然表述
            "我想知道{person}在哪些项目",
            "请查{person}的项目安排",
            "帮我看下{person}负责什么项目",
            "{person}都参与了什么项目？",
            "能告诉我{person}的工作安排吗？",
            "{person}目前在哪个项目？",
            "麻烦查下{person}的项目分配",
            "{person}现在负责哪些工作？",

            # 查询项目人员安排 - 增强泛化表述
            "项目{project}被安排了哪些人？",
            "{project}项目被安排了哪些人？",
            "项目{project}以及{project2}项目被安排了哪些人？",
            "{project}，{project2}项目被安排了哪些人？",
            "项目{project}、{project2}、{project3}项目被安排了哪些人？",
            "是{project}和{project2}项目是谁在负责？",
            "查询{project}的人员安排",
            "查看{project}项目的负责人",
            "列出{project}的工作人员",
            "{project}有哪些人员？",
            "{project}的团队成员是谁？",

            # 增加更多自然表述
            "我想了解{project}的人员配置",
            "请告诉我{project}有哪些人",
            "帮我查下{project}的团队",
            "{project}都有谁在做？",
            "能看看{project}的人员名单吗？",
            "{project}项目谁在负责？",
            "麻烦查询{project}的工作人员",
            "{project}现在有哪些员工？",
            "想知道{project}的人员情况",

            # 复杂项目名称查询（基于失败案例）
            "是{project}和{project2}和{project3}项目是谁在负责？",
            "项目是{project}和{project2}项目被安排了哪些人？",
            "{project}以及{project2}以及{project3}项目被安排了哪些人？"
        ]

        self.staff_update_templates = [
            # 安排人员 - 增强泛化表述
            "安排项目人员，将{person}安排到{project}的{role}角色",
            "安排项目人员，将{person}安排到{project}以及{project2}项目的{role}角色",
            "添加项目人员，{person}到{project}项目担任{role}",
            "添加项目人员,将{person}安排到{project}的{role}",
            "将{person}安排到{project}的{role}负责人",
            "设置{person}为{project}的{role}",
            "安排{person}到{project}项目",
            "添加{person}为{project}的负责人",
            "将{person}分配到{project}",
            "指派{person}负责{project}的{role}工作",

            # 增加更多自然表述
            "我要把{person}安排到{project}",
            "请将{person}加入{project}项目",
            "让{person}负责{project}的{role}",
            "把{person}分配给{project}",
            "需要{person}去{project}做{role}",
            "安排{person}参与{project}项目",
            "请添加{person}到{project}团队",
            "{person}去{project}负责{role}工作",

            # 删除/撤销人员 - 增强泛化表述
            "删除人员，将{person}{project}项目的{role}角色中移除",
            "撤销人员,将{person}从{project}的{role}角色中移除",
            "将{person}从{project}项目中删除",
            "移除{person}在{project}的{role}角色",
            "撤销{person}从{project}项目",
            "删除{person}的{project}项目权限",
            "将{person}({code})从{project}项目的{role}角色中移除",
            "撤销人员,将{person}以及{person2}从{project}项目的{role}角色中移除",
            "删除人员，将{person}和{person2}从{project}、{project2}的{role}角色中移除",
            "将{person}从全部项目中删除",
            "撤销{person}的全部项目权限",

            # 增加更多自然表述
            "我要把{person}从{project}移除",
            "请将{person}从{project}项目中删除",
            "不要{person}负责{project}了",
            "把{person}从{project}团队中移出",
            "需要撤销{person}的{project}权限",
            "请删除{person}在{project}的角色",
            "让{person}不再参与{project}",
            "{person}不用做{project}的{role}了",

            # 多人安排（基于失败案例）
            "安排项目人员，将{person}和{person2},{person3}({code})安排到{project}，{project2}项目的{role}角色",
            "添加项目人员,将{person}({code})，{person2}安排到项目是{project},{project2}以及{project3}的{role}角色",
            "撤销项目人员，将{person}({code})和{person2}-{person3}，{project}，{project2}项目的{role}以及{role2}角色中移除"
        ]

        # 人员姓名（基于失败案例）
        self.person_names = [
            "汤焕", "江泳", "刘志昆", "张伟浪", "付明辉", "刘毅", "魏越兴", "熊建梅",
            "高威刚", "熊建伟", "梁汝科", "廖宁林", "兰家其", "邹旭强", "华伟", "汪锦林", "孙洪",
            "张伟", "李娜", "王芳", "刘翔", "陈静", "杨军", "赵敏", "孙强", "周丽", "吴涛"
        ]

        # 工号格式
        self.employee_codes = ["051707", "051702", "091305", "091306", "061203", "061208", "061202", "101407", "041509", "101409", "021128", "031008", "101410"]

        # 角色信息
        self.roles = ["石材负责人", "常规附件负责人", "常规附件", "钢材负责人", "钢材", "铝型材负责人", "铝板负责人", "玻璃负责人", "辅材负责人", "非常规附件", "不锈钢负责人", "非常规", "非常规附件责任人", "不锈钢"]

        # 复杂项目名称（基于失败案例）
        self.complex_projects = [
            "新世界香蜜四季家园项目商业展示区", "OPPO智能制造中心地块二南区宿舍楼", "岁宝一期壹品苑D栋项目",
            "广东建工科创大厦", "实验103", "墨尔本187 Grattan Street学生公寓", "中山大学附属第七医院（深圳）二期",
            "实验62", "前海金融控股大厦", "坂田街道文体中心项目", "51号视觉样板", "32号视觉样板",
            "海灏生物创新港", "实验104", "实验26", "盛和湾区大厦", "墨尔本WarringalPrivateHospitalStage2",
            "欢聚集团三龙湾项目A地块", "尚智科技园项目幕墙工程", "紫元元大厦项目幕墙制作及安装工程",
            "华彩海口湾广场幕墙工程", "实验68", "龙光玖钻商务中心中期幕墙工程09地块", "创智云城项目三期幕墙工程",
            "福田湾区智慧广场", "实验95", "实验78", "墨尔本36W_ST_C惠灵顿办公楼", "香蜜湖国际公寓", "实验42", "酷狗音乐大厦"
        ]

        # 专门为updateCargo增加大量训练数据模板
        self.updatecargo_templates = [
            # 基础更新操作 - 使用动态货单对象
            "更新{cargo_object}",
            "修改{cargo_object}",
            "编辑{cargo_object}",
            "调整{cargo_object}",
            "处理{cargo_object}",
            "操作{cargo_object}",

            # 导出操作 - 使用动态货单对象
            "导出{cargo_object}",
            "导出{cargo_object},项目{project},供应商送货单号{delivery_no}以及{delivery_no2},供应商是{supplier}的",
            "导出{cargo_object}，{supplier}，单{delivery_no},项目是{project}，{project2}",
            "导出{cargo_object}，供应商是{supplier}，{supplier2}的，供应商送货单号{delivery_no},项目是{project}",
            "导出{cargo_object}，项目是{project}，送货单:{delivery_no}，{supplier}",
            "导出{project}项目的{cargo_object}，供应商{supplier}，送货单号{delivery_no}",
            "请导出{supplier}的{cargo_object}，项目{project}，送货单{delivery_no}",
            "需要导出{cargo_object}，{project}项目，{supplier}，单号{delivery_no}",

            # 🎯 订单混合更新操作（重点丰富）
            "更新订单{order_no}的{cargo_object}",
            "修改订单{order_no}对应的{cargo_object}",
            "处理订单{order_no}相关{cargo_object}",
            "导出订单{order_no}的{cargo_object}",
            "审核订单{order_no}的{cargo_object}",
            "对比订单{order_no}的{cargo_object}重量",
            "计算订单{order_no}的{cargo_object}附加费用",

            # 对比送货单操作 - 使用动态对象
            "对比以下{cargo_object}的重量，并计算附加费用，是{supplier}的,供应商送货单号为{delivery_no}（{weight}），项目是{project},{project2}、{project3}",
            "对比以下{cargo_object}的面积，并计算附加费用,{project}以及{project2},{project3}项目,供应商是{supplier}的,供应商送货单号为{delivery_no}（{area}）以及{delivery_no2}（{area2}）,{delivery_no3}（{area3}）",
            "对比以下{cargo_object}的重量，并计算附加费用，是{project}项目,供应商是{supplier}，供应商送货单号{delivery_no}（{weight}）",
            "对比以下{cargo_object}的重量，并计算附加费用，{cargo_object}{delivery_no}（{weight}）、{delivery_no2}（{weight2}）和{delivery_no3}（{weight3}）,项目是{project},供应商{supplier}",
            "对比以下{cargo_object}的件数，并计算附加费用，项目{project}，{project2}，{project3}，发货单号{delivery_no}（{count}）以及{delivery_no2}（{count2}），{delivery_no3}（{count3}）,{supplier}以及{supplier2}",

            # 审核通过操作 - 使用动态对象
            "审核通过{cargo_object}{delivery_no}，项目{project}，供应商{supplier}",
            "审核通过{supplier}的{cargo_object}{delivery_no}，{project}项目",
            "通过{project}项目的{cargo_object}审核，送货单{delivery_no}，供应商{supplier}",
            "批准{supplier}的{cargo_object}，项目{project}，单号{delivery_no}",
            "确认通过{cargo_object}{delivery_no}的审核，{project}项目",

            # 批量操作 - 使用动态对象
            "批量导出{project}、{project2}项目的{cargo_object}，供应商{supplier}",
            "批量审核{supplier}的{cargo_object}，项目{project}，{project2}",
            "批量对比{project}项目的{cargo_object}重量，供应商{supplier}",
            "批量计算{supplier}的{cargo_object}附加费用，项目{project}、{project2}",
            "批量处理{project}项目的{cargo_object}",
            "批量更新{supplier}的{cargo_object}",

            # 🎯 订单批量操作混合
            "批量导出订单{order_no}相关的{cargo_object}",
            "批量处理订单{order_no}、{order_no2}的{cargo_object}",
            "批量审核订单{order_no}对应{cargo_object}",

            # 更多自然表述 - 使用动态对象
            "我要导出{project}的{cargo_object}",
            "请帮我对比这些{cargo_object}的重量",
            "需要计算{supplier}的{cargo_object}附加费用",
            "帮我审核{project}的{cargo_object}",
            "想导出{supplier}的{cargo_object}",
            "麻烦对比一下{cargo_object}面积",
            "请计算这批{cargo_object}的附加费用",
            "需要审核通过这个{cargo_object}",
            "更新{cargo_object}状态",
            "修改{cargo_object}信息",
            "处理{cargo_object}数据",

            # 🎯 更多订单相关自然表述
            "我要处理订单{order_no}的{cargo_object}",
            "请更新订单{order_no}相关{cargo_object}",
            "需要修改订单{order_no}的{cargo_object}信息",
            "帮我导出订单{order_no}对应的{cargo_object}"
        ]

        # 送货单号
        self.delivery_numbers = ["W4X5Y6", "XYZ6789", "BCD6789", "TUV7890", "G7H8I9", "Q7R8S9", "BCDE789", "LMN1234", "ZAB5678", "C1D2E3", "I7J8K9", "KLM5678", "S1T2U3", "BCD3456", "HIJ1234", "STU1234"]

        # 数值数据
        self.weights = ["63.09", "36.42", "22.33", "33.44", "81.27", "18.62", "321", "75.24", "6789"]
        self.areas = ["36.42", "22.33", "33.44", "81.27", "18.62", "75.24"]
        self.counts = ["432.1", "876.54", "77.7", "123.45", "234.56", "345.67"]

        # 专门为searchContract增加大量训练数据模板 - 使用动态合同表述字典
        self.searchcontract_templates = [
            # 基础查询模式 - 使用动态合同对象
            "查询{contract_object}",
            "查看{contract_object}",
            "查{contract_object}",
            "看{contract_object}",
            "帮我查下{contract_object}",
            "列出{contract_object}",
            "显示{contract_object}",
            "找出{contract_object}",
            "我要查{contract_object}",
            "需要{contract_object}",
            "想看{contract_object}",

            # 时间+合同组合
            "看{time_range}的{contract_object}",
            "查询{time_range}的{contract_object}",
            "帮我查下{time_range}的{contract_object}",
            "查{time_range}的{contract_object}",
            "查看{time_range}提交的{contract_object}",
            "查询提交时间在{time_range}的{contract_object}",

            # 状态+合同组合
            "看{status}的{contract_object}",
            "查询{status}的{contract_object}",
            "查{status}{contract_object}",
            "查询状态为{status}的{contract_object}",
            "查看{status}状态的{contract_object}",
            "帮我查下{status}的{contract_object}",

            # 状态+时间+合同组合
            "看{time_range}{status}的{contract_object}",
            "查询{time_range}{status}的{contract_object}",
            "帮我查下{time_range}{status}的{contract_object}",
            "查{time_range}{status}的{contract_object}",
            "查看{time_range}{status}状态的{contract_object}",

            # 逗号分隔语法 - 解决未识别问题的关键
            "看{contract_object},{status}",
            "查{contract_object},{time_range}",
            "帮我查下{contract_object},{status}",
            "查询{contract_object},{time_range}",
            "看{contract_object},{time_range}{status}",
            "帮我查下{contract_object},{time_range}{status}",

            # 特殊时间格式 - 通过时间、处理时间
            "查询{action_time}的{contract_object}",
            "看{contract_object},{action_time}",
            "帮我查下{contract_object},{action_time}",
            "查{action_time}的{contract_object}",
            "查询{process_time}的{contract_object}",

            # 带项目和供应商的合同查询 - 使用动态对象
            "查询{project}项目的{contract_object}",
            "查看{supplier}的{contract_object}",
            "查询{project}项目{supplier}的{contract_object}",
            "查看{supplier}在{project}的{contract_object}",
            "帮我查下{project}项目的{contract_object}",

            # 复合查询模式 - 使用动态对象
            "查询{contract_object}，{material_type},项目{project}",
            "看项目是{project}，供应商是{supplier}的{contract_object}",
            "查询{material_type}材料的{contract_object}，项目{project}",
            "查看{project}项目，{supplier}，{material_type}的{contract_object}",

            # 基于验证失败案例的真实表述 - 使用动态对象
            "查是{project}，{project2}以及{project3}项目，{status}，{supplier}的{contract_object}",
            "找出来项目是{project},{project2}，{project3}，{status},提交日在{time_range}的{contract_object}",
            "看{supplier}的，{time_range},{project}项目的{contract_object}",
            "看状态是{status}，{supplier}的，提交时间在{time_range},是{project}项目的{contract_object}",
            "看项目是{project}，供应商是{supplier},{material_type}的{contract_object}",

            # 增加更多泛化表述 - 使用动态对象
            "我要查{project}的{contract_object}",
            "帮我找{supplier}的{contract_object}",
            "需要{material_type}的{contract_object}",
            "想看{project}项目的{contract_object}",
            "请查询{supplier}的{contract_object}",
            "麻烦查下{project}的{contract_object}",
            "能否查看{material_type}材料的{contract_object}",
            "请帮忙查询{project}项目{supplier}的{contract_object}",

            # 不同语序的表述 - 使用动态对象
            "{project}项目的{contract_object}查询",
            "{supplier}的{contract_object}查看",
            "{material_type}材料{contract_object}查询",
            "关于{project}的{contract_object}",
            "有关{supplier}的{contract_object}",
            "涉及{material_type}的{contract_object}"
        ]

        # 合同表述变体字典
        self.contract_objects = [
            "合同",
            "合同信息审核单",
            "合同审核单",
            "合同信息",
            "合同结算单",
            "合同结算审核单"
        ]

        # 合同状态 - 扩展版
        self.contract_statuses = ["待审", "驳回", "通过", "审核中", "已提交", "未审核", "已审核", "待确认", "处理", "已处理", "待处理", "审核", "已审核完成", "审核完成", "批准", "已批准", "拒绝", "已拒绝", "完成", "已完成"]

        # 时间范围 - 扩展版
        self.time_ranges = ["最近一周", "最近两周", "最近一个月", "最近三个月", "本月", "上个月", "本季度", "上个季度", "上个年度", "最近一年", "这周", "上周", "本周", "最近5天", "最近五天", "最近3天", "最近三天", "最近10天", "最近十天", "最近半个月", "最近15天", "最近20天", "最近30天"]

        # 特殊时间格式
        self.action_time_ranges = ["通过时间在最近一周", "通过时间在最近五天", "通过时间在本月", "通过时间在上个季度", "通过时间在最近一年", "通过时间在最近3天", "通过时间在最近10天", "通过时间在这个月"]
        self.process_time_ranges = ["处理时间在最近一周", "处理时间在最近五天", "审核时间在本月", "处理时间在上个季度", "审核时间在最近一年"]

        # 订单表述变体字典
        self.po_objects = [
            "订单",
            "订单预结算审核单",
            "订单审核单",
            "预审单",
            "预结算审核单",
            "订单预审单",
            "预结算单",
            "订单预结算单"
        ]

        # 货单表述变体字典 - 供searchCargo和updateCargo共享
        self.cargo_objects = [
            "货单",
            "货单信息审核单",
            "货单审核单",
            "发货单",
            "结算审核单",
            "结算单",
            "货单结算审核单",
            "货单结算单"
        ]

        # 专门为searchPo增加大量训练数据模板 - 使用动态订单表述字典
        self.searchpo_templates = [
            # 基础查询模式 - 使用动态订单对象
            "查询{po_object}",
            "查看{po_object}",
            "查{po_object}",
            "看{po_object}",
            "帮我查下{po_object}",
            "列出{po_object}",
            "显示{po_object}",
            "找出{po_object}",
            "我要查{po_object}",
            "需要{po_object}",
            "想看{po_object}",

            # 基于验证失败案例的真实表述
            "查存在异形材料的,项目是{project}以及{project2}，状态是{status}，提交日期在{time_range}，{supplier}的的预审单",
            "看项目{project}以及{project2}以及{project3}，材料类型为{material_type},属性为含编号{material_code},{supplier}的预结算单",
            "查{project}，{project2}，{project3}，{status},提交日在{time_range}的预结算审核单",
            "看{supplier}的，{time_range},{project}项目的预结算单",
            "看状态是{status}，{supplier}的，提交时间在{time_range},是{project}项目的预结算审核单",
            "看项目是{project}，供应商是{supplier},{material_type}的预结算单",

            # 时间+订单组合
            "看{time_range}的{po_object}",
            "查询{time_range}的{po_object}",
            "帮我查下{time_range}的{po_object}",
            "查{time_range}的{po_object}",
            "查看{time_range}提交的{po_object}",
            "查询提交时间在{time_range}的{po_object}",

            # 状态+订单组合
            "看{status}的{po_object}",
            "查询{status}的{po_object}",
            "查{status}{po_object}",
            "查询状态为{status}的{po_object}",
            "查看{status}状态的{po_object}",
            "帮我查下{status}的{po_object}",

            # 状态+时间+订单组合
            "看{time_range}{status}的{po_object}",
            "查询{time_range}{status}的{po_object}",
            "帮我查下{time_range}{status}的{po_object}",
            "查{time_range}{status}的{po_object}",
            "查看{time_range}{status}状态的{po_object}",
            # 逗号分隔语法 - 解决未识别问题的关键
            "看{po_object},{status}",
            "查{po_object},{time_range}",
            "帮我查下{po_object},{status}",
            "查询{po_object},{time_range}",
            "看{po_object},{time_range}{status}",
            "帮我查下{po_object},{time_range}{status}",

            # 特殊时间格式 - 通过时间、处理时间
            "查询{action_time}的{po_object}",
            "看{po_object},{action_time}",
            "帮我查下{po_object},{action_time}",
            "查{action_time}的{po_object}",
            "查询{process_time}的{po_object}",

            # 带项目和供应商的订单查询 - 使用动态对象
            "查询{project}项目的{po_object}",
            "查看{supplier}的{po_object}",
            "查询{project}项目{supplier}的{po_object}",
            "查看{supplier}在{project}的{po_object}",
            "帮我查下{project}项目的{po_object}",

            # 带材料类型的订单查询 - 使用动态对象
            "查询{material_type}材料的{po_object}",
            "查看{material_type}的{po_object}",
            "查询含{material_type}的{po_object}",
            "查看{material_type}材料的{po_object}",
            "帮我查下{material_type}的{po_object}",

            # 带材料编号的订单查询 - 使用动态对象
            "查询含编号{material_code}的{po_object}",
            "查看编号{material_code}的{po_object}",
            "查询材料编号{material_code}的{po_object}",
            "查看含编号{material_code}的{po_object}",
            "帮我查下编号{material_code}的{po_object}",

            # 复合查询模式 - 使用动态对象
            "查询{po_object}，{material_type},项目{project}",
            "看项目是{project}，供应商是{supplier}的{po_object}",
            "查询{material_type}材料的{po_object}，项目{project}",
            "查看{project}项目，{supplier}，{material_type}的{po_object}",

            # 基于验证失败案例的真实表述 - 使用动态对象
            "查存在异形材料的,项目是{project}以及{project2}，状态是{status}，提交日期在{time_range}，{supplier}的的{po_object}",
            "看项目{project}以及{project2}以及{project3}，材料类型为{material_type},属性为含编号{material_code},{supplier}的{po_object}",
            "查{project}，{project2}，{project3}，{status},提交日在{time_range}的{po_object}",
            "看{supplier}的，{time_range},{project}项目的{po_object}",
            "看状态是{status}，{supplier}的，提交时间在{time_range},是{project}项目的{po_object}",
            "看项目是{project}，供应商是{supplier},{material_type}的{po_object}",

            # 异形材料相关 - 使用动态对象
            "查存在异形材料的{po_object}",
            "查询含异形材料的{po_object}",
            "查看异形材料的{po_object}",
            "查询异形{material_type}的{po_object}",
            "查看含异形材料的{po_object}",

            # 增加更多泛化表述 - 使用动态对象
            "我要查{project}的{po_object}",
            "帮我找{supplier}的{po_object}",
            "需要{material_type}的{po_object}",
            "想看{project}项目的{po_object}",
            "请查询{supplier}的{po_object}",
            "麻烦查下{project}的{po_object}",
            "能否查看{material_type}材料的{po_object}",
            "请帮忙查询{project}项目{supplier}的{po_object}",

            # 不同语序的表述 - 使用动态对象
            "{project}项目的{po_object}查询",
            "{supplier}的{po_object}查看",
            "{material_type}材料{po_object}查询",
            "关于{project}的{po_object}",
            "有关{supplier}的{po_object}",
            "涉及{material_type}的预结算审核单"
        ]

        # 预结算状态
        self.po_statuses = ["待审", "驳回", "通过", "审核中", "已提交", "未审核", "已审核", "待确认", "预审中", "预审通过"]
        
    def generate_natural_language_from_question_data(self, question_data: Dict, business_object: str) -> str:
        """
        将问题数据转换为自然语言
        
        Args:
            question_data: 问题数据字典
            business_object: 业务对象名称
            
        Returns:
            自然语言字符串
        """
        # 过滤掉空值和无意义的字段
        meaningful_parts = []
        
        for key, value in question_data.items():
            if value and str(value).strip() and str(value) not in ['', '的', '和', '将', '到', '去', '从', '角色']:
                meaningful_parts.append(str(value))
        
        # 组合成自然语言
        if meaningful_parts:
            # 简单的连接，保持自然性
            natural_text = ''.join(meaningful_parts)
            
            # 特殊处理：确保语句的完整性
            if not natural_text.endswith(('？', '。', '！')):
                # 根据业务对象类型添加适当的结尾
                if 'search' in business_object:
                    if not any(char in natural_text for char in ['查询', '查', '看', '找', '列出']):
                        natural_text = '查询' + natural_text
                elif 'update' in business_object:
                    if not any(char in natural_text for char in ['安排', '添加', '更新', '修改']):
                        natural_text = '安排' + natural_text
            
            return natural_text
        else:
            # 如果没有有意义的部分，返回一个默认查询
            mapping = self.business_object_mapping.get(business_object, {})
            return f"查询{mapping.get('object', '相关信息')}"
    
    def generate_business_object_data(self, business_object: str) -> List[Dict]:
        """
        为单个业务对象生成训练数据

        Args:
            business_object: 业务对象名称

        Returns:
            训练数据列表
        """
        print(f"正在生成 {business_object} 的训练数据...")

        try:
            training_data = []
            mapping = self.business_object_mapping.get(business_object, {})
            intent = mapping.get('intent', '查询')
            obj = mapping.get('object', '未知对象')

            # 特殊处理searchCargo - 使用模板生成大量数据
            if business_object == 'searchCargo':
                print(f"  使用专门模板生成货单查询数据...")

                # 生成大量货单查询数据
                for _ in range(self.target_samples_per_object * 2):  # 生成2倍数据量
                    template = random.choice(self.searchcargo_templates)

                    # 填充模板变量 - 新增动态货单对象和特殊时间格式
                    user_content = template
                    if '{cargo_object}' in user_content:
                        user_content = user_content.replace('{cargo_object}', random.choice(self.cargo_objects))
                    if '{material_type}' in user_content:
                        user_content = user_content.replace('{material_type}', random.choice(self.material_types))
                    if '{project}' in user_content:
                        user_content = user_content.replace('{project}', random.choice(self.projects))
                    if '{supplier}' in user_content:
                        user_content = user_content.replace('{supplier}', random.choice(self.suppliers))
                    if '{order_no}' in user_content:
                        user_content = user_content.replace('{order_no}', random.choice(self.order_numbers))
                    if '{material_code}' in user_content:
                        user_content = user_content.replace('{material_code}', random.choice(self.material_codes))
                    if '{property}' in user_content:
                        user_content = user_content.replace('{property}', random.choice(self.properties))
                    if '{status}' in user_content:
                        user_content = user_content.replace('{status}', random.choice(self.contract_statuses))
                    if '{time_range}' in user_content:
                        user_content = user_content.replace('{time_range}', random.choice(self.time_ranges))
                    if '{action_time}' in user_content:
                        user_content = user_content.replace('{action_time}', random.choice(self.action_time_ranges))
                    if '{process_time}' in user_content:
                        user_content = user_content.replace('{process_time}', random.choice(self.process_time_ranges))

                    # 构建训练数据
                    training_item = {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_content
                            },
                            {
                                "role": "assistant",
                                "content": f"业务意图[{intent}]业务对象[{obj}]"
                            }
                        ]
                    }

                    training_data.append(training_item)

            # 特殊处理searchStaff - 使用模板生成大量人员查询数据
            elif business_object == 'searchStaff':
                print(f"  使用专门模板生成人员查询数据...")

                # 生成大量人员查询数据
                for _ in range(self.target_samples_per_object * 3):  # 生成3倍数据量
                    template = random.choice(self.staff_query_templates)

                    # 填充模板变量
                    user_content = template
                    if '{person}' in user_content:
                        user_content = user_content.replace('{person}', random.choice(self.person_names))
                    if '{person2}' in user_content:
                        user_content = user_content.replace('{person2}', random.choice(self.person_names))
                    if '{person3}' in user_content:
                        user_content = user_content.replace('{person3}', random.choice(self.person_names))
                    if '{project}' in user_content:
                        user_content = user_content.replace('{project}', random.choice(self.complex_projects))
                    if '{project2}' in user_content:
                        user_content = user_content.replace('{project2}', random.choice(self.complex_projects))
                    if '{project3}' in user_content:
                        user_content = user_content.replace('{project3}', random.choice(self.complex_projects))

                    # 构建训练数据
                    training_item = {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_content
                            },
                            {
                                "role": "assistant",
                                "content": f"业务意图[{intent}]业务对象[{obj}]"
                            }
                        ]
                    }

                    training_data.append(training_item)

            # 特殊处理updateStaff - 使用模板生成大量人员更新数据
            elif business_object == 'updateStaff':
                print(f"  使用专门模板生成人员更新数据...")

                # 生成大量人员更新数据
                for _ in range(self.target_samples_per_object * 3):  # 生成3倍数据量
                    template = random.choice(self.staff_update_templates)

                    # 填充模板变量
                    user_content = template
                    if '{person}' in user_content:
                        user_content = user_content.replace('{person}', random.choice(self.person_names))
                    if '{person2}' in user_content:
                        user_content = user_content.replace('{person2}', random.choice(self.person_names))
                    if '{person3}' in user_content:
                        user_content = user_content.replace('{person3}', random.choice(self.person_names))
                    if '{project}' in user_content:
                        user_content = user_content.replace('{project}', random.choice(self.complex_projects))
                    if '{project2}' in user_content:
                        user_content = user_content.replace('{project2}', random.choice(self.complex_projects))
                    if '{project3}' in user_content:
                        user_content = user_content.replace('{project3}', random.choice(self.complex_projects))
                    if '{role}' in user_content:
                        user_content = user_content.replace('{role}', random.choice(self.roles))
                    if '{role2}' in user_content:
                        user_content = user_content.replace('{role2}', random.choice(self.roles))
                    if '{code}' in user_content:
                        user_content = user_content.replace('{code}', random.choice(self.employee_codes))

                    # 构建训练数据
                    training_item = {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_content
                            },
                            {
                                "role": "assistant",
                                "content": f"业务意图[{intent}]业务对象[{obj}]"
                            }
                        ]
                    }

                    training_data.append(training_item)

            # 特殊处理updateCargo - 使用模板生成大量货单更新数据
            elif business_object == 'updateCargo':
                print(f"  使用专门模板生成货单更新数据...")

                # 生成大量货单更新数据
                for _ in range(self.target_samples_per_object * 2):  # 生成2倍数据量
                    template = random.choice(self.updatecargo_templates)

                    # 填充模板变量 - 新增动态货单对象
                    user_content = template
                    if '{cargo_object}' in user_content:
                        user_content = user_content.replace('{cargo_object}', random.choice(self.cargo_objects))
                    if '{order_no}' in user_content:
                        user_content = user_content.replace('{order_no}', random.choice(self.order_numbers))
                    if '{order_no2}' in user_content:
                        user_content = user_content.replace('{order_no2}', random.choice(self.order_numbers))
                    if '{project}' in user_content:
                        user_content = user_content.replace('{project}', random.choice(self.complex_projects))
                    if '{project2}' in user_content:
                        user_content = user_content.replace('{project2}', random.choice(self.complex_projects))
                    if '{project3}' in user_content:
                        user_content = user_content.replace('{project3}', random.choice(self.complex_projects))
                    if '{supplier}' in user_content:
                        user_content = user_content.replace('{supplier}', random.choice(self.suppliers))
                    if '{supplier2}' in user_content:
                        user_content = user_content.replace('{supplier2}', random.choice(self.suppliers))
                    if '{delivery_no}' in user_content:
                        user_content = user_content.replace('{delivery_no}', random.choice(self.delivery_numbers))
                    if '{delivery_no2}' in user_content:
                        user_content = user_content.replace('{delivery_no2}', random.choice(self.delivery_numbers))
                    if '{delivery_no3}' in user_content:
                        user_content = user_content.replace('{delivery_no3}', random.choice(self.delivery_numbers))
                    if '{weight}' in user_content:
                        user_content = user_content.replace('{weight}', random.choice(self.weights))
                    if '{weight2}' in user_content:
                        user_content = user_content.replace('{weight2}', random.choice(self.weights))
                    if '{weight3}' in user_content:
                        user_content = user_content.replace('{weight3}', random.choice(self.weights))
                    if '{area}' in user_content:
                        user_content = user_content.replace('{area}', random.choice(self.areas))
                    if '{area2}' in user_content:
                        user_content = user_content.replace('{area2}', random.choice(self.areas))
                    if '{area3}' in user_content:
                        user_content = user_content.replace('{area3}', random.choice(self.areas))
                    if '{count}' in user_content:
                        user_content = user_content.replace('{count}', random.choice(self.counts))
                    if '{count2}' in user_content:
                        user_content = user_content.replace('{count2}', random.choice(self.counts))
                    if '{count3}' in user_content:
                        user_content = user_content.replace('{count3}', random.choice(self.counts))

                    # 构建训练数据
                    training_item = {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_content
                            },
                            {
                                "role": "assistant",
                                "content": f"业务意图[{intent}]业务对象[{obj}]"
                            }
                        ]
                    }

                    training_data.append(training_item)

            # 特殊处理searchContract - 使用模板生成大量合同查询数据，增强与人员查询的区分度
            elif business_object == 'searchContract':
                print(f"  使用专门模板生成合同查询数据...")

                # 生成大量合同查询数据
                for _ in range(self.target_samples_per_object * 2):  # 生成2倍数据量
                    template = random.choice(self.searchcontract_templates)

                    # 填充模板变量 - 新增动态合同对象和特殊时间格式
                    user_content = template
                    if '{contract_object}' in user_content:
                        user_content = user_content.replace('{contract_object}', random.choice(self.contract_objects))
                    if '{project}' in user_content:
                        user_content = user_content.replace('{project}', random.choice(self.complex_projects))
                    if '{project2}' in user_content:
                        user_content = user_content.replace('{project2}', random.choice(self.complex_projects))
                    if '{project3}' in user_content:
                        user_content = user_content.replace('{project3}', random.choice(self.complex_projects))
                    if '{supplier}' in user_content:
                        user_content = user_content.replace('{supplier}', random.choice(self.suppliers))
                    if '{material_type}' in user_content:
                        user_content = user_content.replace('{material_type}', random.choice(self.material_types))
                    if '{status}' in user_content:
                        user_content = user_content.replace('{status}', random.choice(self.contract_statuses))
                    if '{time_range}' in user_content:
                        user_content = user_content.replace('{time_range}', random.choice(self.time_ranges))
                    if '{action_time}' in user_content:
                        user_content = user_content.replace('{action_time}', random.choice(self.action_time_ranges))
                    if '{process_time}' in user_content:
                        user_content = user_content.replace('{process_time}', random.choice(self.process_time_ranges))

                    # 构建训练数据
                    training_item = {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_content
                            },
                            {
                                "role": "assistant",
                                "content": f"业务意图[{intent}]业务对象[{obj}]"
                            }
                        ]
                    }

                    training_data.append(training_item)

            # 特殊处理searchPo - 使用模板生成大量预结算查询数据，增强与人员查询的区分度
            elif business_object == 'searchPo':
                print(f"  使用专门模板生成预结算查询数据...")

                # 生成大量预结算查询数据
                for _ in range(self.target_samples_per_object * 2):  # 生成2倍数据量
                    template = random.choice(self.searchpo_templates)

                    # 填充模板变量 - 新增动态订单对象和特殊时间格式
                    user_content = template
                    if '{po_object}' in user_content:
                        user_content = user_content.replace('{po_object}', random.choice(self.po_objects))
                    if '{project}' in user_content:
                        user_content = user_content.replace('{project}', random.choice(self.complex_projects))
                    if '{project2}' in user_content:
                        user_content = user_content.replace('{project2}', random.choice(self.complex_projects))
                    if '{project3}' in user_content:
                        user_content = user_content.replace('{project3}', random.choice(self.complex_projects))
                    if '{supplier}' in user_content:
                        user_content = user_content.replace('{supplier}', random.choice(self.suppliers))
                    if '{material_type}' in user_content:
                        user_content = user_content.replace('{material_type}', random.choice(self.material_types))
                    if '{status}' in user_content:
                        user_content = user_content.replace('{status}', random.choice(self.po_statuses))
                    if '{time_range}' in user_content:
                        user_content = user_content.replace('{time_range}', random.choice(self.time_ranges))
                    if '{action_time}' in user_content:
                        user_content = user_content.replace('{action_time}', random.choice(self.action_time_ranges))
                    if '{process_time}' in user_content:
                        user_content = user_content.replace('{process_time}', random.choice(self.process_time_ranges))
                    if '{material_code}' in user_content:
                        user_content = user_content.replace('{material_code}', random.choice(self.material_codes))

                    # 构建训练数据
                    training_item = {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_content
                            },
                            {
                                "role": "assistant",
                                "content": f"业务意图[{intent}]业务对象[{obj}]"
                            }
                        ]
                    }

                    training_data.append(training_item)

            else:
                # 其他业务对象使用原有逻辑
                actual_business_object = business_object

                # 使用现有框架生成原始数据
                _, raw_data = generate_dialogs_and_raw_data(
                    business_object=actual_business_object,
                    total_samples=min(self.target_samples_per_object, 200),
                    variations_per_rule=2,
                    ruleids=None
                )

                # 限制数据量，确保分布均匀
                max_items = min(len(raw_data), self.target_samples_per_object)

                for i, item in enumerate(raw_data[:max_items]):
                    question_data = item.get('question', {})

                    # 生成自然语言
                    user_content = self.generate_natural_language_from_question_data(question_data, business_object)

                    # 生成助手回复
                    assistant_content = f"业务意图[{intent}]业务对象[{obj}]"

                    # 构建训练数据格式
                    training_item = {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_content
                            },
                            {
                                "role": "assistant",
                                "content": assistant_content
                            }
                        ]
                    }

                    training_data.append(training_item)

            print(f"✓ {business_object} 生成了 {len(training_data)} 条数据")
            return training_data

        except Exception as e:
            print(f"✗ 生成 {business_object} 数据时出错: {e}")
            # 如果失败，生成一些基本的示例数据
            return self.generate_fallback_data(business_object)

    def generate_fallback_data(self, business_object: str) -> List[Dict]:
        """
        生成备用数据，当主要生成方法失败时使用

        Args:
            business_object: 业务对象名称

        Returns:
            备用训练数据列表
        """
        print(f"  使用备用方案为 {business_object} 生成数据...")

        mapping = self.business_object_mapping.get(business_object, {})
        intent = mapping.get('intent', '查询')
        obj = mapping.get('object', '未知对象')

        # 根据业务对象类型生成基本示例
        fallback_examples = []

        if business_object == 'searchCargo':
            fallback_examples = [
                "查询货单信息审核单",
                "查看货单结算审核单",
                "帮我查下货单审核单",
                "列出货单信息",
                "查询货单结算单"
            ]
        elif business_object == 'searchContract':
            fallback_examples = [
                "查询合同信息审核单",
                "查看合同审核单",
                "帮我查下合同信息",
                "列出合同审核单",
                "查询合同信息"
            ]
        elif business_object == 'searchPo':
            fallback_examples = [
                "查询订单预结算审核单",
                "查看订单审核单",
                "帮我查下订单预审单",
                "列出订单预结算审核单",
                "查询订单信息"
            ]
        elif business_object == 'searchStaff':
            fallback_examples = [
                "查询人员安排",
                "查看项目人员",
                "帮我查下人员分配",
                "列出人员安排",
                "查询员工安排"
            ]
        elif business_object == 'updateCargo':
            fallback_examples = [
                "更新货单信息审核单",
                "修改货单审核单",
                "审核通过货单",
                "导出货单结算单",
                "处理货单信息"
            ]
        elif business_object == 'updateStaff':
            fallback_examples = [
                "安排项目人员",
                "更新人员安排",
                "添加项目人员",
                "修改人员分配",
                "调整人员安排"
            ]

        training_data = []
        for example in fallback_examples:
            training_item = {
                "messages": [
                    {
                        "role": "user",
                        "content": example
                    },
                    {
                        "role": "assistant",
                        "content": f"业务意图[{intent}]业务对象[{obj}]"
                    }
                ]
            }
            training_data.append(training_item)

        print(f"  ✓ 备用方案为 {business_object} 生成了 {len(training_data)} 条数据")
        return training_data

    def generate_all_training_data(self) -> List[Dict]:
        """
        生成所有业务对象的训练数据

        Returns:
            完整的训练数据列表
        """
        print("开始生成完整训练数据集...")
        print("=" * 50)

        all_training_data = []
        statistics = {}

        # 按顺序生成，确保每个业务对象都有合理的数据量
        target_per_object = 333  # 每个业务对象目标333条，总计约2000条

        for business_object in self.business_object_mapping.keys():
            print(f"\n处理业务对象: {business_object}")
            data = self.generate_business_object_data(business_object)

            # 如果数据太多，截取到目标数量
            if len(data) > target_per_object:
                data = data[:target_per_object]
                print(f"  数据量过多，截取到 {target_per_object} 条")

            # 如果数据太少，使用备用方案补充
            if len(data) < 50:  # 如果少于50条，补充一些基础数据
                additional_data = self.generate_fallback_data(business_object)
                data.extend(additional_data)
                print(f"  数据量不足，补充到 {len(data)} 条")

            all_training_data.extend(data)
            statistics[business_object] = len(data)

        print("=" * 50)
        print("数据生成完成！")
        print(f"总计生成: {len(all_training_data)} 条训练数据")
        print("\n各业务对象数据分布:")
        for obj, count in statistics.items():
            desc = self.business_object_mapping[obj]['description']
            print(f"  {obj} ({desc}): {count} 条")

        return all_training_data, statistics
    
    def save_training_data(self, training_data: List[Dict], statistics: Dict, output_file: str = "qwen_training_data.json"):
        """
        保存训练数据到文件
        
        Args:
            training_data: 训练数据列表
            statistics: 统计信息
            output_file: 输出文件名
        """
        # 随机打乱数据顺序
        random.shuffle(training_data)
        
        # 保存训练数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = output_file.replace('.json', '_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_samples': len(training_data),
                'business_object_distribution': statistics,
                'business_object_mapping': self.business_object_mapping
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 训练数据已保存到: {output_file}")
        print(f"✓ 统计信息已保存到: {stats_file}")
        
        # 显示数据样本
        print(f"\n数据样本预览 (前3条):")
        for i, sample in enumerate(training_data[:3]):
            print(f"\n样本 {i+1}:")
            print(f"  用户: {sample['messages'][0]['content']}")
            print(f"  助手: {sample['messages'][1]['content']}")


def main():
    """主函数"""
    print("🐾 Claude 4.0 sonnet 训练数据生成器")
    print("专为qwen2.5-3b业务意图识别模型设计")
    print("=" * 60)
    
    # 创建生成器
    generator = TrainingDataGenerator()
    
    # 生成训练数据
    training_data, statistics = generator.generate_all_training_data()
    
    # 保存数据
    generator.save_training_data(training_data, statistics)
    
    print("\n🎉 训练数据生成完成！")
    print("数据已准备好用于qwen2.5-3b模型训练")


if __name__ == "__main__":
    main()
