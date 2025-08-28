#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时脚本：在 drawings.json 的 drawname 字段中随机混入特殊字符
支持的字符：[（$#(.)]
可以插入单个或多个字符
"""

import json
import random
import sys
import os

def random_inject_chars(text, chars_pool="[（$#(.)]", min_count=1, max_count=3):
    """
    在文本中随机位置插入特殊字符
    
    Args:
        text: 原始文本
        chars_pool: 可选择的字符池
        min_count: 最少插入字符数
        max_count: 最多插入字符数
    
    Returns:
        修改后的文本
    """
    if not text:
        return text
    
    # 随机决定插入多少个字符
    insert_count = random.randint(min_count, max_count)
    
    # 将文本转换为列表以便插入
    text_list = list(text)
    
    for _ in range(insert_count):
        # 随机选择一个字符
        char_to_insert = random.choice(chars_pool)
        
        # 随机选择插入位置（可以在任意位置，包括开头和结尾）
        insert_pos = random.randint(0, len(text_list))
        
        # 插入字符
        text_list.insert(insert_pos, char_to_insert)
    
    return ''.join(text_list)

def process_drawings_json(input_file, output_file=None, probability=0.8):
    """
    处理 drawings.json 文件
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径（如果为None，则覆盖原文件）
        probability: 每个条目被修改的概率（0.0-1.0）
    """
    try:
        # 读取原始文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"读取到 {len(data)} 条记录")
        
        # 统计修改数量
        modified_count = 0
        
        # 处理每个条目
        for item in data:
            if 'drawname' in item:
                # 根据概率决定是否修改这个条目
                if random.random() < probability:
                    original_name = item['drawname']
                    # 随机混入字符
                    item['drawname'] = random_inject_chars(
                        original_name,
                        chars_pool="[（$#(.)]",
                        min_count=1,
                        max_count=random.randint(1, 4)  # 随机决定最大插入数量
                    )
                    modified_count += 1
                    print(f"ID {item.get('drawid', '?')}: {original_name} -> {item['drawname']}")
        
        # 保存文件
        output_path = output_file if output_file else input_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n处理完成！")
        print(f"修改了 {modified_count} 条记录")
        print(f"文件已保存到: {output_path}")
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误：{input_file} 不是有效的JSON文件")
        sys.exit(1)
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

def main():
    """主函数"""
    print("=== drawings.json 随机字符注入工具 ===")
    print("支持的字符：[（$#(.)]")
    print()
    
    # 默认文件路径
    default_file = "src/dict/drawings.json"
    
    # 检查文件是否存在
    if not os.path.exists(default_file):
        print(f"错误：找不到文件 {default_file}")
        print("请确保在正确的目录下运行此脚本")
        sys.exit(1)
    
    # 询问用户参数
    try:
        print(f"目标文件: {default_file}")
        
        # 修改概率
        prob_input = input("请输入修改概率 (0.0-1.0, 默认0.8): ").strip()
        probability = float(prob_input) if prob_input else 0.8
        probability = max(0.0, min(1.0, probability))  # 限制在0-1之间
        
        # 是否创建备份
        backup_input = input("是否创建备份文件? (y/N): ").strip().lower()
        create_backup = backup_input in ['y', 'yes', '是']
        
        if create_backup:
            backup_file = f"{default_file}.backup"
            import shutil
            shutil.copy2(default_file, backup_file)
            print(f"备份文件已创建: {backup_file}")
        
        print(f"\n开始处理，修改概率: {probability:.1%}")
        print("=" * 50)
        
        # 处理文件
        process_drawings_json(default_file, probability=probability)
        
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except ValueError:
        print("错误：请输入有效的数字")
        sys.exit(1)

if __name__ == "__main__":
    main()
