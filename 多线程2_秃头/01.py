"""
多线程：
一个工厂，至少有一个车间，一个车间中至少有一个工人，最终是工人在工作
一个程序，至少有一个进程，一个进程中至少有一个线程，最终是线程在工作

多进程：
一个工厂，创建三个车间，每个车间一个工人（共三人），并行处理任务
一个程序，创建三个进程，每个进程一个线程（共三人），并行处理任务

import multiprocessing
t = multiprocessing.Process(target=task)  # 创建一个进程（创建一个进程后，会在进程中还会创建一个线程，因为线程才是CPU调度的最小单元）
t.start()
"""

import multiprocessing

def _add():
    number = 0
    for i in range(100000000):
        number += 1
    print(number)
if __name__ == '__main__':

    t = multiprocessing.Process(target=_add)  # 创建一个线程
    t.start()  # 让线程开始工作
    t.join()   # 等待子线程执行完毕后再继续往下执行。有join，number是1亿，没有join，number不一定，反正不到1亿
    # time.sleep(5)  # 主线程运行到子线程这里，子线程在这段时间内算不完这个数，可以多给他点时间


"""
GIL锁：即全局解释器锁，让一个进程中同一时刻只能有一个线程可以被CPU调度
"""