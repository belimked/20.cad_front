#!/usr/bin/env python

def fix_indentation():
    # 修复路径
    file_path = 'test/service/test_qwen_service.py'
    
    # 读取原文件内容
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # 修复的内容
    fixed_lines = []
    
    # 标记是否在需要修复的函数内
    in_verify_qwen = False
    in_verify_original = False
    
    for i, line in enumerate(lines):
        # 检测是否进入了verify_qwen_file函数
        if 'def verify_qwen_file(' in line:
            in_verify_qwen = True
            fixed_lines.append(line)
            continue
        
        # 检测是否进入了verify_original_file函数
        elif 'def verify_original_file(' in line:
            in_verify_qwen = False
            in_verify_original = True
            fixed_lines.append(line)
            continue
            
        # 检测是否离开了verify_original_file函数
        elif 'def test_generate_qwen_data_for_searchStaff(' in line:
            in_verify_original = False
            fixed_lines.append(line)
            continue
        
        # 修复verify_qwen_file函数中的缩进
        if in_verify_qwen:
            # 修复特定行的缩进
            if 'if os.path.exists(file_path):' in line:
                fixed_lines.append('    if os.path.exists(file_path):\n')
            elif '        print(f"✓ 千问文件生成成功！")' in line:
                fixed_lines.append('        print(f"✓ 千问文件生成成功！")\n')
            elif '        # 验证文件内容' in line:
                fixed_lines.append('        # 验证文件内容\n')
            elif '    with open(file_path, ' in line or '        with open(file_path, ' in line:
                fixed_lines.append('        with open(file_path, \'r\', encoding=\'utf-8\') as f:\n')
            elif '            # 读取JSON文件内容' in line or '                # 读取JSON文件内容' in line:
                fixed_lines.append('            # 读取JSON文件内容\n')
            else:
                # 确保其他行也有正确的缩进
                if line.strip() and line.startswith('                '):
                    fixed_line = '            ' + line.lstrip()
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
        
        # 修复verify_original_file函数中的缩进
        elif in_verify_original:
            # 修复特定行的缩进
            if 'if os.path.exists(file_path):' in line:
                fixed_lines.append('    if os.path.exists(file_path):\n')
            elif '        print(f"✓ 原始数据文件生成成功！")' in line:
                fixed_lines.append('        print(f"✓ 原始数据文件生成成功！")\n')
            elif '        # 验证文件内容' in line:
                fixed_lines.append('        # 验证文件内容\n')
            elif '    with open(file_path, ' in line or '        with open(file_path, ' in line:
                fixed_lines.append('        with open(file_path, \'r\', encoding=\'utf-8\') as f:\n')
            elif '            # 读取JSON文件内容' in line or '                # 读取JSON文件内容' in line:
                fixed_lines.append('            # 读取JSON文件内容\n')
            elif 'print(f"业务类型: {business_object}")' in line and not line.startswith('                '):
                fixed_lines.append('                print(f"业务类型: {business_object}")\n')
            else:
                # 确保其他行也有正确的缩进
                if line.strip() and line.startswith('                '):
                    fixed_line = '            ' + line.lstrip()
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
        
        # 其他函数不修改
        else:
            fixed_lines.append(line)
    
    # 写回文件
    with open(file_path, 'w') as file:
        file.writelines(fixed_lines)
    
    print(f"文件 {file_path} 的缩进已修复")

if __name__ == '__main__':
    fix_indentation() 