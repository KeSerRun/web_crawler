from utils.logger import setup_logger

# 获取日志记录器
logger = setup_logger(__name__)

# 错误处理装饰器
def handle_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f'{func.__name__} 发生异常: {e}')
            # 向上抛出异常，让外层循环捕获并继续执行
            raise e
    return wrapper