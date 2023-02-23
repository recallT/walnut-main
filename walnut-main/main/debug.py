"""
@File    ：debug.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/21
@Desc    ： *****默认调试环境-自定义环境账号信息
            *****本地开发的环境都在这里配置
            *****避免影响environ.py 模块的预定义环境
"""

import os
from typing import Type

import yaml
from falcons.com.env import EnvVars, User


def load_development_config():
    """"""
    path = os.path.dirname(__file__)
    try:
        with open(f'{os.path.abspath(path)}/env.yaml', 'r') as c:
            env = c.read()

            return yaml.safe_load(env)
    except FileNotFoundError:
        raise FileNotFoundError('env.yaml 配置文件没找到，请在当前目录添加该文件并配置好环境信息！')


def gen_env() -> Type[EnvVars]:
    """生成测试环境类"""

    env_dict = load_development_config()
    e = EnvVars
    user = env_dict.pop('user')
    u = User(user['name'], user['password'])
    e.user = u

    for k, v in env_dict.items():
        if k in e.__dict__:
            setattr(e, k, v)

    return e


gen_env()


class DevelopEnv(EnvVars):
    """默认调试环境--这里什么都不用改"""
