import logging
from agent.llm import build_system_prompt,chat,parse_action
from config import MAX_STEPS
from tools.registry import call_tool
logger = logging.getLogger(__name__)
from langsmith import traceable
@traceable
def run(task):
    messages = [
        {'role':'system','content':build_system_prompt()},
        {'role':'user','content':f'任务：{task}\n你的根目录就是工作区'},
    ]
    for step in range(1,MAX_STEPS+1):
        text=chat(messages)
        messages.append({'role':'assistant','content':text})
        obj , err =parse_action(text)
        if err:
            logger.warning(f'[{step}] 解析失败：{err[:60]}')
            messages.append({'role':'assistant','content':
                             f'你上一条输出不是合法 JSON。原因{err}\n'
                             f'请你只输出一个 JSON对象，不要有其他任何文字。'})
            continue
        if 'final' in obj:
            logger.info(f'{step}完成')
            return obj['final']
        action = obj.get('action')
        args = obj.get('args') or {}
        if not isinstance(args,dict):
            args = {}
        logger.debug(f'本轮 messages 有 {len(messages)} 条')
        logger.info(f'[{step}]{obj.get("thought","")}')
        logger.info(f'    -> {action}({args})')
        result = call_tool(action,args)
        messages.append({'role':'user','content':
                         f'工具{action}的结果：\n{result}'})
    return f'达到最大轮数{MAX_STEPS}，任务没做完'









