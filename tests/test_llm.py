from agent.llm import parse_action


def test_纯JSON():
    obj, err = parse_action('{"thought": "看看", "action": "list_files", "args": {"rel": "."}}')
    assert err is None
    assert obj['action'] == 'list_files'


def test_带json围栏也能解析():
    text = '```json\n{"thought": "看看", "action": "read_file", "args": {"rel": "a.py"}}\n```'
    obj, err = parse_action(text)
    assert err is None
    assert obj['action'] == 'read_file'


def test_前后有废话也能解析():
    text = '好的，我先看一下：\n{"thought": "看看", "action": "list_files", "args": {}}\n以上。'
    obj, err = parse_action(text)
    assert err is None
    assert obj['action'] == 'list_files'


def test_final也能识别():
    obj, err = parse_action('{"thought": "完成", "final": "改好了"}')
    assert err is None
    assert obj['final'] == '改好了'


def test_不是JSON会返回错误说明():
    obj, err = parse_action('我不知道该怎么做')
    assert obj is None
    assert '不是合法 JSON' in err


def test_缺action和final会返回错误说明():
    obj, err = parse_action('{"thought": "完成了", "result": "ok"}')
    assert obj is None
    assert 'action' in err


def test_顶层是列表也算错():
    obj, err = parse_action('[1, 2, 3]')
    assert obj is None