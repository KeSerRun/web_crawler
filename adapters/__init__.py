from .goofish import run_crawler_goofish

# 将数据来源与爬虫函数映射起来，方便后续调用
run_crawler_functions = {
    'goofish': run_crawler_goofish,
}