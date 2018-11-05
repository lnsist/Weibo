# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class UserItem(Item):
    """
        用户详情
    """
    # 数据库表名
    collection = "users"
    # 用户ID
    id = Field()
    # 用户名
    name = Field()
    # 头像图片路径
    avatar = Field()
    # 封面图片路径
    cover = Field()
    # 性别
    gender = Field()
    # 描述
    description = Field()
    # 微博总数
    weibos_count = Field()
    # 是否已验证
    verified = Field()
    # 微博验证信息
    verified_reason = Field()
    # 验证类型
    verified_type = Field()
    # 关注总数
    follows_count = Field()
    # 用户关注列表
    follows = Field()
    # 粉丝总数
    fans_count = Field()
    # 用户粉丝列表
    fans = Field()
    # 爬取时间
    crawled_at = Field()


class UserRelationItem(Item):
    """
        用户关系
    """
    # 数据库表名
    collection = "users"
    # 用户ID
    id = Field()
    # 关注列表
    follows = Field()
    # 粉丝列表
    fans = Field()


class WeiboItem(Item):
    # 数据库表名
    collection = "weibos"
    # 微博ID
    id = Field()
    # 点赞总数
    attitudes_count = Field()
    # 评论总数
    comments_count = Field()
    # 转发总数
    reposts_count = Field()
    # 正文图片
    picture = Field()
    # 所有图片
    pictures = Field()
    # 来源
    source = Field()
    # 正文
    text = Field()
    # 转发正文
    raw_text = Field()
    # 缩略图
    thumbnail = Field()
    # 微博用户
    user = Field()
    # 创建时间
    created_at = Field()
    # 爬取时间
    crawled_at = Field()
