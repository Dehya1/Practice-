"""
线程安全
一个进程中可以有多个线程，且线程共享所有进程中的资源
多个线程同时去操作一个‘东西’，可能会存在数据混乱的情况
"""

# import threading
# lock_object = threading.RLock()  # 设置一把锁
#
# loop = 10000000
# number = 0
#
# def _add(count):
#     lock_object.acquire()  # 加锁（申请锁）--申请到锁运行，然后释放，另一个线程收到锁才会运行
#     global number
#     for i in range(count):
#         number += 1
#     lock_object.release()  # 释放锁
#
# def _sub(count):
#     lock_object.acquire()  # 加锁
#     global number
#     for i in range(count):
#         number -= 1
#     lock_object.release()  # 释放锁
#
# t1 = threading.Thread(target=_add,args=(loop,))
# t2 = threading.Thread(target=_sub,args=(loop,))
#
# t1.start()
# t2.start()
#
# t1.join()  # t1线程执行完毕，才能继续往后走
# t2.join()  # t2线程执行完毕，才能继续往后走
#
# print(number)

import threading

lock_object = threading.RLock()

num = 0

def task():
    with lock_object:  # 这样也可以，基于上下文的管理，在内部自动执行枷锁和释放锁
        global num
        # lock_object.acquire()
        for i in range(1000000):
            num += 1
    print(num)
    # lock_object.release()

for i in range(3):  # 按理说应该是打印出100W\200W\300W,实际上并没有，加个锁就好了
    t = threading.Thread(target=task)
    t.start()













