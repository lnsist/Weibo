# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json
import logging

import requests
from scrapy import signals


class WeiboSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WeiboDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CookiesMiddleware(object):
    """
        Cookies 中间件
    """

    def __init__(self, cookies_url):
        """
            初始化
        :param cookies_url: Cookies 路径
        """
        # 日志
        self.logger = logging.getLogger(__name__)
        # Cookies路径
        self.cookies_url = cookies_url

    @classmethod
    def from_crawler(cls, crawler):
        """
            实例化
        :param crawler: 全局对象
        :return:
        """
        # 获取settings配置文件
        settings = crawler.settings
        # 返回Cookies路径实例化
        return cls(cookies_url=settings.get("COOKIES_URL"))

    def get_random_cookies(self):
        """
            获取随机Cookies
        :return: 随机Cookies
        """
        # 捕抓异常
        try:
            # 请求Cookies路径, 获取响应
            response = requests.get(self.cookies_url)
            # 如果获取成功
            if response.status_code == 200:
                # 响应 json转格式dict
                cookies = json.loads(response.text)
            # 返回 Cookies
            return cookies
        # 请求连接异常
        except requests.ConnectionError:
            #
            return False

    def process_request(self, request, spider):
        """
            爬虫请求访问前
        :param request: 请求
        :param spider: 爬虫
        :return:
        """
        # 写日志
        self.logger.debug("正在获取 Cookies")
        # 获取Cookies
        cookies = self.get_random_cookies()
        # 如果获取成功
        if cookies:
            # 设置请求Cookies
            request.cookies = cookies
            # 写日志
            self.logger.debug("使用 Cookies " + json.dumps(cookies))


class ProxyMiddleware(object):
    """
        代理 中间件
    """

    def __init__(self, proxy_url):
        """
            初始化
        :param proxy_url: 代理 路径
        """
        # 日志
        self.logger = logging.getLogger(__name__)
        # 代理 路径
        self.proxy_url = proxy_url

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(proxy_url=settings.get("PROXY_URL"))

    def get_random_proxy(self):
        """
            获取随机 代理
        :return: 随机 代理
        """
        # 捕抓异常
        try:
            # 请求 代理 路径, 获取响应
            response = requests.get(self.proxy_url)
            # 如果获取成功
            if response.status_code == 200:
                # 响应 json转格式dict
                proxy = json.loads(response.text)
            # 返回 代理
            return proxy
        # 请求连接异常
        except requests.ConnectionError:
            #
            return False

    def process_request(self, request, spider):
        """
            爬虫请求访问前
        :param request: 请求
        :param spider: 爬虫
        :return:
        """
        # 如果已经出现失败次数, 才设置代理
        if request.meta.get("retry_times"):
            # 写日志
            self.logger.debug("正在获取 代理")
            # 获取 代理
            proxy = self.get_random_proxy()
            # 如果获取成功
            if proxy:
                # 格式化代理
                uri = "https://{proxy}".format(proxy=proxy)
                # 写日志
                self.logger.debug("使用 代理 " + proxy)
                # 设置代理
                request.meta["poxy"] = uri
