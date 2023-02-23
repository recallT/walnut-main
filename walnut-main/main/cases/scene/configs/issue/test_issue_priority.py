"""
@Desc：全局配置-工作项-优先级
"""
from falcons.check import Checker
from falcons.com.nick import feature, story, step, parametrize
from falcons.helper import mocks

from main.actions.task import team_stamp
from main.api import project as prj
from main.params import issue as ise

# 优先级名称 最长5个字符
PRIORI_NAME = f"priori-{mocks.random_string(5).capitalize()}"


@feature('全局配置-优先级')
class TestGlobalIssuePriori(Checker):
    @staticmethod
    def get_priority_info(token=None):
        """获取最新的优先级配置信息"""
        stamp = team_stamp({"field": 0}, token)
        priori_info = [p for p in stamp['field']['fields'] if p['name'] == '优先级'][0]

        return priori_info

    @story('141311 新建优先级')
    @parametrize('param', ise.priori_update())
    def test_global_priori_add(self, param):
        priori_info = self.get_priority_info()

        with step('新建优先级，输入名称，选择配置颜色，输入描述'):
            param.json_update('field', priori_info)
            param.json['field']['options'].append({
                "value": PRIORI_NAME,
                "desc": "全局优先级auto测试",
                "background_color": "#ff6a39",
                "color": "#fff"
            })
            param.uri_args({'field_uuid': priori_info['uuid']})
            resp = self.call(prj.FieldUpdate, param)

            resp.check_response('field.name', '{{field.priority}}')

        with step('查看工作项 a 的工作项详情，点击打开优先级下拉列表'):
            stamp = team_stamp({"field": 0})
            new_priori_info = \
                [option['value'] for p in stamp['field']['fields'] if p['name'] == '优先级' for option in p['options']]

            assert PRIORI_NAME in new_priori_info

    @story('141295 编辑优先级描述')
    @parametrize('param', ise.priori_update())
    def test_global_priori_desc_update(self, param):
        priori_info = self.get_priority_info()

        with step('清空描述信息'):
            param.json_update('field', priori_info)
            param.json_update('field.options[-1].desc', "")
            param.uri_args({'field_uuid': priori_info['uuid']})
            resp = self.call(prj.FieldUpdate, param)

            up_priori_desc = [p['desc'] for p in resp.value('field.options') if p['value'] == PRIORI_NAME]

            assert up_priori_desc == ['']

        with step('修改描述信息为：xxx'):
            param.json_update('field.options[-1].desc', 'update-全局优先级auto测试')
            resp = self.call(prj.FieldUpdate, param)

            up_priori_desc = [p['desc'] for p in resp.value('field.options') if p['value'] == PRIORI_NAME][0]

            assert up_priori_desc == 'update-全局优先级auto测试'

    @story('141296 编辑优先级名称')
    @parametrize('param', ise.priori_update())
    def test_global_priori_name_update(self, param):
        priori_info = self.get_priority_info()

        with step('清空优先级名称'):
            param.json_update('field', priori_info)
            param.json_update('field.options[-1].value', "")
            param.uri_args({'field_uuid': priori_info['uuid']})
            resp = self.call(prj.FieldUpdate, param, status_code=400)

            resp.check_response('errcode', 'InvalidParameter.Field.Value.Empty')

        with step('修改优先级名称为：xxx'):
            param.json_update('field.options[-1].value', PRIORI_NAME)
            resp = self.call(prj.FieldUpdate, param)

            resp.check_response('field.options[-1].value', PRIORI_NAME)

    @story('141309 设置默认优先级')
    @parametrize('param', ise.priori_update())
    def test_global_set_default_priori(self, param):
        priori_info = self.get_priority_info()

        with step('选择优先级：最高，点击确定'):
            param.json_update('field', priori_info)

            priori_uuid = [p['uuid'] for p in param.json_value('field.options') if p['value'] == '最高'][0]

            param.json_update('field.default_value', priori_uuid)
            param.uri_args({'field_uuid': priori_info['uuid']})
            resp = self.call(prj.FieldUpdate, param)

            resp.check_response('field.default_value', priori_uuid)

        with step('还原默认优先级：普通'):
            default_uuid = [p['uuid'] for p in param.json_value('field.options') if p['value'] == '普通'][0]
            param.json_update('field.default_value', default_uuid)
            resp = self.call(prj.FieldUpdate, param)

            resp.check_response('field.default_value', default_uuid)

    @story('141310 设置优先级的排序')
    @parametrize('param', ise.priori_update())
    def test_global_set_priori_sort(self, param):
        """"""

    @story('141312 删除优先级')
    @parametrize('param', ise.priori_update())
    def test_global_priori_delete(self, param):
        priori_info = self.get_priority_info()

        param.json_update('field', priori_info)
        del param.json['field']['options'][-1]
        param.uri_args({'field_uuid': priori_info['uuid']})
        resp = self.call(prj.FieldUpdate, param)

        del_info = [op['value'] for op in resp.value('field.options')]
        assert PRIORI_NAME not in del_info
