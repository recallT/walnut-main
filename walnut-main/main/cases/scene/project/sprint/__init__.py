"""
@File    ：__init__
@Author  ：xiechunwei
@Date    ：2022/6/30 11:57
@Desc    ：项目设置-迭代配置的公共方法
"""
from falcons.check import Checker
from main.api import sprint as sp
from main.params import proj
from falcons.helper import mocks


class SprintOpt(Checker):

    @classmethod
    def sprint_field_add(cls, types, storage, options: dict = None, code=200):
        """新增迭代属性"""

        param = proj.sprint_field_add(types)[0]
        del param.json['field']['options']
        if options:
            param.json['field'] |= options

        res = cls.call(sp.SprintFieldAdd, param, status_code=code)

        if code == 200:
            storage |= {f'{types}': res.value('field.uuid')}
            storage |= {f'{types}-name': res.value('field.name')}

            return res.value('field.name'), res.value('field.uuid')

    @classmethod
    def sprint_field_edit(cls, types, field_uuid, options: dict = None, code=200):
        """编辑迭代属性"""

        up_name = f'up-{types}-{mocks.num()}'
        param = proj.sprint_field_value_up(field_uuid, up_name, options, types)[0]
        param.uri_args({'field_uuid': field_uuid})

        cls.call(sp.ProSprintFieldUpdate, param, status_code=code)

    @classmethod
    def field_default_edit(cls, field_name, field_uuid, types, up_default, options=None):
        """编辑属性默认值"""

        param = proj.sprint_field_value_up(field_uuid, field_name, options, types)[0]
        param.json_update('field.default_value', up_default)

        if options:
            param.json_update('field.options', options)
        param.uri_args({'field_uuid': field_uuid})

        cls.call(sp.ProSprintFieldUpdate, param)

    @classmethod
    def check_sprint_field(cls, field_name, field_uuid, key='uuid', check_value=None):
        """
        查看项目概览迭代属性
        :param field_name  迭代属性名
        :param field_uuid  迭代属性uuid
        :param key  查看概览迭代属性的key
        :param check_value  需要校验的值
        """

        param = proj.sprint_field_position()[0]
        resp = cls.call(sp.ProSprintField, param, with_json=False)

        result = [f[key] for f in resp.value('fields') if f['name'] == field_name]

        if check_value:
            assert check_value in result
        else:
            assert field_uuid in result

    @classmethod
    def set_field_value(cls, sp_uuid, sf_uuid, value='', code=200):
        """
        迭代设置属性值
        :param sp_uuid  迭代uuid
        :param sf_uuid  属性uuid
        :param value
        :param code
        """

        param = proj.sprint_field_up()[0]
        param.uri_args({'sprint_uuid': sp_uuid})
        param.uri_args({'field_uuid': sf_uuid})
        param.json_update('field_value.value', value)

        return cls.call(sp.SprintFieldUpdate, param, status_code=code)