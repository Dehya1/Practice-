"""
两种锁：
同步锁 -- Lock -- 不支持锁的嵌套
递归锁 -- RLock -- 支持锁的嵌套
"""
# 同步锁
import threading
num = 0
lock_object = threading.Lock()

def task():
    print('开始')
    lock_object.acquire()  # 第1个抵达的线程进入并上锁，其他线程在此等待
    global num
    for i in range(1000000):
        num += 1
    lock_object.release()  # 线程出去，并解开锁，其他线程就可以进入并执行了
    print(num)

for i in range(2):
    t = threading.Thread(target=task)
    t.start()
























