import json
import re

import requests
from config import CHAT_MODEL,CHAT_URL,get_headers
from tools.registry import tools_prompt
def build_system_prompt():
    return (
            '你是 CodePilot，一个会自己动手改代码的助手。\n'
            '你只能通过下面这些工具去操作文件，不能凭空猜文件内容。\n'
            '\n【可用工具】\n'
            + tools_prompt() + '\n'
            '\n【输出格式】\n'
            '每一轮你必须只输出一个 JSON 对象，不要输出任何其他文字。\n'
            '要继续干活就输出：\n'
            '{"thought": "一句话说明这一步要干什么", "action": "工具名", "args": {"参数名": "值"}}\n'
            '已经全部完成就输出：\n'
            '{"thought": "总结一下", "final": "给用户的最终答复"}\n'
            '\n【规则】\n'
            '- action 必须是工具清单里的名字，不许自己编。\n'
            '- args 必须是对象；不需要参数的工具就写 {}。\n'
            '- 一次只调一个工具。\n'
            '- 你输出的全部内容必须是一个 JSON 对象，不要用 ``` 代码块包起来。\n'
    )
def chat(messages):
    data={
        'model':CHAT_MODEL,
        'messages':messages,
        'temperature':0
    }
    resp =requests.post(CHAT_URL,json=data,headers=get_headers(),timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f'模型调用失败：{resp.status_code}{resp.text[:200]}')
    return resp.json()['choices'][0]['message']['content']




def parse_action(text):
    raw = text.strip()
    m = re.search(r'```(?:json)?\s*(.*?)```', raw,re.S)
    if m:
        raw = m.group(1).strip()
    else:
        i ,j = raw.find('{'),raw.rfind('}')
        if i!=-1 and j>1:
            raw = raw[i:j+1]
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        return None,f'不是合法 JSON（{e.msg}，位置 {e.pos}）；你原样输出的是：{text.strip()[:200]}'
    if not isinstance(obj,dict):
        return  None,f'顶层必须是 JSON 对象，你给的是 {type(obj).__name__}'
    if 'action' not in obj and 'final' not in obj:
        return  None,'缺少action或final字段'
    return obj,None















