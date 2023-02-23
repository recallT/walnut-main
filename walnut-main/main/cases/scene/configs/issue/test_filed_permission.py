"""
@Desc：全局配置-工作项类型-工作项权限-属性修改权限
"""
from falcons.check import Checker, go
from falcons.com.nick import feature, story, fixture, step, parametrize

from main.actions.task import team_stamp, TaskAction
from main.api import issue, project as prj
from main.params import conf, proj
from main.params.const import ACCOUNT


@fixture(scope='module')
def _storage():
    return {'constraint_uuids': [], 'c_uuid': []}


@fixture(scope='module', autouse=True)
def clear_constraint(issue_uuid, _storage):
    yield

    if _storage['constraint_uuids']:
        param = conf.constraints_del()[0]
        param.json_update('constraint_uuids', _storage['constraint_uuids'])
        param.uri_args({'issue_uuid': issue_uuid})
        go(issue.ConstraintsDelete, param)


@fixture(scope='module')
def issue_uuid():
    issue_uuid = TaskAction.issue_type_uuid()[0]

    return issue_uuid


@feature('工作项权限-属性修改权限')
class TestFiledUpdatePermission(Checker):

    def init_role(self, token=None):
        resp = team_stamp({'role': 0}, token)
        role = [r['uuid'] for r in resp['role']['roles'] if r['name'] == '项目成员'][0]

        return role

    def constraints_add(self, field_uuid, issue_uuid, status_code=200, token=None) -> list:
        """新增属性权限规则"""

        domain_uuid = self.init_role(token)

        param = conf.constraints(domain_uuid, field_uuid)[0]
        param.uri_args({'issue_uuid': issue_uuid})
        resp = self.call(issue.ConstraintsAdd, param, token=token, status_code=status_code)

        if resp.response.status_code == 200:
            constraints = [c['field_uuid'] for c in resp.value('default_configs.default_constraints')]
            assert field_uuid in constraints

            constraint_uuid = [c['uuid'] for c in resp.value('default_configs.default_constraints') if
                               c['field_uuid'] == field_uuid]

            return constraint_uuid

    @story('145012 新建规则')
    def test_filed_permission_new_rule(self, _storage, issue_uuid):
        """属性修改权限-新建规则"""
        with step('选择工作项属性：标题；选择成员域：项目成员'):
            resp = self.constraints_add('field001', issue_uuid, status_code=[200, 409])

            if resp:
                _storage['constraint_uuids'] += resp  # 缓存规则uuid

    @story('145363 新建规则：选择工作项属性_系统属性')
    def test_new_rule_choice_system(self, _storage, issue_uuid):
        """新建规则选择系统属性"""
        with step('选择工作项属性：所属产品、所属功能模块；选择成员域：项目成员'):
            resp = self.constraints_add('field029-field030', issue_uuid, status_code=[200, 409])

            if resp:
                _storage['constraint_uuids'] += resp

        with step('登录部门B的成员b 账号,在项目A下编辑任务「所属产品、所属功能模块」'):
            """"""

    @story('145375 新建规则：选择工作项属性_自定义属性')
    def test_new_rule_choice_customize(self, _storage, issue_uuid):
        """新建规则选择自定义属性"""
        with step('选择工作项属性：需求来源；选择成员域：项目成员'):
            resp = self.constraints_add('field016', issue_uuid, status_code=[200, 409])

            if resp:
                _storage['constraint_uuids'] += resp

        with step('登录部门B的成员b 账号,在项目A下编辑任务「所属产品、所属功能模块」'):
            """"""

    @story('145350 修改规则：搜索成员域')
    def test_update_rule_search_user(self):
        with step('搜索框中输入用户组名称关键字 用户'):
            # 获取用户名名称
            me = prj.UsersMe()
            me.call()
            name = me.value('name')

            # 搜索成员
            param = proj.program_search_user(name)[0]
            resp = self.call(prj.UsesSearch, param)

            resp.check_response('users[0].name', name)

        with step('搜索框中输入成员名称关键字'):
            param.json_update('keyword', name[:3])
            resp = self.call(prj.UsesSearch, param)

            resp.check_response('users[0].name', name)

    @story('145380 修改规则：添加成员域')
    def test_update_rule_add_user(self, _storage, issue_uuid):
        with step('修改「截止日期」规则，添加成员域'):
            user_uuid = ACCOUNT.user.owner_uuid

            param = conf.constraints(user_uuid, 'field013')[0]
            param.json_update('constraints[0].user_domain_type', 'single_user')
            param.uri_args({'issue_uuid': issue_uuid})
            resp = self.call(issue.ConstraintsAdd, param, status_code=[200, 409])

            if resp.response.status_code == 200:
                c_uuid = [c['uuid'] for c in resp.value('default_configs.default_constraints') if
                          c['field_uuid'] == 'field013' and c['user_domain_param'] == user_uuid]

                _storage['c_uuid'] += c_uuid

    @story('145379 修改规则：删除成员域')
    def test_update_rule_del_user(self, _storage, issue_uuid):
        with step('修改「截止日期」规则，删除成员域'):
            param = conf.constraints_del()[0]
            param.json_update('constraint_uuids', _storage['c_uuid'])
            param.uri_args({'issue_uuid': issue_uuid})
            self.call(issue.ConstraintsDelete, param)

    @story('145011 属性修改权限：删除规则')
    @parametrize('param', conf.constraints_del())
    def test_filed_permission_del_rule(self, param, _storage, issue_uuid):
        with step('删除自定义规则'):
            if _storage['constraint_uuids']:
                param.json_update('constraint_uuids', [_storage['constraint_uuids'][0]])
                param.uri_args({'issue_uuid': issue_uuid})
                self.call(issue.ConstraintsDelete, param)
