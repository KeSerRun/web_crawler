import logging
import sys
from config import config

# 日志配置函数
def setup_logger(name: str = "app", level: int = config.logger_level) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 文件输出
    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    
    # 格式设置
    detailed_format = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    console_handler.setFormatter(simple_format)
    file_handler.setFormatter(detailed_format)
    
    # 添加 handler
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
