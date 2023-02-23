"""
@File    ：test_issue_view_field.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/16
@Desc    ：工作项-查看表单详情
"""

from falcons.check import Checker
from falcons.com.nick import feature, story, fixture

from main.actions.pro import PrjAction
from main.actions.task import TaskAction


@fixture(scope='module')
def p_stamp():
    """项目stamp数据"""
    j = PrjAction.project_stamp_data().json()
    return j


@fixture(scope='module')
def issue_type():
    """工作项UUID"""
    j = TaskAction.task_stamp(True)

    if not j:
        raise RuntimeError('工作项UUID 取值异常！【j】')

    return j


def get_uuid(name, j):
    """"""
    configs = [m['issue_type_uuid']
               for m in j['issue_type_config']['issue_type_configs']
               if m['name'] == name]
    if not configs:
        raise RuntimeError(f'没查到 {name} 默认权限配置!')

    return configs[0]


@feature('开箱默认配置')
class TestIssueViewField(Checker):
    """"""

    @story('152312 新建工作项：检查新建工作项表单展示详情（缺陷）')
    def test_issue_view_field_defense(self, p_stamp, issue_type):
        """"""
        d_type = '缺陷'
        issue_uuid = get_uuid(d_type, issue_type)

        stamp = [s for s in p_stamp['field_config']['field_configs']
                 if s['issue_type_uuid'] == issue_uuid]
        default_field = [s['field_uuid'] for s in stamp]
        # print(default_field)
