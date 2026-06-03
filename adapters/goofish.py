from .base import BaseAdapter
from utils.exception import handle_exception
from utils.logger import setup_logger
import re
from config.config import config
import time
import random

# 创建日志记录器
logger = setup_logger(__name__)

# 盐鱼适配器，继承自 BaseAdapter
class GoofishAdapter(BaseAdapter):
    @handle_exception
    def enter_to_search(self):
        # 访问主页
        self.go_home(self.tab, self.url)
        logger.info(f'进入 {self.url} 成功')
    
    @handle_exception
    def perform_search(self, keys: dict):
        # 找到输入框并输入搜索关键词
        search_input = self.tab.ele('xpath://input[contains(@class, "search-input")]')
        search_input.input(keys['goods'])
        # 点击搜索按钮
        search_button = self.tab.ele('xpath://button[contains(@class, "search-icon")]')
        search_button.click()
    
    @handle_exception
    def action(self):
        '''模拟人工，随机等待1-3秒，触发数据包'''
        time.sleep(random.uniform(1, 3))
        if self.status['page'] <= 1:
            # 触发数据包，这里是示例，实际需要根据页面结构进行调整
            self.tab.refresh()  # 刷新页面以触发数据包
        else:
            # 执行翻页操作，这里是示例，实际需要根据页面结构进行调整
            next_button = self.tab.ele('xpath://div[contains(@class, "search-page-tiny-arrow-right")]').parent()
            if next_button:
                next_button.click()
            else:
                logger.warning('未找到下一页按钮，可能已到达最后一页')

    @handle_exception
    def parse_data(self, data):
        # from rich import print
        # 打印数据包，帮助调试和分析数据结构
        # print(data['data']['resultList'][0]['data']['item']['main']['exContent']) 
        # 解析数据包，这里是示例，实际需要根据数据包结构进行调整
        data_list = []
        for data in data['data']['resultList']:
            item_data = data['data']['item']['main']['exContent']
            parsed_data = {
                # 将当前搜索键组合添加到解析后的数据中
                **self.keys, 
                # 根据数据包结构提取需要的字段
                'itemId': item_data.get('itemId'),
                'area': item_data.get('area'),
                'userNickName': item_data.get('userNickName'),
                'price': ' '.join([item.get('text') for item in item_data.get('price', [])]),
                'userFishShopLabel': ' '.join([item.get('data').get('content') for item in item_data.get('userFishShopLabel',{}).get('tagList',[])]),
                'picUrl': item_data.get('picUrl'),
                'title': re.sub(r'[\n]', '。', item_data.get('detailParams', {}).get('title', '')),
                # ...
            }
            # print(parsed_data)  # 打印解析后的数据，帮助调试和验证解析逻辑
            data_list.append(parsed_data)
        return data_list

# 定义爬虫函数，供 main.py 调用
def run_crawler_goofish():
    # 定义目标URL和数据包URL
    url = 'https://www.goofish.com/'
    pk_url = 'https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/'
    adapter = GoofishAdapter(url, pk_url, name='goofish')
    
    # 运行爬虫
    adapter.run(config.search_keys)