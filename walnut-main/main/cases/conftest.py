#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：conftest.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/18 
@Desc    ：案例全局的conftest
"""
import re

import pytest
from falcons.com.meta import UiMeta, ApiMeta
from falcons.com.ones import unify_login
from falcons.const import env_setup, account_setup
from falcons.helper import mocks
from falcons.helper.functions import read

from main.analyse import analyze_options
from main.config import RunVars
from main.helper.extra import Extra
from main.helper.testcase_listener import data_processing, update_test_plan


def pytest_addoption(parser):
    """Add run options here"""

    # -*-*-*-*-*-*-*-*-*-*-*-*-测试环境配置参数-*-*-*-*-*-*-*-*-*-*-*-*-
    parser.addoption('--host', dest='host', default='develop', help='指定执行环境')

    parser.addoption('--sprint', dest='sprint', type=str, default='', help='指定测试迭代后端分支')

    parser.addoption('--sprint-front', dest='sprint-front', type=str, default='',
                     help='指定测试前端迭代分支 默认为空 即前后端分支一致')

    parser.addoption('--headless', dest='headless', type=int, default=0,
                     help='指定浏览器无头模式')

    parser.addoption('--anv', dest='allure_env', type=int, default=1,
                     help='生成allure env 环境文件')

    parser.addoption('--remote', dest='remote', type=int, default=0,
                     help='使用远程浏览器')

    parser.addoption('--browser', dest='browser', action='store',
                     choices=['chrome', 'firefox', 'ie', 'safari'], default='chrome',
                     help='指定UI浏览器')

    parser.addoption('--p-uuid', dest='p-uuid', help='接口测试项目uuid')

    parser.addoption('--ui-uuid', dest='ui-uuid', help='UI测试项目uuid')

    parser.addoption('--ui-name', dest='ui-name', help='UI测试项目名称')

    parser.addoption('--ones-debug', dest='ones-debug', type=int, default=1,
                     help='是否调试项目')

    parser.addoption('--exclude-project', dest='exclude-project', type=str, default='',
                     help='忽略的项目UUID, 多个项目UUID 以英文逗号[,]隔开')

    parser.addoption('--member', dest='member', type=str, default='',
                     help='测试用户（管理员角色）：[邮箱,密码,所属团队UUID] 逗号分割')

    parser.addoption('--private', dest='private', type=str, default='',
                     help='私有部署环境地址')

    parser.addoption('--language', dest='language', type=str, default='zh',
                     help='系统语言版本,中文 zh,英文 en, 默认中文')

    parser.addoption('--single', dest='single', type=int, default='1',
                     help='是否用pytest执行，默认是，1, 否 0 ')
    parser.addoption('--plan-uuid', dest='plan_uuid', type=str, default='',
                     help='关联测试计划UUID ')


def _set_env(config):
    """初始化环境信息"""
    _ops = config.getoption
    env_ops = {
        'label': _ops("--host"),
        # 区分前后端迭代分支
        # DEV环境存在前后端分支不一致的部署情况
        # 先处理后端/project项目分支部分
        # 其他后端分支暂不处理

        # 后端分支
        'sprint': _ops("--sprint"),
        # 前端分支
        'sprint_front': _ops("--sprint-front"),
        'browser': _ops("--browser"),
        'headless': _ops("--headless"),
        'anv': _ops("--anv"),
        'remote': _ops("--remote"),

        'project_uuid': _ops("--p-uuid"),
        'project_uuid_ui': _ops("--ui-uuid"),
        'proj_name': _ops('--ui-name'),

        'debug': _ops('--ones-debug'),
        'member': _ops('--member'),
        'private': _ops('--private'),

        'language': _ops('--language'),
        'single': _ops('--single'),
        'plan_uuid': _ops('--plan-uuid'),

    }
    # SET HOST SPRINT
    env_setup(env_ops, 'api')
    if env_ops['private']:
        ApiMeta.env.host = env_ops['private']

    if env_ops['label'] == 'dev':
        ApiMeta.env.host = RunVars.dev_host

    # pytest 参数传入了用户账号信息时 直接获取环境配置信息
    # 否则在constant 模块获取用户配置信息
    # 当由 run.py 运行测试案例时，需要设置 ones_debug 为 0
    # 此时从 缓存文件读取账号信息

    env_ops = analyze_options(env_ops, reading=True)

    # debug 状态同步 以 constant 为准
    if getattr(env_ops['constant'], 'debug', None):
        env_ops['debug'] = env_ops['constant'].debug
    # run.py
    if env_ops['plan_uuid']:
        env_ops['constant'].plan_uuid = env_ops['plan_uuid']
    return env_ops


def pytest_configure(config):
    """Set runtime env globally..."""
    env_ops = _set_env(config)

    env_setup(env_ops, 'api')
    env_setup(env_ops, 'ui')

    # 更新 account 账号信息
    account_setup(ApiMeta.account, env_ops['constant'])
    ApiMeta.account.project_uuid = env_ops['project_uuid']

    print(f'DEBUG: ApiMeta- {ApiMeta.env.debug} < > UiMeta -{UiMeta.env.debug}')
    print('Now Plan UUID:', ApiMeta.env.plan_uuid)


@pytest.hookspec(firstresult=True)
def pytest_collection(session):
    """
    调试用例时自动生成测试项目
    pytest_collection 这个fixture 在用例收集阶段执行

    根据 ons-debug 参数的值来判断， 是否创建全局的测试项目

    1：直接创建项目UUID和stamp信息
    0：参数传入项目UUID和名称，并读取项目stamp信息（使用run.py并行执行用例时）
    2：不创建

    :param session:
    :return:
    """
    if ApiMeta.env.debug == 1:
        """本地调试时自动创建项目"""
        prepare_projects()
    elif ApiMeta.env.debug == 0:
        # Load user token

        token = read(RunVars.stamp_env, 'token.pkl')
        ApiMeta.account.user.token = token['Ones-Auth-token']
        ApiMeta.account.user.member_uuid = token['Ones-User-Id']
        ApiMeta.account.user.owner_uuid = token['Ones-User-Id']

        ApiMeta.account.stamp_data = read(RunVars.stamp_env, 'stamp.pkl')

    else:
        set_token()
        print('Now stamp data is None.')


passed = []
failed = []


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # 获取钩子方法的调用结果
    out = yield
    report = out.get_result()
    global passed, failed
    if report.when == "call":
        story_info = [r.args for r in item.own_markers if r.name == 'allure_label'
                      and r.kwargs['label_type'] == 'story']
        uuids = []
        for r in story_info:
            case_id = re.findall(r"\d+\.?\d*", r[0])
            uuids += case_id

        if report.outcome == 'passed':
            passed += uuids
        elif report.outcome == 'failed':
            failed += uuids


def set_token():
    """"""
    _user = ApiMeta.account
    token = unify_login(_user.user)
    print(f'Token: {token}')

    _user.user.token = token['Ones-Auth-token']
    _user.user.uuid = token['Ones-User-Id']


def prepare_projects():
    """
    准备测试用例所需的项目
    创建两个测试项目，一个用于接口测试，一个用于UI测试
    默认情况下，所有用例都基于这些项目

    有个性化项目需求的，需要在其用例的前置条件中生成新的项目

    :return:
    """
    print('Prepare Default Test Projects...')
    set_token()

    init = Extra(ApiMeta)
    # 创建项目前关闭配置中心中的通知
    print("Close Global Notify")
    # init.close_notify()
    print('Create New Project....')

    # dev 和 私有部署环境 都切换为本地视图
    if ApiMeta.env.label == 'private' or 'dev' in ApiMeta.env.host:
        init = Extra(ApiMeta)
        init.switch_local_layout()

    uid = mocks.ones_uuid().capitalize()

    u_name = f'敏捷UI{uid[4:]}'
    UiMeta.env.proj_name = u_name
    pro_uuid = init.new_project(f'ApiTest{uid[:4]}')
    # 刘佛添: 结论：按团队级别隔离，1分钟内调用20次，最小间隔为1秒
    print('Wait 15 seconds....')
    # time.sleep(10.5)
    pro_uuid_ui = init.new_project(UiMeta.env.proj_name)

    if not pro_uuid or not pro_uuid_ui:
        raise RuntimeError('Create project failed, please check your environment is ok.')

    # save project uuid
    UiMeta.env.proj_name = u_name
    UiMeta.env.project_uuid_ui = pro_uuid_ui
    ApiMeta.account.project_uuid = pro_uuid

    print(f'UI name :{u_name}')

    # save stamp
    init.team_stamp()


def pytest_collection_modifyitems(items):
    """终端显示中文乱码问题"""
    for item in items:  # stdout  中文乱码问题
        item.name = item.name.encode().decode('unicode-escape')
        item._nodeid = item._nodeid.encode().decode('unicode-escape')


# -*******-*******-*******-*******-*******-*******-*******-*******-*******-*******


@pytest.fixture(scope='session', autouse=True)
def clean_data():
    """
    在全局用例执行完成后执行测试数据清理动作

    根据 ones-debug 参数来判断
    1： 执行数据清理
    0：由run.py 执行全局清理
    2：不执行
    :return:
    """
    yield

    """将结果反写到测试计划中 目前只记录成功 失败"""
    if ApiMeta.env.plan_uuid:
        plan_uuid = ApiMeta.env.plan_uuid
        # 组装数据
        data = {"passed": passed, "failed": failed}
        # 执行更新测试计划操作
        case_param = data_processing(data, plan_uuid)
        update_test_plan(case_param, plan_uuid)

    if ApiMeta.env.debug == 1:
        print('Clear test data finally...')
        init = Extra(ApiMeta)
        uuid = ApiMeta.account.project_uuid
        uuid_ui = UiMeta.env.project_uuid_ui

        init.teardown(uuid, uuid_ui)

    mocks.remove_images(RunVars.tmp_files)


@pytest.fixture(scope='session')
def admin_token(constants):
    """
    用户登录的头部token信息

    这是某一个测试用户的token
    不同用户，需要实现不同的fixture

    :return:
    """
    return unify_login(constants.account.user)


@pytest.fixture(scope='session')
def ignore_project(request):
    """
    忽略的项目UUID LIST

    在清除测试项目时使用

    :return:
    """
    exclude = request.config.getoption('--exclude-project')
    if exclude:
        ep = [e.strip() for e in exclude.split(',')]
    else:
        ep = []
    return ep


@pytest.fixture(scope='session', name='constants')
def env_constants():
    """
    :return:
    """
    return ApiMeta

# -*******-*******-*******-*******-*******-*******-*******-*******-*******-*******
