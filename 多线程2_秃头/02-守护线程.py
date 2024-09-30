import threading
import time
"""
t.daemon = 布尔值，守护线程（必须放在start之前）
t.daemon = True ，设置守护线程，主线程执行完毕后，子线程也自动关闭。主线程不等待子线程
t.daemon = False ，设置非守护线程，主线程等待子线程，子线程执行完毕后，主线程才结束（默认的）。主线程等待子线程
"""


def task(arg):
    time.sleep(5)
    print('任务')

t = threading.Thread(target=task,args=(11,))
t.daemon = True
t.start()
print('END')















