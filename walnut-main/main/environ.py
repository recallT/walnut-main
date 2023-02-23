#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：environ.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/18 
@Desc    ：不同测试环境的数据类
"""
from falcons.com.env import EnvVars, User
from falcons.com.ones import private_login, api_login
from falcons.helper import functions as f
from falcons.helper.functions import read

from main.config import RunVars, DbConf

DEV_HOST = 'https://dev.myones.net'


class TestEnvVars(EnvVars):
    """Test 环境变量数据"""
    host = 'http://120.24.230.12'
    user = User('test@ones.ai', 'test1234')  # 测试用户
    team_uuid = 'Cui5JpzD'
    owner_uuid = 'AV8G6Ypr'

    member_uuid = '26x5CP1Z'


class Preview1EnvVars(EnvVars):
    """preview1环境变量数据"""
    host = 'https://preview1.myones.net'
    #
    user = User('wuxingjuan+01@ones.ai', 'juan1997')

    team_uuid = '44EdVsvX'

    member_uuid = '7tMnkPmX'
    owner_uuid = '7tMnkPmX'

    # user = User('automationtest@ones.cn', 'qweqwe123')
    #
    # team_uuid = 'UHb6Kru9'
    #
    # member_uuid = 'EPT6cckE'
    # owner_uuid = 'EPT6cckE'


class Preview2EnvVars(Preview1EnvVars):
    """preview2环境变量数据"""
    host = 'https://onesai.myones.net'


class Preview3EnvVars(Preview1EnvVars):
    """preview3环境变量数据"""
    host = 'https://preview3.myones.net'


class SaasEnvVars(Preview1EnvVars):
    """线上测试环境变量数据"""
    host = 'https://ones.cn'
    user = User('wuxingjuan+01@ones.ai', 'juan1997')
    team_uuid = '44EdVsvX'
    owner_uuid = '7tMnkPmX'
    member_uuid = '7tMnkPmX'


class PrivateEnvVars(EnvVars):
    """私有部署环境变量数据"""
    host = 'https://ones.cn'
    user = User('wuxingjuan+01@ones.ai', 'juan1997')
    team_uuid = '44EdVsvX'

    owner_uuid = '7tMnkPmX'  # 所有者

    member_uuid = '7tMnkPmX'  # 成员


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

class DevEnvVars(EnvVars):
    """dev环境变量数据"""
    host = DEV_HOST

    user = User('wuxingjuan@ones.ai', 'juan1997')

    team_uuid = 'Js3bNUir'

    member_uuid = '95sGjuY5'

    owner_uuid = '95sGjuY5'


class SprintS6029(DevEnvVars):
    """
    S6029 迭代的测试账号信息
    """
    user = User('jianjing@ones.ai', 'a123456789')
    team_uuid = '3VM4uGbD'
    member_uuid = 'Y66f73H3'
    owner_uuid = 'Y66f73H3'


class SprintP1038(DevEnvVars):
    """
    P1038 迭代的测试账号信息
    """
    user = User('zeno_account@ones.ai', 'Imok9999')
    team_uuid = '6atDBrmQ'
    member_uuid = 'D5R9VePb'
    owner_uuid = 'D5R9VePb'

    org_uuid = 'K4rzzZPY'  # 用于团队管理相关


class SprintP3034(DevEnvVars):
    """
    P3034 迭代的测试账号信息
    """
    user = User('419374961@qq.com', 'lu123456')
    team_uuid = 'SDvEb1rZ'
    member_uuid = '7CU6yrju'
    owner_uuid = '7CU6yrju'


class SprintMars:
    """
    account 临时环境 测试账号信息
    """
    host = 'https://mars-dev2.myones.net:10560'
    user = User('firstuser@ones.ai', 'Ones123123')
    login_user = User('marsdev@ones.ai', 'qmdzimXCWMTB806837')
    team_uuid = 'RoHyC4oL'
    member_uuid = 'YNVsVAyD'
    owner_uuid = 'YNVsVAyD'

    org_uuid = '7R2oDJ4A'  # 用于团队管理相关

    project_uuid = ''  # 项目uuid 用于接口测试
    project_uuid_ui = ''  # 项目uuid 用于UI测试


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*


# 新增测试迭代的账号配置后在这里添加映射
__sprint_mapper__ = {
    's6029': SprintS6029,
    'p1038': SprintP1038,
    'p3034': SprintP3034
}


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

class AbilityEnvVars(EnvVars):
    """ 能力自测 Test 环境变量数据"""
    host = 'http://120.76.45.123'
    user = User('test1@ones.ai', 'ibJDTEf7PET1')  # 测试用户
    team_uuid = 'RPWfqknE'
    owner_uuid = 'SMS8ciyv'

    # zeno = User('test2@ones.ai', '6XMcNN6J')  另外成员登录信息
    login_user = User('test1@ones.ai', 'ibJDTEf7PET1')
    member_uuid = 'SMS8ciyv'  # test2 的 uuid


class ConstantConf:
    """
    Global constant config
    """
    dev = DevEnvVars
    test = TestEnvVars
    preview1 = Preview1EnvVars
    preview2 = Preview2EnvVars
    preview3 = Preview3EnvVars
    private = PrivateEnvVars
    saas = SaasEnvVars

    ability = AbilityEnvVars
    mars = SprintMars

    @classmethod
    def update_sprint(cls, sprint):
        """Update sprint obj"""

        return __sprint_mapper__.get(sprint.lower())


def parse_member(member_info: str, private=None) -> dict:
    """

    :param member_info:
    :param private:
    :return:
    """
    members = member_info.split(',')
    l_m = len(members)

    if l_m >= 2:
        user = User(members[0], members[1])
        if private:
            auth_info = private_login(private, user)
        else:
            auth_info = api_login(user, all_token=True)
        _member = {
            'team_uuid': auth_info['teams'][0]['uuid'],
            'owner_uuid': auth_info['user']['uuid'],
            'org_uuid': auth_info['org']['uuid'],
            'private_host': private
        }

        if l_m == 3:
            # 直接获取 team_uuid
            _member['team_uuid'] = members[2]
            print(f'SET DEFAULT TEAM UUID: {members[2]}')

        return _member
    else:
        raise ValueError('账号参数格式错误！请按 邮箱,密码,所属团队UUID 填写')


def load_env_var(m_dict: dict, m_str):
    """
    加载EnvVar

    :param m_dict:账号信息 json 格式
    :param m_str: 由 pytest 参数传入的成员账号密码
    :return:EnvVars
    """
    _environ = DevEnvVars
    members = m_str.split(',')
    _environ.user = User(members[0], members[1])

    _environ.team_uuid = m_dict['team_uuid']
    _environ.member_uuid = m_dict['owner_uuid']
    _environ.owner_uuid = m_dict['owner_uuid']
    _environ.user.uuid = m_dict['owner_uuid']

    _environ.org_uuid = m_dict['org_uuid']

    if m_dict['private_host']:
        _environ.host = m_dict['private_host']

    return _environ


def gen_constant(env_option, save=False) -> EnvVars:
    """
    生成运行环境类

    :param env_option: 运行参数dict
    :param save: 是否保存到文件 默认为否
    :return:
    """
    sprint = env_option['sprint']
    member = env_option['member']
    private = env_option['private']

    if member:  # 如果传入来member信息，则直接从生成账号信息
        member_json = parse_member(member, private)
        if save:
            # 将用户信息写入文件
            f.write(RunVars.stamp_env, 'member.pkl', member_json)
        constant = load_env_var(member_json, member)

    else:  # 否则从 constant 中取预定义的账号数据

        if sprint and env_option['label'] == 'dev':
            constant = ConstantConf.update_sprint(sprint)
        else:
            constant = getattr(ConstantConf, env_option['label'])

    return constant


def analyze_options(env_ops, saving=False, reading=False):
    """
    生成运行环境参数

    :param env_ops: 运行参数字典
    :param saving: 保存到缓存 默认为否
    :param reading: 从缓存读 默认为否
    :return:
    """

    is_debug = env_ops.get('ones_debug', 0) or env_ops.get('one-debug', 0)

    if env_ops['private']:  # 如果传了 private 服务地址，就认为是private 环境
        env_ops |= {'label': 'private', }

    db = getattr(DbConf, env_ops['label'])

    # pytest 参数传入了用户账号信息时 直接获取环境配置信息
    # 否则在constant 模块获取用户配置信息
    # 当由 run.py 运行测试案例时，需要设置 ones_debug 为 0
    # 此时从 缓存文件 读取账号信息

    if env_ops['member'] and is_debug == 0 and reading:  # conftest.py goes
        print('Read env member info from cache ....')

        member_json = read(RunVars.stamp_env, 'member.pkl')
        constant = load_env_var(member_json, env_ops['member'])
    else:  # run.py goes
        constant = gen_constant(env_ops, save=saving)

    env_ops |= {
        'host': constant.host,
        'constant': constant,
        'db': db['mysql'],
        'ssh_config': db.get('ssh_config', None),
    }

    return env_ops


def show_env(env_option):
    """"""
    print('*' * 80,
          'Running Environment is:',
          f'[{env_option["label"]}][{env_option["host"]}]',
          '*' * 80,
          sep='\n')


class FieldType:
    """自定义属性的类型值"""
    option = 1  # string 选项，值为当前选中的选项uuid
    text = 2  # string 文本
    integer = 3  # int 整数 值 = 实际数值 x 100000
    float = 4  # float 浮点数 值 =
    date = 5
    time = 6
    milestone = 7
    user = 8
    # project = 9  # 废弃
    # task = 10 # 废弃
    # issue_type = 11 # 废弃
    task_status = 12
    user_list = 13
    # number = 14 # 废弃
    multi_line_text = 15
    multi_option = 16
    interval = 40  # 间隔时间
    stay_count = 41  # 属性选项停留次数
    stay_times = 42  # 属性选项停留时间
    appear_time = 45  # 出现时间


class ThirdPartyType:
    """
    标品第三方类型，注意不要使用超过200的值，超过200的将分配给插件使用
        TypeWechatISV   = 1
        TypeWechatAPP   = 7
        TypeLarkISV     = 11
        TypeLarkAPP     = 9
        TypeDingdingAPP = 2
        TypeLDAP        = 3
        TypeCAS         = 4
        TypeSAML        = 8
        TypeAPI         = 5
        TypeYoudu       = 10
        TypeGoogle      = 13
    """
    wechat_isv = 1
    wechat_app = 7
    lark_isv = 11
    ding_app = 2
    ldap = 3
    cas = 4
    saml = 8
    api = 5
    you_du = 10
    google = 13
