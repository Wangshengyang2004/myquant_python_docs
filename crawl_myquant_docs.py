"""
掘金量化 Python SDK 文档爬虫
自动爬取所有文档并保存为 Markdown 格式
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from pathlib import Path
import html2text

# 完整的文档列表（按照官网菜单顺序）
DOCS_TO_CRAWL = [
    # 基础入门 (1-7)
    {"num": "01", "name": "快速开始", "url": "https://www.myquant.cn/docs2/sdk/python/快速开始.html"},
    {"num": "02", "name": "策略程序架构", "url": "https://www.myquant.cn/docs2/sdk/python/策略程序架构.html"},
    {"num": "03", "name": "变量约定", "url": "https://www.myquant.cn/docs2/sdk/python/变量约定.html"},
    {"num": "04", "name": "数据结构", "url": "https://www.myquant.cn/docs2/sdk/python/数据结构.html"},
    {"num": "05", "name": "基本函数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/基本函数.html"},
    {"num": "06", "name": "数据订阅", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/数据订阅.html"},
    {"num": "07", "name": "数据事件", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/数据事件.html"},

    # 数据查询函数 (8-15)
    {"num": "08", "name": "行情数据查询函数（免费）", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/行情数据查询函数（免费）.html"},
    {"num": "09", "name": "通用数据函数（免费）", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/通用数据函数（免费）.html"},
    {"num": "10", "name": "股票财务数据及基础数据函数（免费）", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/股票财务数据及基础数据函数（免费）.html"},
    {"num": "11", "name": "股票增值数据函数（付费）", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/股票增值数据函数（付费）.html"},
    {"num": "12", "name": "期货基础数据函数（免费）", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/期货基础数据函数（免费）.html"},
    {"num": "13", "name": "期货增值数据函数（付费）", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/期货增值数据函数（付费）.html"},
    {"num": "14", "name": "基金增值数据函数（付费）", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/基金增值数据函数（付费）.html"},
    {"num": "15", "name": "可转债增值数据函数（付费）", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/可转债增值数据函数（付费）.html"},

    # 交易函数 (16-23)
    {"num": "16", "name": "交易函数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/交易函数.html"},
    {"num": "17", "name": "交易查询函数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/交易查询函数.html"},
    {"num": "18", "name": "两融交易函数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/两融交易函数.html"},
    {"num": "19", "name": "算法交易函数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/算法交易函数.html"},
    {"num": "20", "name": "新股新债交易函数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/新股新债交易函数.html"},
    {"num": "21", "name": "基金交易函数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/基金交易函数.html"},
    {"num": "22", "name": "债券交易函数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/债券交易函数.html"},
    {"num": "23", "name": "交易事件", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/交易事件.html"},

    # 其他工具 (24-29)
    {"num": "24", "name": "动态参数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/动态参数.html"},
    {"num": "25", "name": "标的池", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/标的池.html"},
    {"num": "26", "name": "其他函数", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/其他函数.html"},
    {"num": "27", "name": "其他事件", "url": "https://www.myquant.cn/docs2/sdk/python/API介绍/其他事件.html"},
    {"num": "28", "name": "枚举常量", "url": "https://www.myquant.cn/docs2/sdk/python/枚举常量.html"},
    {"num": "29", "name": "错误码", "url": "https://www.myquant.cn/docs2/sdk/python/错误码.html"},
]


def setup_driver():
    """初始化 Chrome WebDriver"""
    chrome_options = Options()

    # 反检测设置
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 模拟真实浏览器
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')

    # 可选：无头模式
    # chrome_options.add_argument('--headless=new')

    driver = webdriver.Chrome(options=chrome_options)

    # 修改 navigator.webdriver 标志
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
        '''
    })

    return driver


def extract_html_content(driver):
    """提取页面主要内容的 HTML"""
    selectors = [
        "//article",
        "//main",
        "//*[@class='content']",
        "//*[@class='markdown-body']",
        "//*[@id='content']"
    ]

    for selector in selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            if elements:
                html_content = elements[0].get_attribute('innerHTML')
                if html_content and len(html_content) > 100:
                    return html_content
        except:
            continue

    # 如果以上都失败，返回整个 body
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        return body.get_attribute('innerHTML')
    except:
        return None


def html_to_markdown(html_content):
    """将 HTML 转换为 Markdown"""
    import re

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # 不自动换行
    h.unicode_snob = True
    h.skip_internal_links = True

    markdown = h.handle(html_content)

    # 使用正则表达式过滤掉不需要的文本（包括前后的空白字符）
    unwanted_patterns = [
        r'\s*复制成功\s*',
        r'\s*复制失败\s*',
        r'\s*点击复制\s*',
        r'\s*已复制\s*',
        r'\s*copy\s+success\s*',
        r'\s*\n\s*复制成功\s*\n\s*',  # 单独一行的复制成功
    ]

    for pattern in unwanted_patterns:
        markdown = re.sub(pattern, '', markdown, flags=re.IGNORECASE)

    # 清理多余的空行（连续超过2个换行符）
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    return markdown


def crawl_page(driver, doc_info, output_dir):
    """爬取单个页面并保存为 Markdown"""
    num = doc_info["num"]
    name = doc_info["name"]
    url = doc_info["url"]

    print(f"\n{'='*80}")
    print(f"[{num}] 正在爬取: {name}")
    print(f"URL: {url}")
    print(f"{'='*80}")

    try:
        # 访问页面
        driver.get(url)

        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)

        # 获取页面标题
        title = driver.title
        print(f"页面标题: {title}")

        # 检查是否是错误页面
        if "404" in title or "undefined" in title:
            print(f"⚠ 页面不存在")
            return False

        # 提取 HTML 内容
        html_content = extract_html_content(driver)
        if not html_content:
            print(f"✗ 未能提取内容")
            return False

        # 转换为 Markdown
        markdown_content = html_to_markdown(html_content)

        if len(markdown_content) > 500:
            # 添加文档头部信息
            full_markdown = f"""# {name}

> **来源**: {url}
> **标题**: {title}

---

{markdown_content}
"""

            # 保存为 Markdown 文件
            output_file = output_dir / f"{num}_{name}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_markdown)

            print(f"✓ 已保存 ({len(markdown_content)} 字符)")
            return True
        else:
            print(f"✗ 内容太短: {len(markdown_content)} 字符")
            return False

    except Exception as e:
        print(f"✗ 爬取失败: {e}")
        return False


def main():
    """主函数"""
    # 创建输出目录
    output_dir = Path("myquant_python_docs_md")
    output_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("掘金量化 Python SDK 文档爬虫")
    print(f"输出目录: {output_dir.absolute()}")
    print(f"文档总数: {len(DOCS_TO_CRAWL)}")
    print("=" * 80)

    # 初始化 WebDriver
    driver = setup_driver()

    success_count = 0
    fail_count = 0
    results = []

    try:
        for i, doc_info in enumerate(DOCS_TO_CRAWL, start=1):
            print(f"\n进度: {i}/{len(DOCS_TO_CRAWL)}")

            if crawl_page(driver, doc_info, output_dir):
                success_count += 1
                results.append(f"✓ [{doc_info['num']}] {doc_info['name']}")
            else:
                fail_count += 1
                results.append(f"✗ [{doc_info['num']}] {doc_info['name']}")

            # 页面间随机等待，避免请求过快
            if i < len(DOCS_TO_CRAWL):
                wait_time = random.uniform(2, 4)
                print(f"等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)

        # 打印结果摘要
        print(f"\n{'='*80}")
        print(f"爬取完成！")
        print(f"{'='*80}")
        print(f"成功: {success_count} 个")
        print(f"失败: {fail_count} 个")
        print(f"\n详细结果:")
        for result in results:
            print(f"  {result}")
        print(f"{'='*80}")

        # 生成索引文件
        generate_index(output_dir, results)

    finally:
        time.sleep(2)
        driver.quit()


def generate_index(output_dir, results):
    """生成索引文件"""
    from datetime import datetime

    index_content = f"""# 掘金量化 Python SDK 文档

> **爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **文档来源**: https://www.myquant.cn/docs2/sdk/python/

## 📊 统计信息

- **文档总数**: {len(DOCS_TO_CRAWL)} 个
- **文件格式**: Markdown (.md)
- **成功爬取**: {sum(1 for r in results if r.startswith('✓'))} 个
- **失败**: {sum(1 for r in results if r.startswith('✗'))} 个

## 📚 文档列表

### 基础入门 (1-7)

"""

    # 按分类添加文档链接
    categories = [
        ("基础入门", 1, 7),
        ("数据查询函数", 8, 15),
        ("交易函数", 16, 23),
        ("其他工具", 24, 29)
    ]

    for i, (category, start, end) in enumerate(categories):
        if i > 0:
            index_content += f"\n### {category} ({start}-{end})\n\n"

        for doc in DOCS_TO_CRAWL:
            num = int(doc["num"])
            if start <= num <= end:
                filename = f"{doc['num']}_{doc['name']}.md"
                status = "✓" if any(r.startswith(f"✓ [{doc['num']}]") for r in results) else "✗"
                index_content += f"{num}. {status} [{doc['name']}](./{filename})\n"

    index_content += f"""
## 📝 使用说明

1. 所有文档已转换为 Markdown 格式，便于阅读和搜索
2. 点击上方链接可直接跳转到对应文档
3. 建议使用支持 Markdown 的编辑器查看

## 🔄 更新文档

重新运行爬虫脚本即可更新所有文档：

```bash
python3 crawl_myquant_docs.py
```

## 📄 原始链接

所有文档均来自掘金量化官方文档：https://www.myquant.cn/docs2/sdk/python/
"""

    # 保存索引文件
    with open(output_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"\n✓ 索引文件已生成: {output_dir / 'README.md'}")


if __name__ == "__main__":
    main()