"""
@File    ：team.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/7/18
@Desc    ：
"""
from falcons.ops import generate_param


def top_bar_search():
    """顶部菜单栏搜索"""

    # types 的值如下

    # space 页面组
    # page 页面
    # resource 附件、文件
    # project 项目
    # task 工作项
    return generate_param({
        'q': 'Test',  # 搜索内容
        'types': 'project',  # 类型可以变更, project, space, resource, page, task
        'start': 0,
        'limit': 50,
    })
