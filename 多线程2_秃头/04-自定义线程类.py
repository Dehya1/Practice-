# # 自定义线程类，直接将线程需要做的事写到run方法中
# import threading
#
# class MyThread(threading.Thread):
#     def run(self):  # 执行线程的时候要干的事，自己写
#         print('执行此线程：', self._args)
#
# t = MyThread(args=(100,))
# t.start()

import threading


class MyThread(threading.Thread):
    def __init__(self, arg):  # 在初始化方法中接收参数
        super().__init__()  # 调用父类的初始化方法
        self.arg = arg  # 将参数保存为实例变量

    def run(self):  # 执行线程的时候要干的事，自己写
        print('执行此线程：', self.arg)  # 访问实例变量


# 创建并启动线程，传递参数
t = MyThread(arg=100)
t.start()















