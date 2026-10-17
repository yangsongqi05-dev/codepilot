import os
import platform

print('cwd  =', os.getcwd())
print('node =', platform.node())
print('能看到 E 盘吗 =', os.path.exists('E:/python'))