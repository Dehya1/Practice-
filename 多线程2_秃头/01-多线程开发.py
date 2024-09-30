# 多线程开发
import threading
import time

# def task(arg):
#     pass

# # 创建一个Thread对象（线程），并封装线程被CPU调度时应该执行的任务和相关参数
# t = threading.Thread(target=task,args=('xxx',))
# # 线程准备就绪（等待CPU调度），代码继续往下执行
# t.start()
# print('主线程继续执行')  # 主线程执行完所有代码，不结束（等待子线程）

# 线程的常见方法
# t.start()，当前线程准备就绪（等待CPU调度，具体时间由CPU决定）
# t.join(),主线程等待当前子线程的任务执行完毕后再向下继续执行

# number = 0
# def _add():
#     global number
#     for i in range(100000000):
#         number += 1
# t = threading.Thread(target=_add)  # 创建一个线程
# t.start()  # 让线程开始工作
# # t.join()   # 等待子线程执行完毕后再继续往下执行。有join，number是1亿，没有join，number不一定，反正不到1亿
# # time.sleep(5)  # 主线程运行到子线程这里，子线程在这段时间内算不完这个数，可以多给他点时间
# print(number)

# result = 0
# import time
# for i in range(100000000):
#     result += i
# print(result)
