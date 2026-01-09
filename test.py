import requests
from bs4 import BeautifulSoup

# 获取用户输入的网址
url = input("请输入网址: ")

try:
    # 发送 GET 请求获取网页内容
    response = requests.get(url)
    response.raise_for_status()  # 如果状态码不是 200，会抛出异常
    
    # 自动检测并设置正确的编码
    if response.encoding is None or response.encoding == 'ISO-8859-1':
        response.encoding = response.apparent_encoding
    
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取标题
    title = soup.find('title')
    
    if title:
        print(f"网页标题: {title.string}")
    else:
        print("未找到网页标题")
        
except requests.exceptions.RequestException as e:
    print(f"请求出错: {e}")
except Exception as e:
    print(f"发生错误: {e}")
