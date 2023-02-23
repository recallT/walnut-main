"""
@File    ：analyse.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/6/22
@Desc    ：
"""
from falcons.com.env import User
from falcons.helper import functions as f

from main.config import DbConf, RunVars
from main.environ import DevEnvVars, EnvVars, parse_member, ConstantConf


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
        if env_option['label'] == 'develop':
            from main.debug import DevelopEnv
            constant = DevelopEnv
            # 本地调试模式时 将前后端迭代号更新到测试参数中去
            env_option.update({
                'sprint': constant.sprint,
                'sprint_front': constant.sprint_front,
                'plan_uuid': constant.plan_uuid,
            })
        elif sprint and env_option['label'] == 'dev':
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

    is_debug = env_ops.get('debug', 0) or env_ops.get('ones-debug', 0)
    single = env_ops.get('single')

    if env_ops['private']:  # 如果传了 private 服务地址，就认为是private 环境
        env_ops |= {'label': 'private', }

    # 数据库连接
    db = getattr(DbConf, env_ops['label'])

    # pytest 参数传入了用户账号信息时 直接获取环境配置信息
    # 否则在constant 模块获取用户配置信息
    # 当由 run.py 运行测试案例时，需要设置 ones_debug 为 0
    # 此时从 缓存文件 读取账号信息

    if all((env_ops['member'], is_debug == 0, reading, not single)):  # conftest.py goes
        print('Read env member info from cache ....')

        member_json = f.read(RunVars.stamp_env, 'member.pkl')
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
