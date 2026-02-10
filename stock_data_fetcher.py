#!/usr/bin/env python3
"""
股票数据获取增强模块
直接使用requests库模拟浏览器访问，解决akshare连接问题
"""

import requests
import pandas as pd
import time
import threading
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class StockDataFetcher:
    """股票数据获取器，直接模拟浏览器访问"""
    
    # 浏览器请求头
    BROWSER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://quote.eastmoney.com/',
    }
    
    def __init__(self, request_interval: float = 2.0, timeout: int = 30):
        """
        初始化数据获取器
        
        Args:
            request_interval: 请求间隔（秒），默认2秒
            timeout: 请求超时时间（秒），默认30秒
        """
        self.request_interval = request_interval
        self.timeout = timeout
        self.session = None
        self.last_request_time = 0
        self.lock = threading.Lock()
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建带有浏览器模拟头的会话"""
        session = requests.Session()
        session.headers.update(self.BROWSER_HEADERS)
        # 设置一些常见的cookie
        session.cookies.set('qgqp_b_id', 'xxxxxxxxxxxxxxx', domain='.eastmoney.com')
        return session
    
    def _wait_for_rate_limit(self):
        """等待以满足请求频率限制"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.request_interval:
                sleep_time = self.request_interval - time_since_last
                print(f"⏳ 等待 {sleep_time:.2f} 秒...")
                time.sleep(sleep_time)
            self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict = None, max_retries: int = 3) -> Optional[requests.Response]:
        """
        发送带重试机制的请求
        
        Args:
            url: 请求URL
            params: 请求参数
            max_retries: 最大重试次数
            
        Returns:
            Response对象或None
        """
        self._wait_for_rate_limit()
        
        for attempt in range(max_retries):
            try:
                print(f"📡 请求: {url[:80]}..." if len(url) > 80 else f"📡 请求: {url}")
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response
                
            except requests.exceptions.ConnectionError as e:
                print(f"⚠️  连接失败 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ 重试次数用尽")
                    return None
                    
            except requests.exceptions.Timeout as e:
                print(f"⚠️  请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    time.sleep(wait_time)
                else:
                    return None
                    
            except Exception as e:
                print(f"⚠️  请求错误: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    time.sleep(wait_time)
                else:
                    return None
        
        return None
    
    def get_spot_quotes(self, symbols: List[str] = None) -> Optional[pd.DataFrame]:
        """
        获取实时行情数据
        
        Args:
            symbols: 股票代码列表，默认获取主要指数和热门股票
            
        Returns:
            DataFrame或None
        """
        # 默认获取主要指数和股票
        if symbols is None:
            symbols = [
                'sh000001',  # 上证指数
                'sz399001',  # 深证成指
                'sz399006',  # 创业板指
                'sh603650',  # 彤程新材
                'sh600519',  # 贵州茅台
                'sz002594',  # 比亚迪
            ]
        
        # 使用腾讯股票行情API
        url = "http://qt.gtimg.cn/q="
        
        all_data = []
        for symbol in symbols:
            response = self._make_request(url + symbol)
            if response and response.status_code == 200:
                try:
                    # 解析腾讯股票数据格式
                    lines = response.text.strip().split('~')
                    if len(lines) > 32:
                        data = {
                            'symbol': symbol,
                            'name': lines[1],
                            'price': float(lines[3]),
                            'change_pct': float(lines[32]),
                            'volume': int(lines[6]),
                            'amount': float(lines[7]),
                            'open': float(lines[5]),
                            'high': float(lines[33]),
                            'low': float(lines[34]),
                            'pre_close': float(lines[4]),
                        }
                        all_data.append(data)
                        direction = '📈' if data['change_pct'] > 0 else '📉' if data['change_pct'] < 0 else '➡️'
                        print(f"{direction} {symbol}: {data['price']:.2f} ({data['change_pct']:+.2f}%)")
                except Exception as e:
                    print(f"❌ 解析 {symbol} 数据失败: {e}")
        
        if all_data:
            return pd.DataFrame(all_data)
        return None
    
    def get_single_stock(self, stock_code: str) -> Optional[Dict]:
        """
        获取单只股票数据
        
        Args:
            stock_code: 股票代码（如 603650, 002594）
            
        Returns:
            字典或None
        """
        # 格式化股票代码
        if stock_code.startswith('6'):
            symbol = f"sh{stock_code}"
        else:
            symbol = f"sz{stock_code}"
        
        url = "http://qt.gtimg.cn/q="
        response = self._make_request(url + symbol)
        
        if response and response.status_code == 200:
            try:
                lines = response.text.strip().split('~')
                if len(lines) > 32:
                    return {
                        'symbol': symbol,
                        'name': lines[1],
                        'price': float(lines[3]),
                        'change_pct': float(lines[32]),
                        'volume': int(lines[6]),
                        'amount': float(lines[7]),
                        'open': float(lines[5]),
                        'high': float(lines[33]),
                        'low': float(lines[34]),
                        'pre_close': float(lines[4]),
                    }
            except Exception as e:
                print(f"❌ 解析 {stock_code} 数据失败: {e}")
        
        return None


def analyze_tongcheng_new_material():
    """分析彤程新材（603650）"""
    print("="*60)
    print("🔍 彤程新材（603650）实时行情分析")
    print("="*60)
    
    fetcher = StockDataFetcher(request_interval=2.0)
    
    # 获取彤程新材数据
    print("\n📊 获取彤程新材实时数据...")
    stock_data = fetcher.get_single_stock("603650")
    
    if stock_data:
        print(f"\n✅ 获取成功!")
        print(f"\n📈 实时行情:")
        print(f"  股票名称: {stock_data['name']}")
        print(f"  股票代码: {stock_data['symbol']}")
        print(f"  当前价格: {stock_data['price']:.2f}元")
        print(f"  涨跌幅: {stock_data['change_pct']:+.2f}%")
        print(f"  今日开盘: {stock_data['open']:.2f}元")
        print(f"  今日最高: {stock_data['high']:.2f}元")
        print(f"  今日最低: {stock_data['low']:.2f}元")
        print(f"  昨日收盘: {stock_data['pre_close']:.2f}元")
        print(f"  成交量: {stock_data['volume']:,}股")
        print(f"  成交额: {stock_data['amount']:.2f}万元")
    else:
        print("\n❌ 获取数据失败")
    
    return stock_data


def analyze_market():
    """分析整体市场"""
    print("="*60)
    print("📊 A股市场实时行情")
    print("="*60)
    
    fetcher = StockDataFetcher(request_interval=2.0)
    
    # 获取主要指数
    print("\n🏛️ 主要指数:")
    indices = ['sh000001', 'sz399001', 'sz399006']
    index_names = {
        'sh000001': '上证指数',
        'sz399001': '深证成指', 
        'sz399006': '创业板指'
    }
    
    for symbol in indices:
        data = fetcher.get_single_stock(symbol)
        if data:
            direction = '📈' if data['change_pct'] > 0 else '📉' if data['change_pct'] < 0 else '➡️'
            print(f"  {direction} {index_names.get(symbol, symbol)}: {data['price']:.2f} ({data['change_pct']:+.2f}%)")
    
    # 获取热门股票
    print("\n🔥 热门股票:")
    stocks = [
        ('603650', '彤程新材'),
        ('600519', '贵州茅台'),
        ('002594', '比亚迪'),
    ]
    
    for code, name in stocks:
        data = fetcher.get_single_stock(code)
        if data:
            direction = '📈' if data['change_pct'] > 0 else '📉' if data['change_pct'] < 0 else '➡️'
            print(f"  {direction} {name} ({code}): {data['price']:.2f} ({data['change_pct']:+.2f}%)")


def main():
    """主函数"""
    print("🔧 股票数据获取器 - 浏览器模拟访问")
    print("="*60)
    
    # 分析彤程新材
    analyze_tongcheng_new_material()
    
    print("\n")
    
    # 分析整体市场
    analyze_market()


if __name__ == "__main__":
    main()
