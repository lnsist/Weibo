# -*- coding: utf-8 -*-
"""
    微博爬虫 -- 爬取一个用户的信息, 微博列表, 粉丝列表, 关注列表
再从粉丝列表和关注列表, 爬取某个用户的信息, 微博列表, 粉丝列表, 关注列表...循环爬取信息
"""
import json
import scrapy
from scrapy import Request
from scrapy.http import Response

from Weibo.items import *


class MweibocnSpider(scrapy.Spider):
    """
        微博爬虫
    """
    # 爬虫名称
    name = 'mweibocn'
    # 域名
    allowed_domains = ['m.weibo.cn']
    # 起始url
    start_urls = ['http://m.weibo.cn/']
    # 用户信息 API
    user_url = "https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}"
    # 关注列表 API
    follow_url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}"
    # 粉丝列表 API
    fan_url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}"
    # 微博列表 API
    weibo_url = "https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}"
    # 开始用户ID
    start_users = ["3217179555", "1742566624", "2282991915", "1288739185", "3952070245", "5878659096"]

    def start_requests(self):
        """
            开始请求访问
        :return:
        """
        for uid in self.start_users:
            yield Request(self.user_url.format(uid=uid), callback=self.parse_user)

    def parse_user(self, response):
        """
            解析用户信息
        :return:
        """
        # 用户信息API响应结果 -- json转为dict
        result = json.loads(response.text)
        # 判断是否成功获取正确据
        if result.get("data").get("userInfo"):
            # 获取用户信息
            user_info = result.get("data").get("userInfo")
            # 实例化 用户Item
            user_item = UserItem()
            # 字段属性对应字典 -- k=Item属性, v=响应结果属性
            field_map = {
                "id": "id", "name": "screen_name", "avatar": "profile_image_url", "cover": "cover_image_phone",
                "gender": "gender", "description": "description", "fans_count": "followers_count",
                "follows_count": "follow_count", "weibos_count": "statuses_count", "verified": "verified",
                "verified_reason": "verified_reason", "verified_type": "verified_type"
            }
            # 循环 字段属性对应字典 field=Item属性, attr=响应结果属性
            for field, attr in field_map.items():
                # 封装用户Item -- 从响应结果中获取数据 ( 默认值为空 "" )
                user_item[field] = user_info.get(attr, "")
            # 生成返回 用户Item
            yield user_item
            # 获取用户ID
            uid = user_info.get("id")
            # 生成返回 解析关注列表, 回调函数, 携带参数
            # yield Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows, meta={"page": 1, "uid": uid})
            # 生成返回 解析粉丝列表, 回调函数, 携带参数 -- 粉丝太多了,,, 不爬取
            # yield Request(self.fan_url.format(uid=uid, page=1), callback=self.parse_fans, meta={"page": 1, "uid": uid})
            # 生成返回 解析微博列表, 回调函数, 携带参数
            yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos, meta={"page": 1, "uid": uid})

    def parse_follows(self, response):
        """
            解析关注列表
        :param response:
        :return:
        """
        # 设置类型 方便智能提醒
        response = response  # type: Response
        # 关注列表API响应结果 -- json转dict
        result = json.loads(response.text)
        # 判断是否成功获取正确数据
        if result.get("ok") and result.get("data").get("cards") and len(result.get("data").get("cards")) and result.get("data").get("cards")[-1].get("card_group"):
            # 获取 全部关注 数据
            user_follows = result.get("data").get("cards")[-1].get("card_group")
            # 循环全部关注数据
            for follow in user_follows:
                # 判断是否有用户信息
                if follow.get("user"):
                    # 获当前关注用户ID
                    follow_uid = follow.get("user").get("id")
                    # 生成返回 -- 用户信息API请求
                    yield Request(self.user_url.format(uid=follow_uid), callback=self.parse_user)
                # 获取回调函数的用户ID -- 当前微博用户ID
                uid = response.meta.get("uid")
                # 用户关系Item
                user_relation_item = UserRelationItem()
                # 列表生成式 -- 生成全部关注中的每个关注用户ID和名称
                rel_follows = [{"id": rel.get("user").get("id"), "name": rel.get("user").get("screen_name")} for rel in user_follows]
                # 封装用户关系的微博用户ID
                user_relation_item["id"] = uid
                # 当前微博用户的关注
                user_relation_item["follows"] = rel_follows
                # 当前微博用户的粉丝
                user_relation_item["fans"] = []
                # 生成返回 用户关系Item
                yield user_relation_item
                # 获取 当前API请求页码 + 1
                page = response.meta.get("page") + 1
                # 生成返回 -- 当前微博用户的下一页关注列表
                yield Request(self.follow_url.format(uid=uid, page=page), callback=self.parse_follows, meta={"uid": uid, "page": page})

    def parse_fans(self, response):
        """
            解析粉丝列表
        :param response:
        :return:
        """
        # 设置类型 方便智能提醒
        response = response  # type: Response
        # 粉丝列表API响应结果 -- json转dict
        result = json.loads(response.text)
        # 判断是否成功获取正确数据
        if result.get("ok") and result.get("data").get("cards") and len(result.get("data").get("cards")) and result.get("data").get("cards")[-1].get("card_group"):
            # 获取 全部粉丝 数据
            user_fans = result.get("data").get("cards")[-1].get("card_group")
            # 循环全部粉丝数据
            for fans in user_fans:
                # 判断是否有用户信息
                if fans.get("user"):
                    # 获当前粉丝用户ID
                    fans_id = fans.get("user").get("id")
                    # 生成返回 -- 用户信息API请求
                    yield Request(self.user_url.format(uid=fans_id), callback=self.parse_user)
                # 获取回调函数的用户ID -- 当前微博用户ID
                uid = response.meta.get("uid")
                # 用户关系Item
                user_relation_item = UserRelationItem()
                # 列表生成式 -- 生成全部粉丝中的每个粉丝用户ID和名称
                rel_fans = [{"id": rel.get("user").get("id"), "name": rel.get("user").get("screen_name")} for rel in user_fans]
                # 封装用户关系的微博用户ID
                user_relation_item["id"] = uid
                # 当前微博用户的关注
                user_relation_item["follows"] = []
                # 当前微博用户的粉丝
                user_relation_item["fans"] = rel_fans
                # 生成返回 用户关系Item
                yield user_relation_item
                # 获取 当前API请求页码 + 1
                page = response.meta.get("page") + 1
                # 生成返回 -- 当前微博用户的下一页关注列表
                yield Request(self.fan_url.format(uid=uid, page=page), callback=self.parse_fans, meta={"uid": uid, "page": page})

    def parse_weibos(self, response):
        """
            解析微博列表
        :param response:
        :return:
        """
        # 设置类型 方便智能提醒
        response = response  # type: Response
        # 微博列表API响应结果 -- json转dict
        result = json.loads(response.text)
        # 判断是否成功获取正确数据
        if result.get("ok") and result.get("data").get("cards"):
            # 获取 微博列表 数据
            weibos = result.get("data").get("cards")
            # 循环 微博列表
            for weibo in weibos:
                # 获取具体微博数据
                mblog = weibo.get("mblog")
                # 如果有微博数据
                if mblog:
                    # 实例化 微博Item
                    weibo_item = WeiboItem()
                    # 字段属性对应字典 -- k=Item属性, v=响应结果属性
                    field_map = {
                        "id": "id", "attitudes_count": "attitudes_count", "comments_count": "comments_count",
                        "reposts_count": "reposts_count", "picture": "original_pic", "pictures": "pics",
                        "source": "source", "text": "text", "raw_text": "raw_text", "thumbnail": "thumbnail_pic",
                        "created_at": "created_at"
                    }

                    # 循环 字段属性对应字典 field=Item属性, attr=响应结果属性
                    for field, attr in field_map.items():
                        # 封装微博Item -- 从响应结果中获取数据 ( 默认值为空 "" )
                        weibo_item[field] = mblog.get(attr, "")
                    # 设置此条微博的用户ID
                    weibo_item["user"] = response.meta.get("uid")
                    # 生成返回 微博Item
                    yield weibo_item
            # 获取回调函数的用户ID -- 当前微博用户ID
            uid = response.meta.get("uid")
            # 获取 当前API请求页码 + 1
            page = response.meta.get("page") + 1
            # 生成返回 -- 当前微博用户的下一页微博列表
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos, meta={"uid": uid, "page": page})
