# 📈基于DrissionPage的自动化爬虫脚本

注意：本项目为AI辅助搭建，并非AI搭建，使用前请确保装有谷歌浏览器，如果是edge，请在config.py中指定浏览器路径

____

## 🎯 项目介绍

- 项目目录结构

```
web-crawler
├─adapters
│  │  base.py
│  │  goofish.py
│  └─ __init__.py    
├─config
│  │  config.py
│  │  setup.py
│  └─ __init__.py         
├─logs
│      app.log   
├─output
│      goofish.csv 
├─runtime
│      checkpoint.json     
└─utils
|   │  exception.py
|   └─ logger.py
│  main.py
│  readme.md
│  requirements.txt
└─ test.py
```

## 💻快速使用

- 环境搭建

```bash
pip install -r requirements.txt
```

- 使用方式

```python
python main.py --source=请填写source
```

⚙️其中source可以为：

| 目的                               | source   | url                      |
| ---------------------------------- | -------- | ------------------------ |
| 爬取某鱼商品价格与商品描述         | goofish  | https://www.goofish.com/ |
| 爬取某度地图中的美食、酒店价格信息 | baidumap | https://map.baidu.com/   |
|                                    |          |                          |
|                                    |          |                          |

持续拓展中。。。

____

## 🛠️配置选项

在config/config.py中

```python
class Config:
    def __init__(self):
        self.logger_level = 'DEBUG'      # 日志级别
        self.HEADLESS = False            # 是否无头模式
        self.NO_IMGS = False             # 是否禁用图片
        self.PORT = 9222                 # 浏览器调试端口,默认9222, 'auto'表示自动选择空闲端口
        self.NEED_LOGIN = True           # 是否需要登录
        self.browser_path = None         # 浏览器路径，None表示使用默认路径，如果是edge，请指定msedge.exe的完整路径，例如 r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

        '''定义需要创建的目录列表'''
        self.directories = [            # 定义需要创建的目录列表
            'output',                   # 存储爬取的数据
            'logs',                     # 存储日志文件
            'runtime'                   # 存储运行时生成的文件，如临时数据等
        ]

        '''定义搜索关键词列表'''
        self.search_keys = {
            'goods': ['笔记本', '手机', '自行车', '显卡', '耳机'],  # 定义搜索关键词列表，这里是示例，可以根据需要修改
            'page': range(1,21)         # 定义页数范围，这里是1到20页，页数必须是最后一个键
        }
```

