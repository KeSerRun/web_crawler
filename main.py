from adapters import *
import argparse

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='爬取网站数据')
    parser.add_argument('--source', type=str, required=True, help=f'数据来源，{", ".join(run_crawler_functions.keys())}')
    args = parser.parse_args()

    # 根据数据来源选择爬虫函数并执行
    if args.source in run_crawler_functions:
        run_crawler_functions[args.source]()
    else:
        print('数据来源不支持，请选择以下选项中的一个：')
        print(', '.join(run_crawler_functions.keys()))
