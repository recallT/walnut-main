#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：run.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/11/18 
@Desc    ：
"""
import argparse
import subprocess
import time

import gevent
from falcons.com.meta import ApiMeta, UiMeta
from falcons.com.ones import unify_login, set_allure_env
from falcons.const import env_setup, account_setup
from falcons.helper import functions as f
from falcons.helper import mocks
from gevent.pool import Pool

from main.analyse import analyze_options, show_env
from main.config import RunVars
from main.helper.extra import Extra

parser = argparse.ArgumentParser(description='自定义命令行参数')

parser.add_argument('--cases', dest='cases', help='指定测试案例目录')

parser.add_argument('--host', dest='host', default='dev',
                    help='指定执行环境')

parser.add_argument('--sprint', dest='sprint', type=str, default='',
                    help='指定测试迭代/分支')

parser.add_argument('--sprint-front', dest='front', type=str, default='',
                    help='指定测试前端迭代分支 默认为空 即前后端分支一致')

parser.add_argument('--headless', dest='headless', type=int, default=0,
                    help='指定浏览器无头模式')

parser.add_argument('--anv', dest='allure_env', type=int, default=0,
                    help='生成allure env 环境文件')

parser.add_argument('--remote', dest='remote', type=int, default=0,
                    help='使用远程浏览器')

parser.add_argument('--ignore', dest='ignore', type=str, default='',
                    help='忽略的用例集 模糊匹配模块信息, 多条信息按英文逗号隔开')

parser.add_argument('--browser', dest='browser', action='store',
                    choices=['chrome', 'firefox', 'ie', 'safari'], default='chrome',
                    help='指定UI浏览器')

parser.add_argument('--member', dest='member', type=str, default='',
                    help='测试用户（管理员角色）：[邮箱,密码,所属团队UUID] 逗号分割')

parser.add_argument('--private', dest='private', type=str, default='',
                    help='私有部署环境地址')

parser.add_argument('--language', dest='language', type=str, default='zh',
                    help='系统语言版本,中文 zh,英文 en, 默认中文')

parser.add_argument('--plan-uuid', dest='plan_uuid', type=str, default='',
                    help='关联测试计划UUID ')

parser.add_argument('--marking', dest='marking', type=str, default='',
                    help='pytest mark 标记 默认为空 ')


def _set_env():
    running_args = parser.parse_args()
    env_ops = {
        'label': running_args.host,
        'sprint': running_args.sprint,
        'sprint-front': running_args.front,
        'browser': running_args.browser,
        'headless': running_args.headless,
        'anv': running_args.allure_env,
        'remote': running_args.remote,
        'cases': running_args.cases,
        'member': running_args.member,
        'private': running_args.private,
        'language': running_args.language,
        'ones-debug': 0,  # 直接为0
        'plan-uuid': running_args.plan_uuid,
        'marking': running_args.marking,

    }
    # SET HOST SPRINT
    env_setup(env_ops, 'api')
    if env_ops['private']:
        ApiMeta.env.host = env_ops['private']

    s_front = env_ops['sprint-front']
    if s_front:
        ApiMeta.env.sprint_front = s_front
    if env_ops['label'] == 'dev':
        ApiMeta.env.host = RunVars.dev_host
    # 更新 account 账号信息
    # account_setup(ApiMeta.account, env_ops['constant'])
    env_ops = analyze_options(env_ops, saving=True)

    return env_ops


def environs():
    env_ops = _set_env()
    show_env(env_ops)

    env_setup(env_ops, 'api')
    env_setup(env_ops, 'ui')

    # 更新 account 账号信息
    account_setup(ApiMeta.account, env_ops['constant'])
    return env_ops


def executor(item, env: dict):
    """

    :param item:
    :param env:
    :return:
    """
    m = []

    for k, v in env.items():  # 添加pytest运行参数
        if k not in ('db', 'ssh_config', 'cases', 'constant', 'label', 'marking'):
            m.append(f'--{k}={v}')
        if k == 'marking':
            m.append(f'-m={env["marking"]}')

    cmd = 'pytest'
    # if platform.system().lower() == 'linux':
    #     cmd = 'pytest'
    command = [f'{cmd}', f'{item[1]}', '-v',
               '--clean-alluredir',
               '--alluredir',
               f'tmp/allure/{item[0]}',
               # '--ones-debug=0',
               '--single', '0',
               '--reruns=2', '--reruns-delay=2'] + m  # Add rerun args

    print('Running command:', ' '.join(command))

    subprocess.call(command)


def setup():
    """Create projects for all test"""
    _env = environs()
    print('Set Default Token...')

    token = unify_login(ApiMeta.account.user)

    # RECORD USER TOKEN TO ApiMeta.account.user
    print(f'Token: {token}')
    ApiMeta.account.user.token = token['Ones-Auth-token']
    ApiMeta.account.user.member_uuid = token['Ones-User-Id']

    # Save User Token
    f.write(RunVars.stamp_env, 'token.pkl', token)

    print('Create New Project')
    init = Extra(ApiMeta)

    # dev 和 私有部署环境 都切换为本地视图
    if ApiMeta.env.label == 'private' or 'dev' in ApiMeta.env.host:
        init = Extra(ApiMeta)
        init.switch_local_layout()

    uid = mocks.ones_uuid().capitalize()

    ui_name = f'敏捷UI{uid[4:]}'
    UiMeta.env.proj_name = ui_name

    pro_uuid = init.new_project(f'ApiTest{uid[:4]}')
    # 刘佛添: 结论：按团队级别隔离，1分钟内调用20次，最小间隔为1秒
    # 另外 间隔最小10秒
    time.sleep(11)
    pro_uuid_ui = init.new_project(ui_name)

    # save project uuid
    ApiMeta.account.project_uuid = pro_uuid
    UiMeta.env.project_uuid_ui = pro_uuid_ui

    stamps = init.team_stamp()

    f.write(RunVars.stamp_env, 'stamp.pkl', stamps)

    print('p_uuid', ApiMeta.account.project_uuid)
    print('ui_uuid', UiMeta.env.project_uuid_ui)

    _env |= {'p-uuid': pro_uuid, 'ui-uuid': pro_uuid_ui, 'host': _env['label'], 'ui-name': ui_name}

    return _env


def teardown(env):
    """全局测试数据清理"""
    if env['anv']:
        print('Set Allure Environment..')

    set_allure_env(RunVars.allure_path, **env)

    print('Delete test project....')
    init = Extra(ApiMeta)
    uuid = ApiMeta.account.project_uuid
    uuid_ui = UiMeta.env.project_uuid_ui

    init.teardown(uuid, uuid_ui)

    mocks.remove_images(RunVars.tmp_files)


if __name__ == '__main__':
    # 解析运行命令参数
    args = parser.parse_args()
    cases = args.cases

    ignore = args.ignore
    ignore = ignore.split(',') if ignore else []
    files = f.collect_module(cases)

    if ignore:  # 过滤掉不执行的模块
        files = [f for f in files if not any(i in f[1] for i in ignore)]

    files_amount = len(files)

    ui_flag = [c for c in files if 'ui_' in c]
    ui_pool = 20 if ui_flag else files_amount  # UI 测试，协程池限制小一点，系统资源有限

    start = time.time()

    e = setup()

    if files:
        pool = Pool(min((RunVars.max_pool, ui_pool, files_amount)))  # 协程池

        tasks = []

        for i in range(files_amount):
            tasks.append(pool.spawn(executor, files[i], e))

        gevent.joinall(tasks)
        end = time.time()

        teardown(e)
        print(f'Execute Done! Take {round((end - start))} secs.')
