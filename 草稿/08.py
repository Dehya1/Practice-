from venv import logger

try:
    # 尝试执行的代码块
    result = 10 / 0
except ZeroDivisionError as e:
    # 如果上面的代码块引发了ZeroDivisionError异常，则执行这里的代码
    # print("错误：除数不能为0")
    logger.error(f'random buy:{e}', exc_info=True)
# except Exception as e:
#     # 如果上面的代码块引发了其他类型的异常，则执行这里的代码
#     # 'e'是捕获到的异常实例
#     print(f"发生了一个错误：{e}")
# else:
#     # 如果没有异常发生，则执行这里的代码
#     # 注意：'else'部分是可选的
#     print("计算成功")
# finally:
#     # 无论是否发生异常，都会执行这里的代码
#     # 'finally'部分也是可选的，但非常有用，比如用于资源清理
#     print("程序继续执行")

