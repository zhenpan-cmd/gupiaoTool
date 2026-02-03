#!/usr/bin/env python3
"""
增强型浏览器自动化工具 - 为Clawdbot设计
"""

import asyncio
import json
import sys
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
import re

class EnhancedBrowserAutomation:
    """增强型浏览器自动化工具"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
    
    async def initialize(self):
        """初始化浏览器"""
        if self.browser is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
    
    async def navigate_to_url(self, url):
        """导航到指定URL"""
        await self.initialize()
        self.page = await self.context.new_page()
        await self.page.goto(url, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(2000)  # 等待页面加载
        return True
    
    async def get_page_content(self):
        """获取页面主要内容"""
        if self.page is None:
            return {"error": "未打开任何页面"}
        
        # 获取页面标题
        title = await self.page.title()
        
        # 获取页面文本内容
        content = await self.page.inner_text('body')
        
        # 获取页面元数据
        meta_description = await self.page.evaluate(
            "() => { const el = document.querySelector('meta[name=\"description\"]'); return el ? el.content : ''; }"
        )
        
        # 获取所有链接
        links = await self.page.evaluate(
            "() => { return Array.from(document.querySelectorAll('a[href]')).map(a => ({ href: a.href, text: a.textContent.trim() })); }"
        )
        
        return {
            "title": title,
            "description": meta_description,
            "content_preview": content[:500] + "..." if len(content) > 500 else content,
            "links_count": len(links),
            "sample_links": links[:10]  # 只返回前10个链接
        }
    
    async def search_and_extract(self, base_url, search_term, selectors=None):
        """在页面上搜索并提取信息"""
        if self.page is None:
            await self.navigate_to_url(base_url)
        
        # 如果提供了选择器，则直接提取信息
        if selectors:
            results = {}
            for name, selector in selectors.items():
                try:
                    elements = await self.page.query_selector_all(selector)
                    results[name] = [await element.text_content() for element in elements]
                except:
                    results[name] = []
            return results
        
        # 否则进行文本搜索
        content = await self.page.inner_text('body')
        # 搜索相关文本段落
        paragraphs = content.split('\n')
        relevant_paragraphs = [p for p in paragraphs if search_term.lower() in p.lower()]
        
        return {
            "search_term": search_term,
            "matches_found": len(relevant_paragraphs),
            "relevant_content": relevant_paragraphs[:5]  # 返回前5个匹配段落
        }
    
    async def fill_form_and_submit(self, form_data, submit_button_selector=None):
        """填充表单并提交"""
        if self.page is None:
            return {"error": "未打开任何页面"}
        
        # 填充表单字段
        for field_name, value in form_data.items():
            try:
                # 尝试多种选择器策略
                selectors = [
                    f'[name="{field_name}"]',
                    f'[id="{field_name}"]',
                    f'text="{field_name}"',
                    f'input[type="text"][placeholder*="{field_name}"]'
                ]
                
                filled = False
                for selector in selectors:
                    try:
                        await self.page.fill(selector, str(value))
                        filled = True
                        break
                    except:
                        continue
                
                if not filled:
                    # 如果精确匹配失败，尝试模糊匹配
                    await self.page.fill(f'text={field_name}', str(value))
            except:
                # 如果找不到字段，记录下来
                print(f"Warning: Could not fill field '{field_name}'")
        
        # 点击提交按钮
        if submit_button_selector:
            try:
                await self.page.click(submit_button_selector)
                await self.page.wait_for_load_state("networkidle")
            except:
                # 尝试通用提交按钮
                try:
                    await self.page.click('text=提交 >> nth=0')
                except:
                    try:
                        await self.page.click('button[type="submit"]')
                    except:
                        # 尝试按Enter键
                        await self.page.press('body', 'Enter')
        
        return {"status": "form_filled_and_submitted"}
    
    async def take_screenshot(self, path="screenshot.png"):
        """截取屏幕截图"""
        if self.page is None:
            return {"error": "未打开任何页面"}
        
        await self.page.screenshot(path=path, full_page=True)
        return {"screenshot_path": path}
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()

async def main():
    """主函数，处理命令行输入"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "需要指定操作类型"}))
        return
    
    operation = sys.argv[1]
    browser_tool = EnhancedBrowserAutomation()
    
    try:
        if operation == "navigate":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "需要指定URL"}))
                return
            
            url = sys.argv[2]
            await browser_tool.navigate_to_url(url)
            content = await browser_tool.get_page_content()
            print(json.dumps(content, ensure_ascii=False, indent=2))
            
        elif operation == "search":
            if len(sys.argv) < 4:
                print(json.dumps({"error": "需要指定URL和搜索词"}))
                return
            
            url = sys.argv[2]
            search_term = sys.argv[3]
            await browser_tool.navigate_to_url(url)
            results = await browser_tool.search_and_extract(url, search_term)
            print(json.dumps(results, ensure_ascii=False, indent=2))
            
        elif operation == "extract":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "需要指定URL"}))
                return
            
            url = sys.argv[2]
            selectors_input = sys.argv[3] if len(sys.argv) > 3 else '{}'
            
            try:
                selectors = json.loads(selectors_input)
            except:
                selectors = {}
            
            await browser_tool.navigate_to_url(url)
            results = await browser_tool.search_and_extract(url, "", selectors)
            print(json.dumps(results, ensure_ascii=False, indent=2))
            
        elif operation == "screenshot":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "需要指定URL"}))
                return
            
            url = sys.argv[2]
            path = sys.argv[3] if len(sys.argv) > 3 else "screenshot.png"
            
            await browser_tool.navigate_to_url(url)
            result = await browser_tool.take_screenshot(path)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
        else:
            print(json.dumps({"error": "无效的操作类型。支持: navigate, search, extract, screenshot"}))
    
    finally:
        await browser_tool.close()

if __name__ == "__main__":
    asyncio.run(main())