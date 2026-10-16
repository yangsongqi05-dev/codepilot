import os
import subprocess
import sys
import shutil

from config import WORKSPACE
from tools.fs import safe_path
PY=sys.executable
def _run(cmd,cwd,timeout):
    try:
        r =subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=timeout,encoding='utf-8',errors='replace')
    except subprocess.TimeoutExpired:
        return f'超时（超过{timeout}秒），已强制结束'
    out =(r.stdout or '')+(r.stderr or '')
    return f'退出码{r.returncode}\n{out.strip()[:2000]}'
def run_python(rel,timeout=30):
    path = safe_path(rel)
    if not os.path.isfile(path):
        return f'文件不存在：{rel}'
    return _run([PY,path],cwd=os.path.dirname(path),timeout=timeout)
def run_tests(rel='demo_project',timeout=60):
    path = safe_path(rel)
    if not os.path.isdir(path):
        return f'目录不存在：{rel}'
    return _run([PY,'-m','pytest','-q'],cwd=path,timeout=timeout)


# if __name__ == '__main__':
#     print(run_python('demo_project/calc.py'))
#     print('---')
#     print(run_python('demo_project/nope.py'))
#     print('---')
#     print(run_tests('demo_project'))

def _find_git():
    found = shutil.which('git')
    if found:
        return found
    for p in (r'C:\Program Files\Git\cmd\git.exe,'
              r'C:\Program Files\Git\cmd\git.exe'):
        if os.path.isfile(p):
            return p
def git_diff():
    git = _find_git()
    if git is None:
        return '找不到 git 跳过'
    a=_run([git,'--no-pager','status','--short','.'],cwd=WORKSPACE,timeout=15)
    b=_run([git,'--no-pager','diff','.'],cwd=WORKSPACE,timeout=15)
    return a+'\n----具体改动----\n'+b


if __name__ == '__main__':
    print(git_diff())





















