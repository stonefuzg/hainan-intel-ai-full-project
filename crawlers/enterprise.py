
import random
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json

def crawl_enterprises():
    """Crawl enterprise data from 爱企查 (aiqicha.baidu.com)
    
    Data source: https://aiqicha.baidu.com/s?q=海南
    Filter: 新成立企业
    Sort: 成立日期 (descending)
    Fields: 企业名称, 成立日期, 注册资本, 行业, 地址
    
    Note: 爱企查使用JavaScript动态加载数据，首先尝试API，失败则返回空列表
    """

    enterprises = []

    try:
        # 爱企查搜索接口
        url = "https://aiqicha.baidu.com/s"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://aiqicha.baidu.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        # 查询参数
        params = {
            'q': '海南',  # 地区
            'sort': 'establish',  # 按成立日期排序
            'pageIndex': '1'
        }

        # 尝试直接请求爱企查页面
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 爱企查的列表项选择器（多个可能的选择器）
        selectors = [
            'div.list-item',
            'li.result-item',
            'div.company-item',
            'div[data-company]',
        ]
        
        company_list = None
        for selector in selectors:
            company_list = soup.select(selector)
            if company_list:
                print(f"[企业爬虫] 使用选择器找到 {len(company_list)} 条记录: {selector}")
                break
        
        if not company_list:
            print("[企业爬虫信息] 无法从爱企查解析到企业数据，尝试备选本地数据源...")
            return []
        
        # 遍历企业列表
        for item in company_list[:10]:  # 获取前10条
            try:
                # 尝试多个可能的选择器来提取数据
                
                # 企业名称
                name = None
                for name_selector in ['a.com-name', 'a.title', '.company-name']:
                    name_elem = item.select_one(name_selector)
                    if name_elem:
                        name = name_elem.get_text(strip=True)
                        break
                
                if not name:
                    continue
                
                # 成立日期
                establish_date = None
                for date_selector in ['.establish-date', '.register-date', 'span[data-field="establish"]']:
                    date_elem = item.select_one(date_selector)
                    if date_elem:
                        establish_date = date_elem.get_text(strip=True)
                        break
                
                if not establish_date:
                    establish_date = datetime.now().strftime("%Y-%m-%d")
                
                # 注册资本
                capital = 0
                for capital_selector in ['.reg-capital', '.capital', 'span[data-field="capital"]']:
                    capital_elem = item.select_one(capital_selector)
                    if capital_elem:
                        capital_text = capital_elem.get_text(strip=True)
                        capital = parse_capital(capital_text)
                        break
                
                # 行业
                industry = "未分类"
                for industry_selector in ['.industry', '.industryco', 'span[data-field="industry"]']:
                    industry_elem = item.select_one(industry_selector)
                    if industry_elem:
                        industry = industry_elem.get_text(strip=True)
                        break
                
                # 地址
                address = "未知"
                for address_selector in ['.address', '.region', 'span[data-field="address"]']:
                    address_elem = item.select_one(address_selector)
                    if address_elem:
                        address = address_elem.get_text(strip=True)
                        break
                
                # 构建企业数据对象
                enterprise = {
                    "name": name,
                    "industry": industry,
                    "capital": capital,
                    "registration_number": "",
                    "registration_date": establish_date,
                    "region": extract_region(address),
                    "legal_form": "",
                    "business_scope": "",
                    "status": "存续",
                    "phone": "",
                    "address": address,
                    "website": "",
                    "employees": "",
                    "annual_revenue": "",
                    "data_source": "爱企查(aiqicha.baidu.com)"
                }
                
                enterprises.append(enterprise)
                
            except Exception as e:
                print(f"[企业爬虫] 解析单条数据失败: {e}")
                continue
        
        if not enterprises:
            print("[企业爬虫信息] 成功连接爱企查但无有效数据，返回空列表")
            return []

    except requests.Timeout:
        print("[企业爬虫错误] Timeout: 爱企查响应超时，请检查网络连接")
        return []
    except requests.ConnectionError as e:
        print(f"[企业爬虫错误] ConnectionError: 无法连接到爱企查 - {e}")
        return []
    except requests.HTTPError as e:
        print(f"[企业爬虫错误] HTTPError: {e}")
        return []
    except Exception as e:
        # Log error without returning fake data
        error_msg = f"[企业爬虫错误] {type(e).__name__}: {str(e)}"
        print(error_msg)
        return []  # Return empty list instead of fake data

    return enterprises


def parse_capital(capital_text):
    """从文本中解析注册资本（转换为万元）
    
    Examples:
        "1000万" -> 1000
        "1000万元" -> 1000
        "100万" -> 100
        "暂无数据" -> 0
    """
    if not capital_text or capital_text in ["暂无数据", "未知"]:
        return 0
    
    try:
        # 移除空格和括号
        text = capital_text.strip()
        
        # 提取数字部分
        import re
        numbers = re.findall(r'[\d.]+', text)
        if not numbers:
            return 0
        
        value = float(numbers[0])
        
        # 根据单位转换
        if '亿' in text:
            value = value * 10000  # 亿转万
        elif '千万' in text:
            value = value * 1000  # 千万转万
        elif '万' in text or '元' in text:
            pass  # 已经是万或转换为万
        else:
            # 如果是普通数字，假设已经是万元
            pass
        
        return int(value)
    except:
        return 0


def extract_region(address):
    """从地址中提取地区（市级）
    
    Examples:
        "海南省海口市..." -> "海口市"
        "海南海口..." -> "海口市"
    """
    if not address:
        return "海南"
    
    # 海南主要城市列表
    hainan_cities = [
        "海口市", "三亚市", "儋州市", "琼海市", "文昌市", 
        "万宁市", "东方市", "五指山市", "定安县", "屯昌县",
        "澄迈县", "临高县", "白沙县", "昌江县", "乐东县",
        "陵水县", "保亭县", "琼中县"
    ]
    
    # 在地址中查找城市名
    for city in hainan_cities:
        if city in address:
            return city
    
    # 如果是"海南"开头，尝试提取市名
    if address.startswith("海南"):
        parts = address[2:6]
        if parts:
            return parts
    
    return "海南"
