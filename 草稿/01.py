import logging

# 创建一个日志记录器，如果不传参数，则默认为root logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # 设置日志记录器的级别为DEBUG，但具体输出级别由处理器决定

# 创建一个文件处理器，用于写入日志文件
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.ERROR)  # 将文件处理器的级别设置为ERROR

# 创建一个日志格式器，并添加到文件处理器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 将文件处理器添加到日志记录器
logger.addHandler(file_handler)

# 现在，只有ERROR及以上级别的日志会被写入到app.log文件中
logger.debug('This is a debug message')  # 这将不会被写入文件
logger.info('This is an info message')  # 这也不会被写入文件
logger.warning('This is a warning message')  # 这同样不会被写入文件
logger.error('This is an error message')  # 这将被写入文件
logger.critical('This is a critical message')  # 这也会被写入文件