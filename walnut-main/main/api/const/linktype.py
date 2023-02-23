"""
@File    ：linktype.py
@Author  ：Zhangweiyu
@Email   ：zhangweiyu@ones.ai
@Date    ：2022/7/21
@Desc    ：
"""


class SysLinkType:
    """"""
    UUID0001 = '关联'
    UUID0002 = '缺陷转需求'
    UUID0003 = '合并'
    UUID0004 = '工单转需求'
    UUID0005 = '需求拆解任务'


def name_to_key(name):
    """
    获取系统部默认关联类型的uuid
    :param name:  中文名字
    :return:
    """
    keys = [k for k in SysLinkType.__dict__.keys() if not k.startswith('__')]
    for k in keys:
        if getattr(SysLinkType, k) == name:
            return k
