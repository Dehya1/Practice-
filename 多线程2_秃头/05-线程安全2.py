import threading
num = 0
lock_object = threading.RLock()

# RLOCK可以嵌套锁，锁两次，释放两次

def task():
    print('开始')
    lock_object.acquire()  # 第一个抵达的线程进入并上锁，其他线程就需要在此等待
    lock_object.acquire()  # 第一个抵达的线程进入并上锁，其他线程就需要在此等待
    print(123)
    lock_object.release()  # 线程出去，并解开锁，其他线程就可以进入并执行了
    lock_object.release()  # 线程出去，并解开锁，其他线程就可以进入并执行了


for i in range(2):
    t = threading.Thread(target=task)
    t.start()

"""
# RLOCK的应用场景
import threading
lock = threading.RLock

# 程序员A开发了一个函数，函数可以被其他开发者调用，内部需要基于锁保证数据安全
def func():
    with lock:
        pass
    
# 程序员B开发了一个函数，可以直接调用这个函数
def run():
    print('其他功能')
    func()  # 调用程序员A写的函数，内部用到了锁
    print('其他功能')
    
# 程序员C开发了一个函数，自己需要加锁，同时也需要调用func函数
def process():
    with lock:
        print('其他功能')
        func()  # 此时会出现多次锁的情况，Rlock支持多次锁，Lock就不行
        print('其他功能')
"""