"""
@Desc：项目设置-项目属性
"""
from falcons.check import Checker
from falcons.com.meta import ApiMeta
from falcons.com.nick import feature, story, parametrize, fixture, step, mark

from main.api import project as prj
from main.helper.extra import Extra
from main.params import conf


@fixture(scope='module')
def data_storage():
    creator = Extra(ApiMeta)
    p_uuid = creator.new_project('proj_test_field')

    return {'proj_uuid': p_uuid}


@fixture(scope='module', autouse=True)
def _clear_proj(data_storage):
    yield
    creator = Extra(ApiMeta)
    creator.del_project(data_storage['proj_uuid'])


SYS_FIELD = ['成员数量', '工作项数量', '工作项完成度', '计划开始日期', '项目成员', '已完成工作项数量', '总剩余工时']


@mark.smoke
@feature('项目属性')
class TestProjField(Checker):

    def proj_field_add(self, field_type, storage, options: list = None):
        """新建项目配置-项目属性"""

        # 配置中心已存在项目属性
        param = conf.add_field(field_type)[0]

        if options:
            param.json['item'] |= {'options': options}

        resp = self.call(prj.ItemsAdd, param)
        field_uuid = resp.value('item.aliases')

        # 项目属性中添加属性
        f_param = conf.add_field_to_project(storage['proj_uuid'])[0]
        f_param.json_update('item.aliases', field_uuid)
        prj_resp = self.call(prj.ItemsAdd, f_param)

        prj_resp.check_response('item.aliases', field_uuid)

        storage |= {f'{field_type}_field_uuid': resp.value('item.aliases'),
                    f'{field_type}_global_key': resp.value('item.key'),
                    f'{field_type}_proj_key': prj_resp.value('item.key')}

    def proj_overview_field_check(self, field_type, storage):
        """项目概览-项目属性检查"""

        s_param = conf.get_sys_status()[0]
        del s_param.json['query']['must'][1]
        resp = self.call(prj.TeamView, s_param)

        aliases = [i['aliases'] for i in resp.value('items')]
        assert storage[f'{field_type}_field_uuid'] in aliases

    def proj_and_global_field_del(self, storage, field_type):
        """删除项目内和全局项目属性"""

        # 删除项目中的项目属性
        param = conf.delete_field()[0]
        param.uri_args({'item_key': storage[f'{field_type}_proj_key']})
        self.call(prj.ItemDelete, param)

        # 删除全局配置中的项目属性
        param.uri_args({'item_key': storage[f'{field_type}_global_key']})
        self.call(prj.ItemDelete, param)

    @story('138326 项目属性：添加单行文本属性')
    @story('138329 项目属性：添加多行文本属性')
    @story('138328 项目属性：添加单选成员属性')
    @story('138331 项目属性：添加多选成员属性')
    @story('138332 项目属性：添加浮点数属性')
    @story('138333 项目属性：添加日期属性')
    @story('138334 项目属性：添加时间属性')
    @story('138336 项目属性：添加整数属性')
    @parametrize('field_type', ['text', 'multi_line_text', 'user', 'user_list', 'float', 'date', 'time', 'integer'])
    def test_proj_field_add(self, field_type, data_storage):
        with step('添加项目属性'):
            self.proj_field_add(field_type, data_storage)

        with step('进入项目概览，查看「项目属性」'):
            self.proj_overview_field_check(field_type, data_storage)

    @story('138327 项目属性：添加单选菜单属性')
    @story('138330 项目属性：添加多选菜单属性')
    @parametrize('field_type', ['option', 'multi_option'])
    def test_proj_field_menu_add(self, field_type, data_storage):
        """添加单选/多选菜单项目属性"""
        with step('添加项目属性'):
            opt = [{"value": "test_1"}, {"value": "test_2"}]
            self.proj_field_add(field_type, data_storage, opt)

        with step('进入项目概览，查看「项目属性」'):
            self.proj_overview_field_check('option', data_storage)

    @story('138310 项目属性：删除单行文本属性')
    @story('138313 项目属性：删除多行文本属性')
    @story('138312 项目属性：删除单选成员属性')
    @story('138315 项目属性：删除多选成员属性')
    @story('138316 项目属性：删除浮点数属性')
    @story('138317 项目属性：删除日期属性')
    @story('138318 项目属性：删除时间属性')
    @story('138311 项目属性：删除单选菜单属性')
    @story('138320 项目属性：删除整数属性')
    @story('138314 项目属性：删除多选菜单属性')
    @parametrize('field_types',
                 ['text', 'multi_line_text', 'user', 'user_list', 'float', 'date', 'time', 'integer', 'option',
                  'multi_option'])
    def test_proj_field_del(self, data_storage, field_types):
        self.proj_and_global_field_del(data_storage, field_types)

    @story('138338 项目属性：新建项目后默认属性列表检查')
    def test_check_proj_default_field(self):
        with step('查看项目属性列表默认系统属性'):
            s_param = conf.get_sys_status()[0]
            del s_param.json['query']['must'][1]
            resp = self.call(prj.TeamView, s_param)

            names = [i['name'] for i in resp.value('items') if i['built_in'] == True]

            for name in SYS_FIELD:
                assert name in names
