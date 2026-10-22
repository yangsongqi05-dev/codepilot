import logging
from agent.llm import build_system_prompt,chat,parse_action
from config import MAX_STEPS
from tools.registry import call_tool
logger = logging.getLogger(__name__)
from langsmith import traceable
@traceable
def run(task):
    verified = False
    final_retry = 0
    empty =0
    messages = [
        {'role':'system','content':build_system_prompt()},
        {'role':'user','content':f'任务：{task}\n你的根目录就是工作区'},
    ]
    for step in range(1,MAX_STEPS+1):
        text=chat(messages)
        if not text or not text.strip():
            empty += 1
            logger.warning(f'[{step}模型返回为空](连续{empty}次)')
            if empty >= 2:
                logger.warning('模型连续无输出，按未验证收工')
                return '【未验证】模型停止输出，任务未确认完成。'
        empty = 0
        messages.append({'role':'assistant','content':text})
        obj , err =parse_action(text)
        if err:
            logger.warning(f'[{step}] 解析失败：{err[:60]}')
            messages.append({'role':'user','content':
                             f'你上一条输出不是合法 JSON。原因{err}\n'
                             f'请你只输出一个 JSON对象，不要有其他任何文字。'})
            continue
        if 'final' in obj:
            if not verified and final_retry == 0:
                final_retry += 1
                logger.warning(f'[{step}]想收工但没验证过，打回')
                messages.append({'role': 'user', 'content':
                    '再试一次。如果要继续，就照这个格式输出：'
                    '{"thought":"...","action":"run_tests","args":{"rel":"demo_project"}} ；'
                    '如果确实跑不起来，就输出 final 并在 final 里写明原因。'})
                continue
            logger.info(f'[{step}]完成(verified={verified})')
            return obj['final']
        action = obj.get('action')
        args = obj.get('args') or {}
        if not isinstance(args,dict):
            args = {}
        logger.debug(f'本轮 messages 有 {len(messages)} 条')
        logger.info(f'[{step}]{obj.get("thought","")}')
        logger.info(f'    -> {action}({args})')
        result = call_tool(action,args)
        if action =='run_tests' and '退出码0' in result:
            verified = True
        messages.append({'role':'user','content':
                         f'工具{action}的结果：\n{result}'})
    return f'达到最大轮数{MAX_STEPS}，任务没做完'









