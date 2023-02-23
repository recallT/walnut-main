#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：config.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/23 
@Desc    ：
"""
import os

from falcons.com.env import RuntimeConfig
from falcons.com.meta import MysqlDb

_p_ = os.path

# 工作目录重新赋值为项目根目录
RuntimeConfig.working_path = _p_.abspath(_p_.join(_p_.dirname(__file__), _p_.pardir))


class RunConfig(RuntimeConfig):
    """"""
    wechat_hook = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1ee9e732-c6b3-499a-8c5c-434c1a13e833'

    # dev 扫码机器人通知
    login_hook = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a6492651-f9f4-4f63-9396-19ee211b4080'
    dev_host = 'https://dev.myones.net'


# 全局配置实例
RunVars = RunConfig()


class DbConf:
    develop = {
        'mysql': MysqlDb('119.23.130.213', 'onesdev', 'onesdev', db='preview2'),
        # 'ssh_config': SshConfig('119.23.130.213', 'ones-test', 8022),
    }
    preview1 = {
        'mysql': MysqlDb('119.23.130.213', 'onesdev', 'onesdev', db='preview1'),
        # 'ssh_config': SshConfig('119.23.130.213', 'ones-test', 8022),
    }
    preview2 = {
        'mysql': MysqlDb('119.23.130.213', 'onesdev', 'onesdev', db='preview2'),
        # 'ssh_config': SshConfig('119.23.130.213', 'ones-test', 8022),
    }
    preview3 = {
        'mysql': MysqlDb('119.23.130.213', 'onesdev', 'onesdev', db='preview2'),
        # 'ssh_config': SshConfig('119.23.130.213', 'ones-test', 8022),
    }
    saas = {  # 临时的 其时无用
        'mysql': MysqlDb('119.23.130.213', 'onesdev', 'onesdev', db='preview1'),
        # 'ssh_config': SshConfig('119.23.130.213', 'ones-test', 8022),
    }
    dev = {
        'mysql': MysqlDb('119.23.130.213', 'onesdev', 'onesdev'),
        # 'ssh_config': SshConfig('119.23.130.213', 'ones-test', 8022), dev 环境不用ssh
    }
    test = {
        'mysql': MysqlDb('172.18.26.238', 'test', 'test1234'),
        # 'ssh_config': SshConfig('120.24.230.12', 'zeno', 22),
    }
    private = {
        'mysql': MysqlDb('127.0.0.1', 'root', 'ones@123.'),  # 不用数据库操作
        # 'ssh_config': SshConfig('120.24.230.12', 'zeno', 22),
    }
    ability = {
        'mysql': MysqlDb('127.0.0.1', 'root', 'XkHZOFiJUhQY9Ic'),  # 不用数据库操作
    }
    honor = {
        'mysql': MysqlDb('127.0.0.1', 'root', 'XkHZOFiJUhQY9Ic'),  # 不用数据库操作
    }
    mars = {
        'mysql': MysqlDb('127.0.0.1', 'root', 'ones@123.'),  # 不用数据库操作
    }
