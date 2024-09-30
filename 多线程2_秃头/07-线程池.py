import time
from concurrent.futures import ThreadPoolExecutor

# pool = ThreadPoolExecutor(100)
# pool.submit(函数名,参数1,参数2,参数...)

def task(video_url,num):
    print('开始执行任务',video_url)
    time.sleep(5)

# 创建线程池，最多维护10个线程
pool =ThreadPoolExecutor(10)
url_list = ['www.xxx-{}.com'.format(i) for i in range(300)]
for url in url_list:
    # 在线程池中提交一个任务，线程池中如果有空闲线程，则分配一个线程去执行，执行完毕后再将线程交还给线程池；如果没有空闲线程，则等待
    pool.submit(task,url,2)

print('END')


















