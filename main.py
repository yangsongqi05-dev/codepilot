import sys
from config import WORKSPACE,MAX_STEPS
from agent.loop import run
def main():
    if len(sys.argv) < 2:
        print('用法：python main.py "你的任务"')
        return
    task = sys.argv[1]
    print("="*55)
    print('CodePilot启动')
    print('任务:',task)
    print('工作区:',WORKSPACE)
    print('最大轮数:',MAX_STEPS)
    print('='*55)
    answer = run(task)
    print('=' * 55)
    print('最终答复：',answer)
if __name__ == '__main__':
    main()