import time
import threading

def sing(msg):
    while True:
        print('唱歌，啦啦啦啦',msg)
        time.sleep(1)

def dance(msg):
    while True:
        print('跳舞，哒哒哒',msg)
        time.sleep(1)

if __name__ == '__main__':
    sing_thread = threading.Thread(target=sing,args=('哈哈哈哈哈哈',))    # 创建线程
    dance_thread = threading.Thread(target=dance,kwargs={'msg':'hehehehehehe'})

    sing_thread.start()     # 让线程干活
    dance_thread.start()












