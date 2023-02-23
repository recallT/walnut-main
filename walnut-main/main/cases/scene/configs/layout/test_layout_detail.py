"""
@File    ：test_layout_detail.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/5/7
@Desc    ：工作项视图详情检查
"""

from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture

from main.api import project as pj
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
        """"""
        # TODO 测试方法没完成
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

    @story('新建工作项：检查新建工作项表单展示详情（缺陷）')
    def test_new_defect_default_fields(self):
        """"""

        defect = ('标题', '所属项目', '工作项类型', '描述', '负责人',
                  '优先级', '所属迭代', '严重程度',
                  '缺陷类型', '解决者', '关注者', '关联工作项', '文件', '是否线上缺陷',)

        self.check_field(defect, '缺陷')

    @story('新建工作项：检查新建工作项表单展示详情（任务）')
    def test_new_task_default_fields(self):
        """"""

        task = ('标题', '所属项目', '工作项类型', '描述', '负责人', '优先级', '所属迭代', '截止日期', '预估工时', '关注者',)

        self.check_field(task, '任务')

    @story('新建工作项：检查新建工作项表单展示详情（需求）')
    def test_new_demand_default_fields(self):
        """"""

        task = ('标题', '所属项目', '工作项类型', '描述', '负责人', '优先级', '所属迭代', '关注者',)

        self.check_field(task, '需求')

    @story('新建工作项：检查新建工作项表单展示详情（子任务）')
    def test_new_sub_task_default_fields(self):
        """"""

        task = ('标题', '所属项目', '工作项类型', '描述', '负责人', '优先级', '所属迭代', '截止日期', '预估工时', '关注者',)

        self.check_field(task, '子任务')

    @story('新建工作项：检查新建工作项表单展示详情（子需求）')
    def test_new_sub_demand_default_fields(self):
        """"""

        task = ('标题', '所属项目', '工作项类型', '描述', '负责人', '优先级', '所属迭代', '关注者',)

        self.check_field(task, '子需求')
