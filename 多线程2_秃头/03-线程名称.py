# 线程名称的设置和获取
import threading
def task():
    # 获取当前执行此代码的线程
    name = threading.current_thread().name  # 获取当前正在执行的线程的名称
    print(name)

for i in range(10):
    t = threading.Thread(target=task)
    t.name = f'编号{i}'  # 给线程对象设置自定义名称。在start之前设置名字
    t.start()
















