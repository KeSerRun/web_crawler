
'''
配置文件，存储全局变量和常量
'''

class Config:
    def __init__(self):
        self.logger_level = 'DEBUG'      # 日志级别
        self.HEADLESS = False            # 是否无头模式
        self.NO_IMGS = False             # 是否禁用图片
        self.PORT = 9222                 # 浏览器调试端口,默认9222, 'auto'表示自动选择空闲端口
        self.NEED_LOGIN = True           # 是否需要登录
        self.browser_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'         # 浏览器路径，None表示使用默认路径

        '''定义需要创建的目录列表'''
        self.directories = [            # 定义需要创建的目录列表
            'output',                   # 存储爬取的数据
            'logs',                     # 存储日志文件
            'runtime'                   # 存储运行时生成的文件，如临时数据等
        ]

        '''定义搜索关键词列表'''
        self.search_keys = {
            'goods': ['笔记本', '手机', '自行车', '显卡', '耳机'],  # 定义搜索关键词列表，这里是示例，可以根据需要修改
            'page': range(1,21)         # 定义页数范围，这里是1到20页
        }

config = Config()