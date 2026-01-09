#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆瓣电影Top250爬虫
功能：抓取豆瓣电影Top250的所有电影标题
特性：自动处理中文乱码，User-Agent伪装，错误处理
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import csv
from urllib.parse import urljoin

class DoubanTop250Spider:
    def __init__(self):
        # 豆瓣Top250的基础URL
        self.base_url = "https://movie.douban.com/top250"
        
        # 模拟真实浏览器User-Agent，避免403错误
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',  # requests 会自动处理 gzip 解压
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # 存储所有电影信息
        self.movies = []
        
        # 请求会话，保持cookie连接和会话状态
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 记录上一页URL，用于设置Referer
        self.previous_url = None
    
    def get_page(self, url, retry_times=3):
        """
        获取网页内容，自动处理中文乱码和重试机制
        
        Args:
            url: 请求的URL
            retry_times: 重试次数
            
        Returns:
            str: 页面HTML内容
        """
        for attempt in range(retry_times):
            try:
                # 添加随机延迟，避免请求过快被封
                time.sleep(random.uniform(1, 3))
                
                # 设置 Referer 头，模拟真实翻页
                current_headers = self.headers.copy()
                if self.previous_url:
                    # 如果不是第一页，设置 Referer 为上一页URL
                    current_headers['Referer'] = self.previous_url
                else:
                    # 第一页的 Referer 设置为豆瓣首页
                    current_headers['Referer'] = 'https://www.douban.com/'
                
                # 使用 Session 发送请求，保持会话状态
                # requests 会自动处理 gzip 压缩解压
                response = self.session.get(url, headers=current_headers, timeout=10)
                
                # 打印响应状态码，方便排查问题
                print(f"响应状态码: {response.status_code}")
                print(f"Content-Encoding: {response.headers.get('Content-Encoding', 'None')}")
                
                # 检查响应状态码
                if response.status_code == 403:
                    print(f"访问被拒绝 (403)，可能是反爬机制触发，第{attempt + 1}次重试...")
                    print(f"当前使用的 User-Agent: {self.headers['User-Agent'][:80]}...")
                    # 更换User-Agent重试
                    self.rotate_user_agent()
                    continue
                
                # 检查其他HTTP错误并打印详细错误信息
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    print(f"HTTP错误！状态码: {response.status_code}")
                    print(f"错误详情: {e}")
                    print(f"响应内容前100字符: {response.text[:100]}")
                    raise
                
                # 打印响应内容前100字符，用于调试
                print(f"响应内容前100字符: {response.text[:100]}")
                
                # 自动检测并设置正确的编码
                # requests 已经自动处理了 gzip 解压，这里只需要处理编码
                if response.encoding == 'ISO-8859-1' or response.encoding is None:
                    # 豆瓣通常使用UTF-8编码
                    response.encoding = 'utf-8'
                elif response.encoding is None:
                    # 尝试从HTML中获取编码信息
                    response.encoding = response.apparent_encoding
                
                # 更新上一页URL，用于下次请求的Referer
                self.previous_url = url
                
                return response.text
                
            except requests.exceptions.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/{retry_times}): {e}")
                if attempt < retry_times - 1:
                    time.sleep(random.uniform(2, 5))
                else:
                    raise
    
    def rotate_user_agent(self):
        """轮换User-Agent，避免被识别为爬虫"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
        ]
        self.headers['User-Agent'] = random.choice(user_agents)
        self.session.headers.update(self.headers)
        print(f"已更换User-Agent为: {self.headers['User-Agent'][:50]}...")
    
    def parse_movie_info(self, soup, rank_start=1):
        """
        解析电影信息
        
        Args:
            soup: BeautifulSoup对象
            rank_start: 起始排名
            
        Returns:
            list: 电影信息列表
        """
        movies = []
        
        # 查找所有电影条目 - 确保使用类名为 item 的 div
        movie_items = soup.find_all('div', class_='item')
        print(f"找到 {len(movie_items)} 个电影条目")
        
        for index, item in enumerate(movie_items, rank_start):
            try:
                # 提取电影排名
                rank = index
                
                # 提取电影标题 - 直接查找 span 类名为 title 的第一个文本
                title_span = item.find('span', class_='title')
                if title_span:
                    main_title = title_span.get_text(strip=True)
                else:
                    main_title = "未知标题"
                
                # 查找英文标题（可选）
                english_title = ""
                other_spans = item.find_all('span', class_='other')
                if other_spans:
                    english_title = other_spans[0].get_text(strip=True)
                
                # 提取评分 - 直接查找 span 类名为 rating_num 的文本
                rating_span = item.find('span', class_='rating_num')
                if rating_span:
                    rating = rating_span.get_text(strip=True)
                else:
                    rating = "未知评分"
                
                # 提取评价人数
                rating_div = item.find('div', class_='star')
                people = "未知"
                if rating_div:
                    all_spans = rating_div.find_all('span')
                    if len(all_spans) > 3:  # 通常最后一个span是评价人数
                        people = all_spans[-1].get_text(strip=True)
                
                # 提取引用
                quote = ""
                quote_span = item.find('span', class_='inq')
                if quote_span:
                    quote = quote_span.get_text(strip=True)
                
                movie_info = {
                    'rank': rank,
                    'title': main_title,
                    'english_title': english_title,
                    'rating': rating,
                    'people': people,
                    'quote': quote
                }
                
                movies.append(movie_info)
                print(f"成功解析: {rank}. {main_title} ({rating})")
                
            except Exception as e:
                print(f"解析第{index}部电影时出错: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        return movies
    
    def scrape_all_pages(self):
        """爬取所有页面的数据"""
        print("开始爬取豆瓣电影Top250（前3页，共75部电影）...")
        
        # 重置 previous_url，从第一页开始
        self.previous_url = None
        
        # 只爬取前3页，每页25部电影，共75部
        total_pages = 3
        movies_per_page = 25
        
        for page in range(total_pages):
            # 构造分页URL
            start = page * movies_per_page
            url = f"{self.base_url}?start={start}"
            
            print(f"\n正在爬取第{page + 1}页: {url}")
            
            try:
                # 获取页面内容
                html_content = self.get_page(url)
                
                # 解析HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 解析电影信息
                page_movies = self.parse_movie_info(soup, rank_start=start + 1)
                self.movies.extend(page_movies)
                
                print(f"第{page + 1}页爬取完成，共获取{len(page_movies)}部电影")
                
                # 每爬完一页随机暂停1-3秒，防止被封IP
                if page < total_pages - 1:  # 最后一页不需要延迟
                    delay = random.uniform(1, 3)
                    print(f"随机暂停 {delay:.2f} 秒后继续...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"第{page + 1}页爬取失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n爬取完成！共获取{len(self.movies)}部电影信息")
        return self.movies
    
    def save_to_csv(self, filename='douban_top250.csv'):
        """将结果保存到CSV文件"""
        if not self.movies:
            print("没有数据可保存")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['rank', 'title', 'english_title', 'rating', 'people', 'quote']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for movie in self.movies:
                    writer.writerow(movie)
            
            print(f"数据已保存到 {filename}")
        except Exception as e:
            print(f"保存文件时出错: {e}")
    
    def display_results(self, limit=10):
        """显示爬取结果"""
        if not self.movies:
            print("没有数据可显示")
            return
        
        print(f"\n{'='*80}")
        print(f"豆瓣电影Top250 - 前{min(limit, len(self.movies))}名")
        print(f"{'='*80}")
        
        for movie in self.movies[:limit]:
            print(f"{movie['rank']:3d}. {movie['title']}")
            if movie['english_title']:
                print(f"     英文标题: {movie['english_title']}")
            print(f"     评分: {movie['rating']} | {movie['people']}")
            if movie['quote']:
                print(f"     推荐语: {movie['quote']}")
            print()


def main():
    """主函数"""
    try:
        # 创建爬虫实例
        spider = DoubanTop250Spider()
        
        # 开始爬取
        spider.scrape_all_pages()
        
        # 显示结果
        spider.display_results(limit=15)
        
        # 保存到CSV文件
        spider.save_to_csv('douban_top250.csv')
        
        print("爬取任务完成！")
        
    except KeyboardInterrupt:
        print("\n用户中断爬取")
    except Exception as e:
        print(f"程序运行出错: {e}")


if __name__ == "__main__":
    main()
