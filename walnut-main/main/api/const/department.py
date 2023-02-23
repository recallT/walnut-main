"""
@File    ：department.py
@Author  ：Zeno
@Email   ：zhangweiyu@ones.ai
@Date    ：2022/7/20
@Desc    ：
"""


class SysDepartment:
    """"""
    department001 = '已禁用'
    department002 = '未激活成员'
    department003 = '未分配部门'


def name_to_key(name):
    """
    获取系统部默认部门的uuid
    :param name:  中文名字
    :return:
    """
    keys = [k for k in SysDepartment.__dict__.keys() if not k.startswith('__')]
    for k in keys:
        if getattr(SysDepartment, k) == name:
            return k
