from DrissionPage import Chromium, ChromiumOptions
from utils.exception import handle_exception
from utils.logger import setup_logger
from config import config
import json
from typing import Any
import flatdict
import pandas as pd
import os

logger = setup_logger(__name__)

# 加载断点
@handle_exception
def load_checkpoint(url: str)->dict:
    logger.info(f'加载断点, URL: {url}')
    if not os.path.exists('runtime/checkpoint.json'):
        logger.warning('断点文件 runtime/checkpoint.json 不存在，返回空状态')
        # 如果文件不存在，创建一个空的断点文件
        with open('runtime/checkpoint.json', 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)
        return None
    with open('runtime/checkpoint.json', 'r', encoding='utf-8') as f:
        check_points = json.load(f) if os.path.exists('runtime/checkpoint.json') else []
    status = next((cp['status'] for cp in check_points if cp['url'] == url), None)
    return status

# 保存断点
@handle_exception
def save_checkpoint(url:dict, status:dict):
    # 读取现有的断点信息
    with open('runtime/checkpoint.json', 'r', encoding='utf-8') as f:
        check_points = json.load(f) if os.path.exists('runtime/checkpoint.json') else []
    # 更新当前URL的断点信息
    has_updated = False
    for i, cp in enumerate(check_points):
        if cp['url'] == url:
            check_points[i]['status'] = status
            has_updated = True
            break
    # 如果没有找到对应URL的断点信息，则添加新的记录
    if not has_updated:
        check_points.append({'url': url, 'status': status})
    # 保存更新后的断点信息
    with open('runtime/checkpoint.json', 'w', encoding='utf-8') as f:
        json.dump(check_points, f, indent=4,ensure_ascii=False)

# 保存数据
@handle_exception
def save_data(data: dict | list[dict], filename: str):
    if isinstance(data, dict):
        data = [data]  # 将单条记录转换为列表
    # 将嵌套字典展平为一层
    flat_list = [flatdict.FlatDict(item, delimiter='.') for item in data]
    logger.info(f'正在保存数据到 output/{filename}，共 {len(flat_list)} 条记录')
    # 将展平后的数据转换为DataFrame
    df = pd.DataFrame(flat_list)
    # 保存为CSV文件，使用UTF-8编码，避免中文乱码，追加模式，且不写入索引
    file_exists = os.path.exists(f'output/{filename}')
    with open(f'output/{filename}', 'a', encoding='utf-8') as f:
        df.to_csv(
            f,
            index=False,
            header=not file_exists,  # 文件不存在时写入表头，存在则跳过
            encoding='utf-8' 
        )
    logger.info(f'数据已成功保存到 output/{filename}')

# 获取新的浏览器实例
@handle_exception
def get_newbrowser()->Chromium:
    co = ChromiumOptions()  # 创建选项对象
    if config.PORT == 'auto':
        co.auto_port()          # 设置连接端口
    else:
        co.set_local_port(config.PORT)  # 设置调试端口，默认9222
    co.headless(config.HEADLESS)      # 设置无头模式
    co.no_imgs(config.NO_IMGS)        # 禁用图片
    # 设置用户代理
    co.set_user_agent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/148.0.0.0 Safari/537.36'
    ) 
    # 去掉自动化特征
    co.set_argument('--disable-blink-features=AutomationControlled') 
    co.set_argument('--no-first-run')
    co.set_argument('--no-default-browser-check')
    # 补充以下参数：
    co.set_argument('--disable-infobars')           # 禁止信息栏
    co.set_argument('--disable-extensions')         # 禁用扩展
    co.set_argument('--disable-gpu')                # 禁用GPU（部分检测点）
    co.set_argument('--disable-dev-shm-usage')      # 避免 /dev/shm 问题
    co.set_argument('--window-size=540,1080')       # 设置窗口大小（无头时重要）
    co.set_argument('--start-maximized')            # 最大化窗口
    # 语言、时区、地理位置伪装
    co.set_argument('--lang=zh-CN,zh')
    co.set_pref('intl.accept_languages', 'zh-CN,zh')
    # co.set_browser_path(r'D:\chrome.exe') # 如果系统找不到 Chrome 路径，可以在这里手动指定
    # 获取浏览器对象
    browser = Chromium(co) 
    logger.debug('已创建新的浏览器实例')
    return browser

# 获取新的标签页
@handle_exception
def get_newtab(browser=None):
    # 如果没有浏览器实例，重开一个浏览器实例
    if browser is None:
        browser = get_newbrowser()
    # 获取标签页对象
    tab = browser.new_tab()
    # 设置超时时间，不能超过5秒，提高效率
    tab.set.timeouts(base=5)
    logger.debug('已创建新的标签页')
    return tab

# 访问主页
@handle_exception
def go_home(tab: Any, url: str):
    # 访问URL
    tab.get(url)
    # 等待页面加载完成，不能超过5秒，提高效率
    tab.wait.doc_loaded(timeout=5)
    logger.debug('已访问主页')

# 搜索键生成器
def search_key_generator(search_keys: dict, status: dict):
    """
    根据 status 作为起始点，依次生成所有搜索键组合
    
    示例：
    search_keys = {
        'key1': ['a', 'b', 'c'],
        'key2': ['x', 'y']
    }
    status = {'key1': 'b', 'key2': 'x'}
    
    生成的顺序：
    1. {'key1': 'b', 'key2': 'x'}  # 起始点
    2. {'key1': 'b', 'key2': 'y'}  # key2 进位
    3. {'key1': 'c', 'key2': 'x'}  # key2 到头，key1 进位，key2 重置
    4. {'key1': 'c', 'key2': 'y'}
    5. ... 退出
    """
    
    # 获取所有 key 的顺序（比如按字母排序或保持原顺序）
    keys = list(search_keys.keys())
    
    if not status:
        # 如果没有断点信息，从第一个组合开始
        status = {key: values[0] for key, values in search_keys.items()}

    # 初始化当前状态为 status
    current = status.copy()
    
    while True:
        yield current.copy()  # 返回当前状态
        
        # 推进到下一个组合（类似加法进位），先推进最后一个 key
        for i in range(len(keys) - 1, -1, -1):  
            key = keys[i]
            values = search_keys[key]
            current_idx = values.index(current[key])
            
            if current_idx < len(values) - 1:
                # 当前位可以递增
                current[key] = values[current_idx + 1]
                break
            else:
                # 当前位到头了，重置为第一个值，继续进位
                current[key] = values[0]
                # 继续循环，让更高位递增
        else:
            # 所有组合都已遍历完，停止
            break

# 执行基类
class BaseAdapter:
    def __init__(self, url: str, pk_url: str, name: str='new'):
        """爬虫适配器基类

        Args:
            url (str): 数据来源的URL
            pk_url (str): 数据包URL
            name (str): 爬虫任务名称，默认为 'new'，用于区分不同的爬虫任务
        """
        self.url = url
        self.pk_url = pk_url
        self.name = name
        # 初始化浏览器和标签页
        self.browser = get_newbrowser()
        self.tab = get_newtab(self.browser)
        # 访问主页函数，确保浏览器正常工作
        self.go_home = go_home
        # 当前状态
        self.status = load_checkpoint(self.url) or {}

    # 进入搜索页面方法，子类必须实现
    def enter_to_search(self):
        raise NotImplementedError('子类必须实现 enter_to_search 方法')
    
    # 执行搜索方法，子类必须实现
    def perform_search(self, keys: dict):
        raise NotImplementedError('子类必须实现 perform_search 方法')
    
    # 数据包的触发方法，子类必须实现
    def action(self):
        raise NotImplementedError('子类必须实现 action 方法')

    # 解析数据包方法，子类必须实现
    def parse_data(self, data):
        raise NotImplementedError('子类必须实现 parse_data 方法')

    @handle_exception
    def __enter_to_search(self):
        # 进入搜索页面
        self.enter_to_search()
        # 等待用户登录（如果需要登录的话）
        if config.NEED_LOGIN:
            input('登录后，手工搜索，排除干扰后按回车继续...')  

    # 执行方法，包含整个爬取流程
    @handle_exception
    def __execute(self, search_keys: dict):
        # 创建搜索键生成器
        gen = search_key_generator(search_keys, self.status)
        # 迭代生成搜索键组合并执行搜索
        for idx,keys in enumerate(gen):
            # 将当前搜索键组合保存到实例属性，方便调试和日志记录
            self.keys = keys  
            logger.info(f'正在搜索，当前搜索键组合: {keys}')
            # 更新断点信息
            self.status.update(keys)
            # 保存断点，确保在爬取过程中任何时候发生错误都能从当前搜索键组合继续爬取
            save_checkpoint(self.url, self.status)
            # 只有在第一页时才进入搜索页面，后续页数直接执行翻页操作
            if self.status['page'] <= 1 or idx == 0:
                # 进入搜索页面
                self.__enter_to_search()
                # 执行搜索
                self.perform_search(keys)
            # 监听数据包并执行数据包触发方法
            self.tab.listen.start(self.pk_url)
            # 执行数据包触发方法
            self.action()  
            # 抓取数据包
            data = self.tab.listen.wait(timeout=5)
            # 停止监听
            self.tab.listen.stop()
            # 解析数据包
            data = self.parse_data(data.response.body)
            # 保存数据
            save_data(data, f'{self.name}.csv')

    # 公开的执行方法
    def run(self, search_keys: dict):
        try:
            self.__execute(search_keys)
        except Exception as e:
            logger.error(f'执行过程中发生错误: {e}')
        finally:
            # 关闭浏览器
            self.browser.quit()
    
    def __del__(self):
        # 确保浏览器在对象销毁时关闭，避免资源泄露
        try:
            self.browser.quit()
        except Exception as e:
            logger.warning(f'在销毁对象时关闭浏览器发生错误: {e}')