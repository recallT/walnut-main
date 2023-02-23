"""
@Desc ： 项目-工作项类型-工作流-步骤属性
"""
import time

from falcons.check import Checker
from falcons.com.nick import story, fixture, step, feature

from main.actions.pro import PrjAction
from main.actions.task import TaskAction
from main.api import project as api, issue, project
from main.api.issue import IssueFieldConfig, ImportantFieldUpdate
from main.params import proj, task as t, conf, issue as i, data as d
from main.params.const import ACCOUNT
from main.params.issue import notice_rules, field_sort
from main.actions.issue import IssueAction as Ia


@fixture(scope='module')
def _add_task():
    m = TaskAction.new_issue()
    return m[0]


@fixture(scope='module', autouse=True)
def _project_del():
    """还原项目内步骤属性"""
    yield
    data = [{"field_uuid": "tf-comment", "default_value": "", "required": False}]

    TestProStepProperties().add_step_properties('tf-comment', field=data)


@fixture(scope='module', autouse=True)
def _del():
    """还原步骤属性"""
    yield
    data = [{"field_uuid": "tf-comment", "default_value": "", "required": False}]

    TestGlobalStepProperties().add_global_step_properties('tf-comment', field=data)


@feature('项目工作项类型-工作流-步骤属性')
class TestProStepProperties(Checker):

    def add_step_properties(self, field_uuid, process_name='开始任务', token=None, **kwargs):
        """
        添加步骤属性
        :param token
        :param process_name 添加步骤属性流转过程的名称
        :param field_uuid 添加属性的uuid
        """
        issue_type = TaskAction.issue_type_uuid(token=token)[0]

        param = t.task_field(True)[0]
        param.json = {"transition": 0}
        stamp_resp = self.call(api.TeamStampData, param, token)

        process_uuid = [n['uuid'] for n in stamp_resp.value('transition.transitions') if
                        n['issue_type_uuid'] == issue_type and n['project_uuid'] == ACCOUNT.project_uuid and
                        n['name'] == process_name][0]

        prm = proj.pro_step_properties_up(issue_type, process_uuid, field_uuid)[0]

        if kwargs:
            prm.json_update('transition.fields', kwargs['field'])

        time.sleep(1)
        res = self.call(api.ProStepPropertiesUpdate, prm, token)
        uuids = [f['field_uuid'] for f in res.value('transition.fields')]

        assert field_uuid in uuids

        return res

    @story('117795 检查添加步骤属性时设置属性默认值和必填项的表现')
    @story('117777 步骤属性：检查添加步骤属性时设置属性默认值和必填项的表现')
    def test_step_priority(self):
        with step('属性名称选择：优先级,属性默认值：最高,是否必填：必填'):
            pri_uuid = TaskAction.task_field_value_uuid('优先级', '最高')

            data = [{"required": True, "field_uuid": "field012", "default_value": pri_uuid},
                    {"field_uuid": "tf-comment", "default_value": "", "required": False}]

            self.add_step_properties('field012', field=data)

    @story('117882 添加步骤属性（登记工时）')
    def test_step_register_hour_add(self):
        self.add_step_properties('tf-manhour')

    @story('117929 添加步骤属性（关联 Wiki 页面）')
    def test_step_wiki_add(self):
        self.add_step_properties('tf-wikipage')

    @story('117960 添加步骤属性（所属产品）')
    def test_step_product_add(self):
        self.add_step_properties('field029')

    @story('117981 添加步骤属性（文件）')
    def test_step_file_add(self):
        self.add_step_properties('tf-resource')

    @story('118001 添加步骤属性（预估工时）')
    def test_step_estimate_hour_add(self):
        self.add_step_properties('field018')

    @story('117815 列表排序')
    def test_step_list_sort(self):
        data = [
            {
                "field_uuid": "field029",
                "default_value": None,
                "required": False
            },
            {
                "field_uuid": "tf-resource",
                "default_value": None,
                "required": False
            },
            {
                "field_uuid": "tf-wikipage",
                "default_value": None,
                "required": False
            },
            {
                "field_uuid": "tf-comment",
                "default_value": "",
                "required": False
            }
        ]

        self.add_step_properties('tf-resource', field=data)

    @story('148475 步骤属性：删除步骤属性')
    @story('148476 删除步骤属性')
    def test_step_delete(self):
        data = [{"field_uuid": "tf-comment", "default_value": "", "required": False}]

        self.add_step_properties('tf-comment', field=data)

    @story('T121433 T121448 更改任务状态：步骤属性设为必填，变更状态时不填 ')
    def test_step_file_not_value(self):
        with step('前置条件：添加一个必填工作项属性，创建一个任务工作项'):
            pri_uuid = TaskAction.task_field_value_uuid('优先级', '最高')

            data = [{"required": True, "field_uuid": "field012", "default_value": pri_uuid},
                    {"field_uuid": "tf-comment", "default_value": "", "required": False}]

            self.add_step_properties('field012', field=data)
            task_uuid = TaskAction.new_issue(issue_type_name='任务', is_batch=False)[0]
        with step('修改状态为开始任务）'):
            resp_transitions = PrjAction.get_task_transitions(task_uuid)
            # 修改状态为开始任务
            transitions_uuid = [name_list['uuid'] for name_list in resp_transitions.value('transitions') if
                                name_list['name'] == '开始任务'][0]
            # 必填信息不填，返回400
            TaskAction.transit_task_status(transitions_uuid, task_uuid, status_code=400)


@feature('全局配置工作项类型-工作流-步骤属性')
class TestGlobalStepProperties(Checker):

    def add_global_step_properties(self, field_uuid, process_name='开始任务', **kwargs):
        """
        添加全局步骤属性
        :param process_name 添加步骤属性流转过程的名称
        :param field_uuid 添加属性的uuid
        """
        issue_type = TaskAction.issue_type_uuid()[0]

        param = t.task_field(True)[0]
        param.json = {"issue_type": 0}
        stamp_resp = self.call(api.TeamStampData, param)

        process_uuid = [u['uuid'] for n in stamp_resp.value('issue_type.issue_types') if
                        n['uuid'] == issue_type for u in n['default_configs']['default_transitions'] if
                        u['name'] == process_name][0]

        prm = proj.global_step_properties_up(issue_type, process_uuid, field_uuid)[0]

        if kwargs:
            prm.json_update('transition.fields', kwargs['field'])

        time.sleep(1)
        res = self.call(api.GlobalStepPropertiesUpdate, prm)

        return res

    @story('117753 编辑列表属性默认值及必填项')
    def test_global_step_priority(self):
        with step('属性名称选择：优先级,属性默认值：最高,是否必填：必填'):
            pri_uuid = TaskAction.task_field_value_uuid('优先级', '最高')

            data = [{"required": True, "field_uuid": "field012", "default_value": pri_uuid},
                    {"field_uuid": "tf-comment", "default_value": "", "required": False}]

            self.add_global_step_properties('field012', field=data)

    @story('117888 添加步骤属性（登记工时）')
    @story('117887 添加步骤属性（登记工时）')
    def test_global_step_register_hour_add(self):
        self.add_global_step_properties('tf-manhour')

    @story('117925 添加步骤属性（关联 Wiki 页面）')
    def test_global_step_wiki_add(self):
        self.add_global_step_properties('tf-wikipage')

    @story('117944 添加步骤属性（进度）')
    def test_global_step_schedule_add(self):
        self.add_global_step_properties('field033')

    @story('117973 添加步骤属性（所属产品）')
    def test_global_step_product_add(self):
        self.add_global_step_properties('field029')

    @story('117977 添加步骤属性（文件）')
    def test_global_step_file_add(self):
        self.add_global_step_properties('tf-resource')

    @story('118012 添加步骤属性（预估工时）')
    def test_global_step_estimate_hour_add(self):
        self.add_global_step_properties('field018')

    @story('118059 添加步骤属性（自定义单选成员）')
    def test_global_step_customize_add(self):
        with step('前置条件'):
            # 新增工作项属性
            param = conf.add_issue_type_field()[0]
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            issue_type = TaskAction.issue_type_uuid()[0]
            prm = i.add_issue_field()[0]
            prm.json_update('field_config.field_uuid', field_uuid)
            prm.json_update('field_config.required', False)
            prm.uri_args({'issue_uuid': issue_type})

            self.call(issue.IssueFieldAdd, prm)

        with step('添加步骤属性选择（自定义单选成员）'):
            self.add_global_step_properties(field_uuid)

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_type, field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('117813 列表排序')
    def test_global_step_list_sort(self):
        data = [
            {
                "field_uuid": "field029",
                "default_value": None,
                "required": False
            },
            {
                "field_uuid": "tf-resource",
                "default_value": None,
                "required": False
            },
            {
                "field_uuid": "tf-wikipage",
                "default_value": None,
                "required": False
            },
            {
                "field_uuid": "tf-comment",
                "default_value": "",
                "required": False
            }
        ]

        self.add_global_step_properties('tf-resource', field=data)

    @story('117851 删除步骤属性')
    def test_global_step_delete(self):
        data = [{"field_uuid": "tf-comment", "default_value": "", "required": False}]

        self.add_global_step_properties('tf-comment', field=data)

    @story('T123714 工作项属性：删除工作项属性')
    def test_del_issue_field(self):
        param = conf.add_issue_type_field()[0]
        res = self.call(project.FieldsAdd, param)
        field_uuid = res.value('field.uuid')

        with step('点击「示例属性」后的删除按钮'):
            p = d.field_delete()[0]
            p.uri_args({'field_uuid': field_uuid})
            self.call(api.FieldDelete, p)

    @story('T128335 关键属性：属性排序--任务')
    def test_task_sort_important_field(self):
        issue_type_uuid = TaskAction.issue_type_uuid('任务')[0]
        param = notice_rules()[0]
        param.uri_args({'issue_uuid': issue_type_uuid})
        resp = self.call(IssueFieldConfig, param)
        with step('长按拖拽「ID」至「负责人」后'):
            important_field = [r['field_uuid'] for r in resp.json()[0]['items'] if r['is_important_field'] == True]
            important_field.reverse()
            param_field = field_sort()[0]
            param_field.json_update('fields', important_field)
            param_field.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(ImportantFieldUpdate, param_field)
            resp.check_response('name', '任务')
            resp.check_response('built_in', True)

    @story('T128331 关键属性：属性排序--子任务')
    def test_sub_task_sort_important_field(self):
        issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
        param = notice_rules()[0]
        param.uri_args({'issue_uuid': issue_type_uuid})
        resp = self.call(IssueFieldConfig, param)
        with step('长按拖拽「ID」至「负责人」后'):
            important_field = [r['field_uuid'] for r in resp.json()[0]['items'] if r['is_important_field'] == True]
            important_field.reverse()
            param_field = field_sort()[0]
            param_field.json_update('fields', important_field)
            param_field.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(ImportantFieldUpdate, param_field)
            resp.check_response('name', '子任务')
            resp.check_response('built_in', True)

    @story('128504 关键属性：添加自定义关键属性（单选菜单）')
    def test_task_add_important_field(self):
        issue_type_uuid = TaskAction.issue_type_uuid('任务')[0]
        param = notice_rules()[0]
        param.uri_args({'issue_uuid': issue_type_uuid})
        resp = self.call(IssueFieldConfig, param)
        with step('点击添加关键属性'):
            important_field = [r['field_uuid'] for r in resp.json()[0]['items'] if r['is_important_field'] == True]
            new_field = [r['field_uuid'] for r in resp.json()[0]['items'] if
                         r['is_important_field'] == False and r['can_delete'] == True][0]
            important_field.append(new_field)
            param_field = field_sort()[0]
            param_field.json_update('fields', important_field)
            param_field.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(ImportantFieldUpdate, param_field)
            resp.check_response('built_in', True)
        with step('删除添加的关键属性'):
            important_field.remove(new_field)
            param_field.json_update('fields', important_field)
            resp_del = self.call(ImportantFieldUpdate, param_field)
            resp_del.check_response('built_in', True)

    @story('128505 关键属性：添加自定义关键属性（单选菜单）--子任务')
    def test_sub_task_add_important_field(self):
        issue_type_uuid = TaskAction.issue_type_uuid('子任务')[0]
        param = notice_rules()[0]
        param.uri_args({'issue_uuid': issue_type_uuid})
        resp = self.call(IssueFieldConfig, param)
        with step('点击添加关键属性'):
            important_field = [r['field_uuid'] for r in resp.json()[0]['items'] if r['is_important_field'] == True]
            new_field = [r['field_uuid'] for r in resp.json()[0]['items'] if
                         r['is_important_field'] == False and r['can_delete'] == True][0]
            important_field.append(new_field)
            param_field = field_sort()[0]
            param_field.json_update('fields', important_field)
            param_field.uri_args({'issue_type_uuid': issue_type_uuid})
            resp = self.call(ImportantFieldUpdate, param_field)
            resp.check_response('built_in', True)

        with step('删除添加的关键属性'):
            important_field.remove(new_field)
            param_field.json_update('fields', important_field)
            resp_del = self.call(ImportantFieldUpdate, param_field)
            resp_del.check_response('built_in', True)

    @story('T118049 步骤属性：添加步骤属性（自定义单选菜单）')
    @story('162176 步骤属性：移除步骤属性（自定义多选菜单）')
    def test_global_step_radio_menu(self):
        with step('前置条件'):
            # 新增工作项属性 定义单选菜单
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 1)
            param.json_update('field.options', [{'value': "test", 'background_color': "#307fe2", 'color': "#fff"}])
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            issue_type = TaskAction.issue_type_uuid()[0]
            param = i.add_task_field([field_uuid], '')[0]
            param.json_update('project_issue_types', [])
            param.json_update('team_issue_types', [issue_type])
            self.call(project.AddTaskField, param)

        with step('添加步骤属性选择（定义单选菜单）'):
            self.add_global_step_properties(field_uuid)

            with step('清除数据'):
                # 删除工作项内属性
                Ia.del_issue_field(issue_type, field_uuid)
                # 删除全局属性
                Ia.del_field(field_uuid)

    @story('T118087 步骤属性：添加步骤属性（自定义单选迭代）')
    def test_global_step_radio_sprint(self):
        with step('前置条件'):
            # 新增工作项属性 定义单选菜单
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 7)
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            issue_type = TaskAction.issue_type_uuid()[0]
            param = i.add_task_field([field_uuid], '')[0]
            param.json_update('project_issue_types', [])
            param.json_update('team_issue_types', [issue_type])
            self.call(project.AddTaskField, param)

        with step('添加步骤属性选择（自定义单选迭代）'):
            self.add_global_step_properties(field_uuid)

            with step('清除数据'):
                # 删除工作项内属性
                Ia.del_issue_field(issue_type, field_uuid)
                # 删除全局属性
                Ia.del_field(field_uuid)

    @story('T118113 步骤属性：添加步骤属性（自定义多行文本）')
    def test_global_step_more_text(self):
        with step('前置条件'):
            # 新增工作项属性 定义单选菜单
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 15)
            param.json_update('field.options',
                              [{'value': "test", 'background_color': "#307fe2", 'color': "#fff"}])
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            issue_type = TaskAction.issue_type_uuid()[0]
            param = i.add_task_field([field_uuid], '')[0]
            param.json_update('project_issue_types', [])
            param.json_update('team_issue_types', [issue_type])
            self.call(project.AddTaskField, param)

        with step('添加步骤属性选择（自定义多行文本）'):
            self.add_global_step_properties(field_uuid)

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_type, field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118128 步骤属性：添加步骤属性（自定义多选菜单））-任务')
    def test_global_task_step_check_menu_add(self):
        with step('前置条件'):
            # 新增工作项属性 自定义多选菜单
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 16)
            param.json_update('field.options', [{'value': "test", 'background_color': "#307fe2", 'color': "#fff"}])
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            issue_type = TaskAction.issue_type_uuid(issue_types='任务')[0]
            param = i.add_task_field([field_uuid], '')[0]
            param.json_update('project_issue_types', [])
            param.json_update('team_issue_types', [issue_type])
            self.call(project.AddTaskField, param)

        with step('添加步骤属性选择（自定义单选成员）'):
            self.add_global_step_properties(field_uuid)

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_type, field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)

    @story('T118139 步骤属性：添加步骤属性（自定义多选成员）')
    def test_global_task_step_check_member_add(self):
        with step('前置条件'):
            # 新增工作项属性 自定义多选菜单
            param = conf.add_issue_type_field()[0]
            param.json_update('field.type', 13)
            res = self.call(api.FieldsAdd, param)
            field_uuid = res.value('field.uuid')

            # 将新增属性添加到对应工作项
            issue_type = TaskAction.issue_type_uuid(issue_types='任务')[0]
            param = i.add_task_field([field_uuid], '')[0]
            param.json_update('project_issue_types', [])
            param.json_update('team_issue_types', [issue_type])
            self.call(project.AddTaskField, param)

        with step('添加步骤属性选择（自定义单选成员）'):
            self.add_global_step_properties(field_uuid)

        with step('清除数据'):
            # 删除工作项内属性
            Ia.del_issue_field(issue_type, field_uuid)
            # 删除全局属性
            Ia.del_field(field_uuid)
