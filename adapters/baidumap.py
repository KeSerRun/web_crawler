from .base import BaseAdapter
from utils.exception import handle_exception
from utils.logger import setup_logger
import re
from config.config import config
import time
import random

# 创建日志记录器
logger = setup_logger(__name__)

# 度哥地图适配器，继承自 BaseAdapter
class BaiduMapAdapter(BaseAdapter):
    @handle_exception
    def enter_to_search(self):
        # 访问主页
        self.go_home(self.tab, self.url)
        logger.info(f'进入 {self.url} 成功')
    
    @handle_exception
    def perform_search(self, keys: dict):
        # 找到输入框并输入搜索关键词
        search_input = self.tab.ele('xpath://input[contains(@class, "searchbox-content-common")]')
        search_input.input(f"{keys['location']}:{keys['class']}")
        # 点击搜索按钮
        search_button = self.tab.ele('xpath://button[contains(@data-title, "搜索")]')
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
            next_button = self.tab.ele('xpath://a[contains(@tid, "toNextPage")]')
            if next_button:
                next_button.click()
            else:
                logger.warning('未找到下一页按钮，可能已到达最后一页')

    @handle_exception
    def listen_and_action(self):
        # 监听数据包并执行数据包触发方法
        self.tab.listen.start(self.pk_url,res_type='XHR')
        self.action()  # 执行数据包触发方法
        # 跳过第一个数据包，因为它通常是页面加载时的请求，可能不包含我们需要的数据
        self.tab.listen.wait(timeout=5)  # 抓取数据包
        data = self.tab.listen.wait(timeout=5)  # 抓取数据包
        self.tab.listen.stop()  # 停止监听
        return data

    @handle_exception
    def parse_data(self, data):
        # from rich import print
        # # 打印数据包，帮助调试和分析数据结构
        # data = data['content'][0]
        # import json
        # with open('data.json', 'w', encoding='utf-8') as f:
        #     json.dump(data,f, ensure_ascii=False, indent=4)
        # exit()
        # 解析数据包，这里是示例，实际需要根据数据包结构进行调整

        data_list = []
        for data in data['content']:
            item_data = data
            '''根据分类解析数据包'''
            if self.keys['class'] == '美食':
                extra_info = {
                    'business_time': item_data.get('business_time',{}).get('data',[{}])[0].get('business_time_text',{}).get('common', ''),
                    'price': item_data.get('ext',{}).get('detail_info',{}).get('bubble_info',{}).get('title',{}).get('text', ''),
                    'score': item_data.get('ext',{}).get('detail_info',{}).get('bubble_info',{}).get('sub_title',{}).get('text', ''),
                    'phone': item_data.get('ext',{}).get('detail_info',{}).get('phone',''),
                }
            elif self.keys['class'] == '酒店':
                extra_info = {
                    'business_time': item_data.get('ext',{}).get('detail_info',{}).get('vs_content',{}).get('basic_facts',{}).get('hotel_detail',{}).get('basic_info',{}).get('checkin_policy', '')\
                                    + '，' + item_data.get('ext',{}).get('detail_info',{}).get('vs_content',{}).get('basic_facts',{}).get('hotel_detail',{}).get('basic_info',{}).get('checkout_policy', ''),
                    'price': item_data.get('ext',{}).get('detail_info',{}).get('hotel_ext',{}).get('singleroom',{}).get('realprice', ''),
                    'score': item_data.get('ext',{}).get('detail_info',{}).get('overall_rating', ''),
                    'phone': item_data.get('ext',{}).get('detail_info',{}).get('phone',''),
                }
            parsed_data = {
                # 将当前搜索键组合添加到解析后的数据中
                **self.keys, 
                # 根据数据包结构提取需要的字段
                'addr': item_data.get('addr', ''),
                'area_name': item_data.get('area_name', ''),
                'di_tag': item_data.get('di_tag', ''),
                'name': item_data.get('name', ''),
                'coordinates': f"{item_data.get('x','')},{item_data.get('y','')}",
                # 添加根据分类解析的额外信息
                **extra_info 
                # ...
            }
            # print(parsed_data)  # 打印解析后的数据，帮助调试和验证解析逻辑
            # exit()
            data_list.append(parsed_data)
        return data_list

# 定义爬虫函数，供 main.py 调用
def run_crawler_baidumap():
    # 定义目标URL和数据包URL
    url = 'https://map.baidu.com/'
    pk_url = 'https://map.baidu.com/?newmap=1'
    adapter = BaiduMapAdapter(url, pk_url, name='baidumap')
    
    # 运行爬虫
    adapter.run(config.search_keys)