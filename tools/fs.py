import os
from config import WORKSPACE
TEXT_EXTS = ('.py', '.txt', '.md', '.json', '.yml', '.yaml', '.toml', '.cfg', '.ini', '.html', '.css', '.js')
SKIP_DIRS = {'.git', '.venv', '__pycache__', 'node_modules', '.idea'}
def safe_path(rel):
    root = os.path.join(WORKSPACE)
    full =os.path.abspath(os.path.join(root,rel))
    if full != root and not  full.startswith(root + os.sep):
        raise ValueError(f'路径越界，拒绝访问：{rel}')
    return full
def list_files(rel='.'):
    path = safe_path(rel)
    if not os.path.isdir(path):
        return f'不是目录：{rel}'
    names=[]
    for name in sorted(os.listdir(path)):
        mark = '/' if os.path.isdir(os.path.join(path, name)) else ''
        names.append(name+mark)
    return  '\n'.join(names) if names else '空目录'
def read_file(rel):
    path = safe_path(rel)
    if not os.path.isfile(path):
        return f'文件不存在：{rel}'
    with open(path,encoding='utf_8') as f:
        return f.read()
# if __name__ == '__main__':
#     print(list_files('demo_project'))
#     print('---')
#     print(read_file('demo_project/calc.py'))
#     print('---')
#     print(read_file('demo_project/nope.py'))
#     print('---')
#     print(read_file('../../config.py'))


def write_file(rel, content):
    path = safe_path(rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,'w',encoding='utf_8') as f:
        f.write(content)
    return f'已写入{rel}({len(content)}字符)'
def edit_file(rel, old,new):
    path = safe_path(rel)
    if not os.path.isfile(path):
        return f'文件不存在:{rel}'
    with open(path,encoding='utf_8') as f:
        text = f.read()
    count = text.count(old)
    if count == 0:
        return f'没有找到要替换的内容，请先 read_file 确认原文:{rel}'
    if count > 1:
        return f'要替换的内容再文件里出现{count}次，请多带几行上下文让他唯一:{rel}'
    with open(path,'w',encoding='utf_8') as f:
        f.write(text.replace(old,new))
    return f'已修改{rel}'

# if __name__ == '__main__':
#     print(write_file('demo_project/tmp.txt', 'hello\nworld\n'))
#     print('---')
#     print(edit_file('demo_project/tmp.txt', 'world', 'CodePilot'))
#     print('---')
#     print(edit_file('demo_project/tmp.txt', 'l', 'X'))
#     print('---')
#     print(edit_file('demo_project/tmp.txt', 'zzz', 'X'))
#     print('---')
#     print(read_file('demo_project/tmp.txt'))

def search_code(keyword, rel='.',max_hit=40):
    path = safe_path(rel)
    hits = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(TEXT_EXTS):
                continue
            full = os.path.join(dirpath, fn)
            try:
                with open(full,encoding='utf_8') as f:
                    for i , line in enumerate(f,1):
                        if keyword in line:
                            short = os.path.relpath(full,WORKSPACE)
                            hits.append(f'{short}:{i}:{line.strip()[:120]}')
                            if len(hits) >= max_hit:
                                return '\n'.join(hits)+f'已截断，超过{max_hit}'
            except (UnicodeDecodeError, OSError) :
                continue
    return '\n'.join(hits) if hits else f'没有找到：{keyword}'

if __name__ == '__main__':
    print(search_code('average'))
    print('---')
    print(search_code('zzzzz'))
    print('---')
    print(search_code('import'))



















