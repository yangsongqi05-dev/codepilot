import cmd
import os
import subprocess
import sys
import shutil
from dataclasses import replace

from pygments.lexer import words

from config import WORKSPACE, DOCKER_IMAGE
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
    rel2 = rel.replace('\\','/')
    return _in_container(['python',os.path.basename(rel2)],
                         workdir=os.path.dirname(rel2),timeout=timeout)

def run_tests(rel='demo_project',timeout=120):
    path = safe_path(rel)
    if not os.path.isdir(path):
        return f'目录不存在：{rel}'
    return _in_container(['python','-m','pytest','-q'],workdir=rel,timeout=timeout)

def _find_docker():
    found = shutil.which('docker')
    if found:
        return found
    p = r'C:\Program Files\Docker\Docker\resources\bin\docker.exe'r'C:\Program Files\Docker\Docker\resources\bin\docker.exe'
    if os.path.isfile(p):
        return p
    return None

def  _in_container(cmd,workdir='.',timeout=60):
    docker = _find_docker()
    if docker  is None:
        return '找不到docker命令，请确认 Docker Dsektop 在运行'
    host = WORKSPACE.replace('\\','/')
    sub = workdir.replace('\\','/').strip('/')
    work = '/work' if sub in ('','.') else f'/work/{sub}'
    full = [docker,'run','--rm',
            '-v',f'{host}:/work',
            '-w',work,
            DOCKER_IMAGE,
            'timeout',str(timeout)] + cmd
    return _run(full,cwd=WORKSPACE,timeout=timeout + 30)


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
    for p in (r'C:\Program Files\Git\cmd\git.exe',
              r'C:\Program Files (x86)\Git\cmd\git.exe'):
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
    print(run_python('demo_project/probe.py'))
    print('---')
    print(run_tests('demo_project'))
if __name__ == '__main__':
    print(run_python('demo_project/loop.py', timeout=10))




















