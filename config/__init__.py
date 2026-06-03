# 导入配置模块
from .config import config
# 导入目录设置模块
from .setup import setup_directories


# 确保目录结构已创建
setup_directories(config.directories)  