#!/usr/bin/env python3
"""
浏览器自动化工具包装器
"""

import subprocess
import json
import sys
import os

def run_browser_automation(operation, *args):
    """
    运行浏览器自动化工具
    :param operation: 操作类型 (navigate, search, extract, screenshot)
    :param args: 操作参数
    :return: 结果
    """
    cmd = ["python3", "/root/clawd/enhanced_browser_tool.py", operation] + list(args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            return {"error": f"执行失败: {result.stderr}"}
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"error": f"解析输出失败: {result.stdout}"}
    
    except subprocess.TimeoutExpired:
        return {"error": "操作超时"}
    except Exception as e:
        return {"error": f"执行异常: {str(e)}"}

def browse_url(url):
    """浏览指定URL"""
    return run_browser_automation("navigate", url)

def search_on_page(url, search_term):
    """在页面上搜索内容"""
    return run_browser_automation("search", url, search_term)

def extract_elements(url, selectors_json):
    """提取页面元素"""
    return run_browser_automation("extract", url, selectors_json)

def take_screenshot(url, save_path="screenshot.png"):
    """截取页面截图"""
    return run_browser_automation("screenshot", url, save_path)

def check_screenshot_exists(path):
    """检查截图是否存在"""
    return os.path.exists(path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 browser_automation_wrapper.py <operation> [args...]")
        print("Operations: browse, search, extract, screenshot")
        sys.exit(1)
    
    operation = sys.argv[1]
    args = sys.argv[2:]
    
    result = run_browser_automation(operation, *args)
    print(json.dumps(result, ensure_ascii=False, indent=2))