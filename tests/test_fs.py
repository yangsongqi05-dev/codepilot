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


















