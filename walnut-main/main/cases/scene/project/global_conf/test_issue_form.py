"""
@File    ：test_issue_form.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/4/29
@Desc    ： 全局配置-工作项-新建工作项类型测试用例
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture

from main.actions.task import TaskAction
from main.api import project as pj
from main.api.const.field import SysField
from main.params import conf


@fixture(scope='module')
def _layout_uuid() -> list[tuple]:
    """
    获取全局默认的视图配置
    uuid and name

    :return: name, uuid
    """

    resp = go(pj.ItemGraphql, conf.layout_list()[0])

    uuids = [(r['name'], r['uuid'])
             for r in resp.value('data.issueTypeLayouts') if r['builtIn']]

    return uuids


@feature('全局配置')
class TestNewIssueForm(Checker):

    @classmethod
    def check_field(cls, data, name, token=None):
        #  TODO 这个检查方法需要更新 不能用工作项默认属性的方式 需要其检查视图配置
        # draft_param = conf.layout_draft_get()[0]
        # draft_param.uri_args({'layout_uuid': layout_uuid})
        # draft = go(ly.LayoutDraftGet, draft_param, token)
        #
        # forms = draft.value('data.form_block_root.children')
        # # 取 值为 left 的section
        # field_section = [f['children'][0]['children'] for f in forms if f['metadata']['section'] == 'left']
        #
        # # 遍历 field_section 数据 从 其 children 字段中取配置信息
        # # 如果 children 的 type 为rich_text、task_fields 的取uuid
        # # 其余取 metadata 的title 字段
        # return_fields = []  # 暂存字段名字
        # for children in field_section:
        #     for field in children:
        #         for child in field['children']:
        #             if child['type'] in ('rich_text', 'task_fields',):
        #                 metadata = child['metadata']
        #                 if 'fields' in metadata:
        #                     for f in metadata['fields']:
        #                         try:
        #                             n = getattr(SysField, f['uuid'])
        #                             return_fields.append(n)
        #                         except AttributeError:
        #                             print(f"{f['uuid']} NOT FOUND")
        #                 if 'field' in metadata:
        #                     try:
        #                         n = getattr(SysField, metadata['field']['uuid'])
        #                         return_fields.append(n)
        #                     except AttributeError:
        #                         print(f"{metadata['field']['uuid']} NOT FOUND")
        #             else:
        #                 if 'metadata' in child:
        #                     return_fields.append(child['metadata']['title'])
        #
        # # 校验返回结果
        # not_exist = []
        # for d in data:
        #     if d not in return_fields:
        #         not_exist.append(d)
        # if not_exist:
        #     raise AssertionError(f'{not_exist} NOT FOUND.')

        resp = TaskAction.task_stamp()
        issue_types = [r for r in resp['issue_type']['issue_types']]
        configs = [c['default_configs']['default_field_configs'] for c in issue_types if c['name'] == name][0]

        field_uuid = []

        for c in configs:
            if c['field_uuid'].startswith('field'):
                try:
                    name = getattr(SysField, c['field_uuid'])
                    field_uuid.append(name)
                except AttributeError:
                    print(f'{c["field_uuid"]} not found.')
        not_exist = []
        for d in data:
            if d not in field_uuid:
                # not_exist.append(d)
                print(f'{d} not found.')

        if not_exist:
            raise AssertionError(not_exist)

    @story('T152312 新建工作项：检查新建工作项表单展示详情（缺陷）')
    def test_new_defect_default_fields(self):
        """"""

        defect = ('标题', '所属项目', '工作项类型', '描述', '负责人',
                  '优先级', '所属迭代', '严重程度',
                  '缺陷类型', '解决者', '关注者', '关联工作项', '文件', '是否线上缺陷',)

        self.check_field(defect, '缺陷')

    @story('T152314 新建工作项：检查新建工作项表单展示详情（任务）')
    def test_new_task_default_fields(self):
        """"""

        task = ('标题', '所属项目', '工作项类型', '描述', '负责人', '优先级', '所属迭代', '截止日期', '预估工时', '关注者',)

        self.check_field(task, '任务')

    @story('T152313 新建工作项：检查新建工作项表单展示详情（需求）')
    def test_new_demand_default_fields(self):
        """"""

        task = ('标题', '所属项目', '工作项类型', '描述', '负责人', '优先级', '所属迭代', '关注者',)

        self.check_field(task, '需求')

    @story('T152316 新建工作项：检查新建工作项表单展示详情（子任务）')
    def test_new_sub_task_default_fields(self):
        """"""

        task = ('标题', '所属项目', '工作项类型', '描述', '负责人', '优先级', '所属迭代', '截止日期', '预估工时', '关注者',)

        self.check_field(task, '子任务')

    @story('T152315 新建工作项：检查新建工作项表单展示详情（子需求）')
    def test_new_sub_demand_default_fields(self):
        """"""

        task = ('标题', '所属项目', '工作项类型', '描述', '负责人', '优先级', '所属迭代', '关注者',)

        self.check_field(task, '子需求')
