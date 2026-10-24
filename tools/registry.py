
from tools.fs import list_files, read_file, write_file, edit_file, search_code
from tools.shell import run_python, run_tests, git_diff
from tools.code_index import search_codebase
TOOLS={
    'list_file':{
        'fn':list_files,
        'desc':'列出工作区内某个目录下的文件名',
        'params':{'rel':'(可选)目录相对路径，默认 "." 是工作区根目录'}
    },
    'read_file': {
        'fn': read_file,
        'desc': '读取工作区里的一个内容',
        'params': {'rel': '(必填)文件相对路径'}
    },
    'write_file': {
        'fn': write_file,
        'desc': '把内容写入一个文件（会覆盖原文；测试和配置文件会被拒绝）',
        'params': {'rel': '（必填）文件相对路径',
                   'content':'(必填)要写入的完整内容'}
    },
    'edit_file': {
        'fn': edit_file,
        'desc': '把文件里唯一出现的一段文本换成新文本（测试和配置文件会被拒绝）',
        'params': {'rel': '(必填)文件相对路径',
                   'old':'(必填)要被替换的原文，必须在文件里唯一出现',
                   'new':'(必填)替换成什么'}
    },
    'search_code': {
        'fn': search_code,
        'desc': '在工作区里按照关键词搜代码，返回 文件：行号：内容',
        'params': {'rel': '(可选)在哪个目录下搜，默认"."',
                   'keyword':'(必填)要搜的关键词'}
    },
    'run_python': {
        'fn': run_python,
        'desc': '跑工作区里的Python文件，返回输出和退出码',
        'params': {'rel': '(必填)文件相对路径'}
    },
    'run_tests': {
        'fn': run_tests,
        'desc': '在工作区某目录下跑pytest',
        'params': {'rel': '(可选)目录相对路径，默认"demo_project"'}
    },
    'git_diff': {
        'fn': git_diff,
        'desc': '看看工作区里改了什么（哪些文件动了+具体改动）',
        'params': {}
    },
    'search_codebase': {
        'fn': search_codebase,
        'desc': '按语义搜索代码库：描述你想找的代码是干什么的，它返回最相关的几段代码',
        'params': {'query': '(必填) 用一句话描述你要找什么，比如"计算平均值的逻辑"',
                   'k': '(可选) 返回几段，默认 3'},
    },
}
def tools_prompt():
    lines=[]
    for name,t in TOOLS.items():
        lines.append(f'- {name}:{t["desc"]}')
        for p,d in t['params'].items():
            lines.append(f'  {p}:{d}')
    return '\n'.join(lines)
from langsmith import traceable          # ← 新加
@traceable(run_type="tool")
def call_tool(name,args):
    if name not in TOOLS:
        return f'没有这个工具：{name}。可用的是：{",".join(TOOLS)}'
    try:
        return TOOLS[name]['fn'](**args)
    except TypeError as e:
        return f'参数不对：{e}'
    except Exception as e:
        return f'工具执行出错：{type(e).__name__}:{e}'

if __name__ == '__main__':
    print(tools_prompt())
    print('====')
    print(call_tool('search_codebase', {'query': '怎么把一堆数加起来然后除以它们的个数'}))




