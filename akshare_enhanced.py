#!/usr/bin/env python3
"""
AKShare增强模块
添加浏览器模拟请求头和请求频率限制，解决API连接问题
"""

import akshare as ak
import requests
import time
import threading
from typing import Dict, Any, Optional, Callable
from functools import wraps
import warnings
warnings.filterwarnings('ignore')


class AkshareEnhanced:
    """AKShare增强类，添加浏览器模拟和频率控制"""
    
    # 浏览器请求头
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Referer': 'https://www.eastmoney.com/',
    }
    
    def __init__(self, min_request_interval: float = 3.0, max_retries: int = 3):
        """
        初始化增强模块
        
        Args:
            min_request_interval: 最小请求间隔（秒），默认3秒
            max_retries: 最大重试次数，默认3次
        """
        self.min_request_interval = min_request_interval
        self.max_retries = max_retries
        self.last_request_time = 0
        self.session = None
        self.lock = threading.Lock()
        
    def create_session(self) -> requests.Session:
        """创建带有浏览器模拟头的请求会话"""
        session = requests.Session()
        session.headers.update(self.DEFAULT_HEADERS)
        self.session = session
        return session
    
    def wait_for_rate_limit(self):
        """等待以满足请求频率限制"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last
                print(f"⏳ 等待 {sleep_time:.2f} 秒以满足请求频率限制...")
                time.sleep(sleep_time)
            self.last_request_time = time.time()
    
    def get_with_retry(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        带重试机制的GET请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            Response对象或None
        """
        self.wait_for_rate_limit()
        
        for attempt in range(self.max_retries):
            try:
                if self.session:
                    response = self.session.get(url, **kwargs)
                else:
                    response = requests.get(url, **kwargs)
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.ConnectionError as e:
                print(f"⚠️  连接失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 指数退避
                    print(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ 重试次数用尽，放弃请求")
                    return None
                    
            except requests.exceptions.Timeout as e:
                print(f"⚠️  请求超时 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                else:
                    return None
                    
            except requests.exceptions.HTTPError as e:
                print(f"⚠️  HTTP错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                else:
                    return None
                    
            except Exception as e:
                print(f"⚠️  未知错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                else:
                    return None
        
        return None


def rate_limited(min_interval: float = 3.0):
    """
    装饰器：为函数添加请求频率限制
    
    Args:
        min_interval: 最小请求间隔（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if hasattr(wrapper, '_last_call'):
                time_since_last = current_time - wrapper._last_call
                if time_since_last < min_interval:
                    sleep_time = min_interval - time_since_last
                    print(f"⏳ 等待 {sleep_time:.2f} 秒以满足请求频率限制...")
                    time.sleep(sleep_time)
            
            wrapper._last_call = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class AkshareWrapper:
    """AKShare包装器，提供增强的数据获取功能"""
    
    def __init__(self, request_interval: float = 3.0, max_retries: int = 3):
        """
        初始化包装器
        
        Args:
            request_interval: 请求间隔（秒）
            max_retries: 最大重试次数
        """
        self.enhanced = AkshareEnhanced(
            min_request_interval=request_interval,
            max_retries=max_retries
        )
        self.enhanced.create_session()
    
    def get_stock_zh_a_spot_em(self) -> Optional[Any]:
        """
        获取A股实时行情（增强版）
        
        Returns:
            DataFrame或None
        """
        print("🔄 使用增强模式获取A股实时行情...")
        self.enhanced.wait_for_rate_limit()
        
        try:
            data = ak.stock_zh_a_spot_em()
            if data is not None and not data.empty:
                print(f"✅ 成功获取 {len(data)} 条A股数据")
                return data
            else:
                print("⚠️  获取到空数据")
                return None
        except Exception as e:
            print(f"❌ 获取A股数据失败: {e}")
            return None
    
    def get_stock_zh_a_hist(self, symbol: str = "0000001", period: str = "daily", 
                           start_date: str = "20240101", end_date: str = "20241231") -> Optional[Any]:
        """
        获取A股历史数据（增强版）
        
        Args:
            symbol: 股票代码
            period: 周期 (daily, weekly, monthly)
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame或None
        """
        print(f"🔄 获取 {symbol} 历史数据...")
        self.enhanced.wait_for_rate_limit()
        
        try:
            data = ak.stock_zh_a_hist(symbol=symbol, period=period, 
                                     start_date=start_date, end_date=end_date)
            if data is not None and not data.empty:
                print(f"✅ 成功获取 {len(data)} 条历史数据")
                return data
            else:
                print("⚠️  获取到空数据")
                return None
        except Exception as e:
            print(f"❌ 获取历史数据失败: {e}")
            return None


# 测试函数
def test_enhanced_akshare():
    """测试增强版AKShare功能"""
    print("="*60)
    print("🧪 测试AKShare增强模块")
    print("="*60)
    
    wrapper = AkshareWrapper(request_interval=3.0, max_retries=3)
    
    # 测试获取A股实时数据
    print("\n📊 测试获取A股实时数据...")
    data = wrapper.get_stock_zh_a_spot_em()
    
    if data is not None and not data.empty:
        print(f"\n✅ 成功获取 {len(data)} 条A股数据")
        print("\n前5条数据:")
        print(data.head())
    else:
        print("\n❌ 获取A股数据失败")
    
    return data


if __name__ == "__main__":
    test_enhanced_akshare()
