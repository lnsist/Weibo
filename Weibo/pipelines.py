# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import time

import pymongo

from Weibo.items import *


class WeiboPipeline(object):
    """
        微博项目管道
    """

    def process_item(self, item, spider):
        # 判断当前Item -- 微博Item
        if isinstance(item, WeiboItem):
            # 如果created_at 有数据
            if item.get("created_at"):
                # 去空格
                item["created_at"] = item["created_at"].strip()
                # 格式化时间
                item["created_at"] = self.parse_time(item.get("created_at"))
        # 判断当前Item -- 用户Item 或 微博Item
        if isinstance(item, UserItem) or isinstance(item, WeiboItem):
            # 格式化当前时间
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # 设置爬取时间 为 当前时间
            item["crawled_at"] = now
        # 返回item
        return item

    @staticmethod
    def parse_time(date):
        """
            处理时间 -- 获取具体日期
        :param date: 时间
        :return: 具体日期
        """
        # 格式化后的日期
        datetime = ""

        # 刚刚
        if re.match("刚刚", date):
            # 格式 yyyy-mm-dd H:M:S   时间  当前时间秒数
            datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        # xx 分钟前
        if re.match("\d+分钟前", date):
            # 获取具体分钟数
            miute = re.match("(\d+)", date).group()
            # 格式 yyyy-mm-dd H:M:S   时间  当前时间秒数 减去 (分钟数 * 60秒)秒
            datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - float(miute) * 60))

        # xx 小时前
        if re.match("\d+小时前", date):
            # 获取具体小时数
            hour = re.match("(\d+)", date).group()
            # 格式 yyyy-mm-dd H:M:S   时间  当前时间秒数 减去 (小时数 * 60分 * 60秒)秒
            datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - float(hour) * 60 * 60))

        # 昨天
        if re.match("昨天.*", date):
            day = re.match("昨天(.*)", date).group().strip()
            # 格式 yyyy-mm-dd   时间  当前时间秒数 减去 1天(24小时 * 60分 * 60秒)秒 加上 具体时分秒
            datetime = time.strftime("%Y-%m-%d", time.localtime - 24 * 60 * 60) + " " + day

        # 确切时间 m月-d日 H时:M分
        if re.match("\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}", date):
            # 格式 yyyy-  时间  当前时间秒数的年份 加上 确切时间
            datetime = time.strftime("%Y-", time.localtime()) + date

        # 确切时间 Y年-m月-d日
        if re.match("\d{4}-\d{1,2}-\d{1,2}", date):
            # 直接返回
            datetime = date

        # 返回具体日期
        return datetime


class MongoPipeline(object):
    """
        数据库管道
    """

    def __init__(self, mongo_uri, mongo_db):
        """
            初始化
        :param mongo_uri: 数据库地址
        :param mongo_db: 数据库名称
        """
        # 数据库地址
        self.mongo_uri = mongo_uri
        # 数据库名称
        self.mongo_db = mongo_db
        # 数据库客户端
        self.client = None
        # 数据库
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        """
            创建数据库管道
        :param crawler: 全局对象
        :return:
        """
        # 返回数据库管道 -- 从配置文件获取信息
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE")
        )

    def open_spider(self, spider):
        """
            爬虫打开时
        :param spider: 爬虫
        :return:
        """
        # 获取数据库客户端连接
        self.client = pymongo.MongoClient(self.mongo_uri)
        # 获取 数据库
        self.db = self.client[self.mongo_db]
        # 获取数据库表   create_index 创建索引, 提高检索效率
        self.db[UserItem.collection].create_index([("id", pymongo.ASCENDING)])
        # 获取数据库表   create_index 创建索引, 提高检索效率
        self.db[WeiboItem.collection].create_index([("id", pymongo.ASCENDING)])

    def close_spider(self, spider):
        """
            爬虫关闭时
        :param spider: 爬虫
        :return:
        """
        # 关闭数据库
        self.client.close()

    def process_item(self, item, spider):
        """
            数据处理
        :param item: Item
        :param spider: 爬虫
        :return:
        """
        # 如果Item 是 用户Item 或 微博Item
        if isinstance(item, UserItem) or isinstance(item, WeiboItem):
            # 根据ID更新数据, 没有数据, 则插入数据
            # {"id": item.get("id")} -- 查询条件
            # {"$set": item} -- "$set" 如果存在则更新 item 数据
            # True -- 如果数据不存在, 则插入数据
            self.db[item.collection].update({"id": item.get("id")}, {"$set": item}, True)
        # 如果Item 是 用户关系Item
        if isinstance(item, UserRelationItem):
            # 根据ID跟新数据, 没有数据, 则插入数据
            # "$addToSet" -- 插入数据同时去重 k=需要操作的字段
            # "$each" -- 遍历插入数据
            # True -- 如果数据不存在, 则插入数据
            self.db[item.collection].update({"id": item.get("id")},
                                            {"$addToSet": {
                                                "follows": {"$each": item["follows"]},
                                                "fans": {"$each": item["fans"]}
                                            }}, True)
        return item

