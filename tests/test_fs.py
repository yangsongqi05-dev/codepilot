import os
import pytest
from config import WORKSPACE
from tools.fs import safe_path
import tools.fs
def test_正常路径放行():
    p = safe_path('demo_project/calc.py')
    assert os.path.isabs(p)
    assert p.startswith(WORKSPACE + os.sep)
def test_绕一圈还在工作区也放行():
    p = safe_path('demo_project/../demo_project/calc.py')
    assert p.startswith(WORKSPACE + os.sep)
def test_根目录本身放行():
    assert safe_path('.')==os.path.abspath(WORKSPACE)
def test_上级目录被拒绝():
    with pytest.raises(ValueError):
        safe_path('../config.py')
def test_读密钥文件被拒绝():
    with pytest.raises(ValueError):
        safe_path('../../api_key.txt.txt')
@pytest.mark.skipif(os.name != 'nt', reason='反斜杠只在 Windows 上是路径分隔符')
def test_反斜杠越界也被拒绝():
    with pytest.raises(ValueError):
        safe_path('..\\..\\config.py')

@pytest.fixture
def work(tmp_path,monkeypatch):
    monkeypatch.setattr(tools.fs,'WORKSPACE',str(tmp_path))
    (tmp_path / 'a.txt').write_text('第一行\n第二行\n第三行\n',encoding='utf_8')
    return tmp_path
def test_唯一匹配会被替换(work):
    r = tools.fs.edit_file('a.txt','第二行','改过了')
    assert '已修改' in r
    assert (work / 'a.txt').read_text(encoding='utf-8') == '第一行\n改过了\n第三行\n'
def test_找不到原文时文件不变(work):
    r = tools.fs.edit_file('a.txt', '不存在的文字', 'X')
    assert '没有找到' in r
    assert (work / 'a.txt').read_text(encoding='utf-8') == '第一行\n第二行\n第三行\n'
def test_出现多次时拒绝修改(work):
    r = tools.fs.edit_file('a.txt', '行', 'X')
    assert '出现' in r
    assert (work / 'a.txt').read_text(encoding='utf-8') == '第一行\n第二行\n第三行\n'
def test_文件不存在时返回提示(work):
    r = tools.fs.edit_file('nope.txt', 'a', 'b')
    assert '不存在' in r

def test_测试文件禁止写入和修改(work):
    target = work / 'demo_project' / 'test_calc.py'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('assert 1 == 1\n',encoding = 'utf-8 ')

    write_result = tools.fs.write_file(
        'demo_project/test_calc.py',
        '被篡改\n'
    )
    assert '受保护' in write_result
    assert target.read_text(encoding='utf_8') == 'assert 1 == 1\n'

    edit_result = tools.fs.edit_file(
        'demo_project/test_calc.py',
        '== 1',
        '== 2'
    )
    assert '受保护' in edit_result
    assert target.read_text(encoding='utf_8') == 'assert 1 == 1\n'

def test_业务源码仍然可以修改(work):
    target = work / 'demo_project' / 'calc.py'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('def add(a,b):\n return a - b\n', encoding='utf_8')
    result = tools.fs.edit_file(
        'demo_project/calc.py',
        'a - b',
        'a + b'
    )
    assert '已修改' in result
    assert target.read_text(encoding='utf_8') == (
    'def add(a,b):\n return a + b\n'
    )

def test_配置文件禁止写入(work):
    protected_files = [
        'demo_project/conftest.py',
        'pytest.ini',
        'requirements.txt',
        'Dockerfile',
        '.github/workflows/ci.yml',
    ]
    for rel in protected_files:
        target = work / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('原始内容\n',encoding='utf_8')

        result = tools.fs.write_file(rel,'被篡改\n')

        assert '受保护' in result
        assert target.read_text(encoding='utf_8') == '原始内容\n'

















