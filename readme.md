# 📈基于DrissionPage的自动化爬虫脚本

注意：本项目为AI辅助搭建，并非AI搭建，使用前请安装谷歌浏览器

____

## 项目介绍

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

## 快速使用

- 环境搭建

```bash
pip install -r requirements.txt
```

- 使用方式

```python
python main.py --source=请填写source
```

⚙️其中source可以为：

| 目的                       | source  | url                      |
| -------------------------- | ------- | ------------------------ |
| 爬取某鱼商品价格与商品描述 | goofish | https://www.goofish.com/ |
|                            |         |                          |
|                            |         |                          |
|                            |         |                          |

持续拓展中。。。

____

