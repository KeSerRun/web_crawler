from .goofish import run_crawler_goofish
from .baidumap import run_crawler_baidumap

# 将数据来源与爬虫函数映射起来，方便后续调用
run_crawler_functions = {
    'goofish': run_crawler_goofish,
    'baidumap': run_crawler_baidumap,
}