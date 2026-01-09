基于 Python 的自动化网页标题提取工具

一个简单易用的 Python 工具，用于自动提取任意网页的标题（Title）。支持自动识别网页编码，完美解决中文乱码问题。

项目简介
本项目是一个轻量级的网页标题提取工具，通过输入网址即可快速获取网页的标题信息。工具具有以下特点：
简单易用，只需输入网址即可
自动识别网页编码，完美支持中文显示
完善的错误处理机制
轻量级，依赖库少

技术栈
 **Python 3.x** - 编程语言
 **Requests** - 用于发送 HTTP 请求，获取网页内容
 **BeautifulSoup4** - 用于解析 HTML 文档，提取标题信息
 
在网页爬取过程中，中文乱码是一个常见问题。本项目通过以下方式完美解决了这个问题：
问题原因
1. 网页服务器返回的响应头中可能没有明确指定编码
2. Requests 库默认使用 `ISO-8859-1` 编码，无法正确解析中文网页
3. 不同网站可能使用不同的编码格式（UTF-8、GBK、GB2312 等）
解决方案
使用 Requests 库的 `apparent_encoding` 属性自动检测网页的实际编码：
```python
# 自动检测并设置正确的编码
if response.encoding is None or response.encoding == 'ISO-8859-1':
    response.encoding = response.apparent_encoding
```

工作原理：
`apparent_encoding` 会分析响应内容的字节流，自动推断出最可能的编码格式
当检测到编码未正确识别时（`None` 或 `ISO-8859-1`），自动使用检测到的编码
这样就能正确解析各种编码格式的网页，包括 UTF-8、GBK、GB2312 等中文编码

如何运行

1. 环境要求：Python 3.6 或更高版本

2. 安装依赖
使用 pip 安装所需的依赖库：

```bash
pip install requests beautifulsoup4
```

3. 运行程序

在终端中运行脚本：
```bash
python test.py
```

4. 使用示例
运行程序后，按提示输入网址：

```
请输入网址: https://www.baidu.com
网页标题: 百度一下，你就知道
```

代码说明
程序的主要流程：
1. **获取用户输入** - 通过 `input()` 函数获取用户输入的网址
2. **发送 HTTP 请求** - 使用 `requests.get()` 获取网页内容
3. **自动检测编码** - 使用 `apparent_encoding` 自动识别网页编码
4. **解析 HTML** - 使用 BeautifulSoup 解析 HTML 文档
5. **提取标题** - 查找并提取 `<title>` 标签的内容
6. **错误处理** - 完善的异常处理机制，确保程序稳定运行

注意事项
- 确保网络连接正常
- 某些网站可能有反爬虫机制，可能无法正常访问
- 输入网址时请包含协议（如 `https://` 或 `http://`）

许可证
本项目采用 MIT 许可证。

贡献
欢迎提交 Issue 和 Pull Request！
