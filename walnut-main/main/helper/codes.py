import time

from falcons.com.meta import ApiMeta
from falcons.helper.mysql import MysqlOps, sql_executor


def get_db_config():
    """"""
    db = {
        'db': ApiMeta.env.mysql,
        'ssh_config': ApiMeta.env.ssh_config,
        'sprint': ApiMeta.env.sprint,
    }

    return db


def table_prefix(config: dict) -> str:
    """"""
    brh = config.pop('sprint')

    _db = config['db'].db
    if _db:
        prefix = f'project_{_db}.'
    else:
        prefix = f'project_{brh.lower()}.' if brh else 'project.'

    return prefix


def get_phone_code(phone):
    """
    注册团队时，获取手机验证码
    Args:
        phone(type: string +86手机号):注册团队时，使用的手机号码
    returns:
        phone_code 表中该手机号对应的验证码
    """
    sql = "SELECT `code` FROM {prefix}phone_code WHERE phone='{phone}';"
    r = RunSql()
    return r.run_sql(sql, phone, k='phone')


def reset_passwd_code(email):
    """
    重置密码时，获取邮箱验证码
    Args:
        email(type: string):注册的邮箱
    returns:
        reset_code 表中该邮箱对应的重置密码的验证码
    """
    r = RunSql()

    sql = "SELECT `code` FROM {prefix}reset_password_code WHERE email='{email}' and status=1 limit 1;"
    for _ in range(10):
        """"""
        m = r.run_sql(sql, email)
        if not m:
            time.sleep(2)
            continue

        return m
    else:
        raise AssertionError('重置密码code 未入库！')


def get_email_code(email):
    """
    激活邮箱时，获取邮箱验证码
    Args:
        email(type: string):注册的邮箱
    returns:
        email_code 表中该邮箱对应的激活邮箱的验证码
    """

    sql = "SELECT `code` FROM {prefix}email_code WHERE email='{email}' limit 1;"
    r = RunSql()
    return r.run_sql(sql, email)


def get_request_code(email):
    """
    修改邮箱时，获取邮箱验证码
    Args:
        email(type: string):要替换成的新邮箱
    returns:
        request_code 表中新邮箱的验证码
    """
    sql = "SELECT `code` FROM {prefix}request_code WHERE email='{email}' limit 1;"
    r = RunSql()
    return r.run_sql(sql, email)


def get_field_option_code(team_uuid, option_uuid):
    """
    获取属性选项的值

    """
    sql = f"select fo.uuid from field_option fo where fo.team_uuid ='{team_uuid}' and fo.field_uuid  ='{option_uuid}';"
    r = RunSql()
    return r.run(sql)


def get_member_uuid():
    """获取待激活用户"""
    r = RunSql()
    sql = """select uuid from {prefix}user where status = 3  limit 1;"""  # 从用户表中取一个待激活的用户
    uuid = r.run(sql)

    return uuid[0]['uuid']


class RunSql:
    def __init__(self):
        self.config = get_db_config()
        self.prefix = table_prefix(self.config)

    def run_sql(self, sql, *args, k='email'):
        """"""

        sql = sql.format(**{'prefix': self.prefix, k: args[0]})
        print(f'Execute sql: [{sql}]')

        def executor(cursor):
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                return result['code']

        return sql_executor(self.config, executor)

    def run(self, sql):
        """
        执行sql语句
        :param sql:  sql 中的表需要带有{prefix} 参数
        :return:
        """

        sql = sql.format(**{'prefix': self.prefix})

        db = MysqlOps(self.config)

        return db.execute_sql(sql)
