"""
测试材料提取功能和配置实时生效

验证内容：
1. 数据库配置是否正确存在
2. DictService 配置查询方法是否正常
3. 材料提取正则匹配是否正确
4. 配置修改后立即生效

Author: CAD Auto Processor Team
Date: 2025-11-05
"""

import sys
from pathlib import Path
import re
import json

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.dict_service import DictionaryService
from src.utils.database import db_session
from src.models.dictionary import Dictionary


def test_database_configs():
    """测试 1: 验证数据库配置是否正确存在"""
    print("=" * 70)
    print("测试 1: 验证数据库配置")
    print("=" * 70)

    try:
        with db_session() as session:
            configs = session.query(Dictionary).filter_by(
                dict_type='extraction',
                is_active=True
            ).order_by(Dictionary.sort_order).all()

            print(f"\n✅ 找到 {len(configs)} 条配置:\n")

            for cfg in configs:
                print(f"  [{cfg.dict_key}]")
                print(f"    标签: {cfg.dict_label}")
                print(f"    描述: {cfg.dict_description}")

                # 解析并显示值
                try:
                    value = json.loads(cfg.dict_value)
                    if isinstance(value, list):
                        print(f"    值（数组，{len(value)} 项）: {value[:5]}..." if len(value) > 5 else f"    值: {value}")
                    elif isinstance(value, dict):
                        print(f"    值（对象）: {value}")
                except json.JSONDecodeError:
                    print(f"    值（原始）: {cfg.dict_value[:100]}...")
                print()

            expected_keys = ['extraction_excluded_keywords', 'extraction_material_keywords', 'extraction_rules']
            actual_keys = [cfg.dict_key for cfg in configs]

            if set(expected_keys) == set(actual_keys):
                print("✅ 所有必需配置已存在")
                return True
            else:
                missing = set(expected_keys) - set(actual_keys)
                print(f"❌ 缺少配置: {missing}")
                return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dict_service_methods():
    """测试 2: 验证 DictService 配置查询方法"""
    print("\n" + "=" * 70)
    print("测试 2: DictService 配置查询方法")
    print("=" * 70)

    try:
        # 测试 get_config_list()
        print("\n📋 测试 get_config_list():")

        excluded_keywords = DictionaryService.get_config_list('extraction_excluded_keywords')
        print(f"  ✅ extraction_excluded_keywords: {len(excluded_keywords)} 项")
        print(f"     前5项: {excluded_keywords[:5]}")

        material_keywords = DictionaryService.get_config_list('extraction_material_keywords')
        print(f"  ✅ extraction_material_keywords: {len(material_keywords)} 项")
        print(f"     值: {material_keywords}")

        # 测试 get_config_dict()
        print("\n📊 测试 get_config_dict():")

        extraction_rules = DictionaryService.get_config_dict('extraction_rules')
        print(f"  ✅ extraction_rules: {extraction_rules}")

        # 测试不存在的配置（应返回默认值）
        print("\n🔍 测试不存在的配置:")

        not_exist_list = DictionaryService.get_config_list('not_exist_key', default=['default1', 'default2'])
        print(f"  ✅ 不存在的列表配置返回默认值: {not_exist_list}")

        not_exist_dict = DictionaryService.get_config_dict('not_exist_key', default={'key': 'value'})
        print(f"  ✅ 不存在的字典配置返回默认值: {not_exist_dict}")

        print("\n✅ DictService 方法测试通过")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_material_extraction_regex():
    """测试 3: 验证材料提取正则匹配"""
    print("\n" + "=" * 70)
    print("测试 3: 材料提取正则匹配")
    print("=" * 70)

    # 获取材料关键字
    material_keywords = DictionaryService.get_config_list(
        'extraction_material_keywords',
        default=['材料:', 'Material:', 'material:']
    )

    print(f"\n📋 使用关键字: {material_keywords}")

    # 测试用例
    test_cases = [
        {
            'html': '<td rowspan="3">材料: 80x80钢块(Q235B)</td>',
            'expected': '材料: 80x80钢块(Q235B)'
        },
        {
            'html': '<td colspan="5">材料: 见列表</td>',
            'expected': '材料: 见列表'
        },
        {
            'html': '<td>Material: Steel Q235B</td>',
            'expected': 'Material: Steel Q235B'
        },
        {
            'html': '<td rowspan="2" colspan="3">材料: 不锈钢 304</td>',
            'expected': '材料: 不锈钢 304'
        },
        {
            'html': '<td>无关内容</td><td>材料: 铝合金</td><td>其他</td>',
            'expected': '材料: 铝合金'
        }
    ]

    print("\n🧪 运行测试用例:\n")

    passed = 0
    failed = 0

    for i, case in enumerate(test_cases, 1):
        html = case['html']
        expected = case['expected']

        # 模拟 _extract_material_info 的逻辑
        result = None
        for keyword in material_keywords:
            pattern = rf'<td[^>]*>([^<]*{re.escape(keyword)}[^<]*)</td>'
            matches = re.findall(pattern, html, re.IGNORECASE)

            if matches:
                result = matches[0].strip()
                result = re.sub(r'\s+', ' ', result)
                break

        # 验证结果
        if result == expected:
            print(f"  ✅ 测试 {i}: 通过")
            print(f"     输入: {html[:60]}...")
            print(f"     输出: {result}")
            passed += 1
        else:
            print(f"  ❌ 测试 {i}: 失败")
            print(f"     输入: {html[:60]}...")
            print(f"     期望: {expected}")
            print(f"     实际: {result}")
            failed += 1
        print()

    print(f"📊 测试结果: {passed}/{len(test_cases)} 通过, {failed}/{len(test_cases)} 失败")

    return failed == 0


def test_config_realtime_update():
    """测试 4: 验证配置修改后立即生效"""
    print("\n" + "=" * 70)
    print("测试 4: 配置实时生效")
    print("=" * 70)

    try:
        # 1. 读取当前配置
        print("\n📖 读取当前配置:")
        keywords_before = DictionaryService.get_config_list('extraction_material_keywords')
        print(f"  当前材料关键字: {keywords_before}")

        # 2. 添加测试关键字
        print("\n✏️  添加测试关键字 '材质:' 到数据库:")
        with db_session() as session:
            config_item = session.query(Dictionary).filter_by(
                dict_type='extraction',
                dict_key='extraction_material_keywords'
            ).first()

            if config_item:
                current_value = json.loads(config_item.dict_value)
                test_keyword = '材质:'

                if test_keyword not in current_value:
                    current_value.append(test_keyword)
                    config_item.dict_value = json.dumps(current_value, ensure_ascii=False)
                    session.commit()
                    print(f"  ✅ 已添加测试关键字: {test_keyword}")
                else:
                    print(f"  ℹ️  测试关键字已存在: {test_keyword}")

        # 3. 立即读取验证（无缓存）
        print("\n🔍 立即读取验证:")
        keywords_after = DictionaryService.get_config_list('extraction_material_keywords')
        print(f"  更新后材料关键字: {keywords_after}")

        if '材质:' in keywords_after:
            print("  ✅ 配置实时生效成功！")

            # 4. 恢复原始配置
            print("\n🔄 恢复原始配置:")
            with db_session() as session:
                config_item = session.query(Dictionary).filter_by(
                    dict_type='extraction',
                    dict_key='extraction_material_keywords'
                ).first()

                if config_item:
                    config_item.dict_value = json.dumps(keywords_before, ensure_ascii=False)
                    session.commit()
                    print(f"  ✅ 已恢复为: {keywords_before}")

            # 5. 验证恢复
            keywords_restored = DictionaryService.get_config_list('extraction_material_keywords')
            if keywords_restored == keywords_before:
                print("  ✅ 配置恢复成功")
                return True
            else:
                print(f"  ⚠️  配置恢复不完全: {keywords_restored}")
                return False
        else:
            print("  ❌ 配置未立即生效")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n")
    print("🧪" * 35)
    print("材料提取功能测试套件")
    print("🧪" * 35)
    print()

    results = []

    # 测试 1: 数据库配置
    results.append(("数据库配置验证", test_database_configs()))

    # 测试 2: DictService 方法
    results.append(("DictService 方法", test_dict_service_methods()))

    # 测试 3: 材料提取正则
    results.append(("材料提取正则", test_material_extraction_regex()))

    # 测试 4: 配置实时生效
    results.append(("配置实时生效", test_config_realtime_update()))

    # 汇总结果
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    print()

    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status} - {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print()
    print(f"📊 总计: {total_passed}/{total_tests} 测试通过")
    print()

    if total_passed == total_tests:
        print("🎉 所有测试通过！材料提取功能工作正常。")
        print()
        return True
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        print()
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
