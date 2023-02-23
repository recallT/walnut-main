"""
@File    ：field.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/17
@Desc    ：
"""


class SysField:
    """"""
    field001 = '标题'
    field002 = '描述'
    field003 = '创建者'
    field004 = '负责人'
    field005 = '状态'
    field006 = '所属项目'
    field007 = '工作项类型'
    field008 = '关注者'
    field009 = '创建时间'
    field010 = '更新时间'
    field011 = '所属迭代'
    field012 = '优先级'
    field013 = '截止日期'
    field014 = '父工作项'
    field015 = '工作项编号'
    field016 = '富文本'
    field017 = '任务状态分类'
    field018 = '预估工时'
    field019 = '已登记工时合计'
    field020 = '剩余工时'
    field021 = '子工作项类型'
    field023 = '关联工作项数量'
    field024 = ''  # 泳道工作项筛选条件：工作项类型
    field025 = '预估偏差'
    field026 = '工时进度'
    field027 = '计划开始日期'
    field028 = '计划结束日期'
    field029 = '所属产品（多选项）'
    field030 = '所属产品模块（多选项）'  # 31 32
    field031 = '是否线上缺陷'
    field032 = '故事点'
    field033 = '进度'
    field034 = '工作项类型配置'
    field035 = '发布进度'
    field036 = '发布日期'
    field037 = '关联发布'
    field038 = '严重程度'
    field039 = '处理结果'
    field040 = '解决者'
    field041 = '缺陷类型'


def name_to_key(name):
    """
    获取系统属性key
    :param name:  中文名字
    :return:
    """
    keys = [k for k in SysField.__dict__.keys() if not k.startswith('__')]
    for k in keys:
        if getattr(SysField, k) == name:
            return k
