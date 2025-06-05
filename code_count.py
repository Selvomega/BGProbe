import os

def count_code_lines_in_file(filepath):
    count = 0
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        in_multiline_comment = False
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue  # 跳过空行
            if stripped.startswith('#'):
                continue  # 跳过单行注释
            if stripped.startswith('"""') or stripped.startswith("'''"):
                # 处理多行注释开始
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    continue  # 同一行开始和结束，跳过
                in_multiline_comment = not in_multiline_comment
                continue
            if in_multiline_comment:
                continue
            count += 1
    return count

def count_total_code_lines(root='.'):
    total = 0
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                total += count_code_lines_in_file(filepath)
    return total

if __name__ == '__main__':
    total_lines = count_total_code_lines('.')
    print(f'有效 Python 代码行数：{total_lines}')
