from falcons.check import Checker
from falcons.com.nick import parametrize, feature, fixture, story, step, mark
from falcons.helper import mocks

from main.actions.sprint import SprintAction
from main.api import more as prd
from main.api import project as api
from main.params import data, conf, more
from main.params.const import ACCOUNT


@fixture(scope='module')
def _storage():
    """Store product item for case actions
    eg :
    {
        "assign": "EFUpm6kT",
        "create_time": 1638862523,
        "item_type": "product",
        "key": "product-EFUpm6kTE4Pd4WR4",
        "name": "但",
        "name_pinyin": "dan4",
        "owner": "EFUpm6kT",
        "uuid": "EFUpm6kTE4Pd4WR4"
        "b_uuid": ""
    }
    """
    p = {}

    return p


@fixture(scope='module')
def _user_domain():
    param = []
    return param


@mark.smoke
@feature('产品管理相关')
class TestProducts(Checker):

    @story('T23168 新建产品')
    @story('143674 产品概览：新建产品')
    @parametrize('param', data.product_add())
    def test_product_add(self, param, _storage):

        with step('填写产品信息'):
            rp = self.call(api.ItemsAdd, param)

            _storage |= rp.json()['item']  # Save Product item

            rp.check_response('item.assign', param.json['item']['assign'])
            rp.check_response('item.item_type', param.json['item']['item_type'])
            rp.check_response('item.name', param.json['item']['name'])

        with step('名字为空'):
            param.json['item']['name'] = ''
            rp = self.call(api.ItemsAdd, param, status_code=400)
            rp.check_response('errcode', 'MissingParameter.Parent.Name')

    @story('T143672 查看产品列表')
    @parametrize('param', conf.view_product())
    def test_product_list(self, param):

        default_field = '创建日期', '产品名称', '产品负责人', '产品创建人', '未开始工作项数', '工作项数', '已完成工作项数'

        view = self.call(api.TeamView, param)

        fields = [f['name'] for f in view.json()['items'] if f['built_in']]
        err_ = [d for d in default_field if d not in fields]

        assert not err_, f'有未包含的系统产品属性{err_}'

    @story('更新产品：名称')
    @parametrize('param', data.product_update())
    def test_product_update(self, param, _storage):

        param.uri_args({'item_key': _storage['key']})
        up = self.call(api.ItemUpdate, param)

        up.check_response('item.name', param.json['item']['name'])
        up.check_response('item.uuid', _storage['uuid'])

    @story('T23172 产品信息：更新产品负责人')
    @parametrize('param', data.product_update())
    def test_product_principal_update(self, param, _storage):

        param.json['item'] = {'assign': ACCOUNT.user.member_uuid}
        param.uri_args({'item_key': _storage['key']})
        up = self.call(api.ItemUpdate, param)

        up.check_response('item.assign', ACCOUNT.user.member_uuid)

    @story('T143669 产品版本：新建版本默认关联当前产品')
    @parametrize('param', more.version_add())
    def test_prd_add_version(self, param, _storage):

        with step('在产品A-版本中新建版本A'):
            param.json['version']['product_uuids'].append(_storage['uuid'])
            add = self.call(api.VersionAdd, param)
            add.check_response('version.title', param.json['version']['title'])

        with step('检查默认关联版本A'):
            add.check_response('version.product_uuids', [_storage['uuid']])

            _storage |= {'ver_uuid': add.json()['version']['uuid']}

    @story('T143670 产品版本：关联产品')
    @parametrize('param', more.version_relate_product())
    def test_prd_version_relate_product(self, param, _storage):

        with step('前置条件'):
            # 新建产品B
            prm = data.product_add()[0]
            prm.json['item']['name'] = f'Pro - {mocks.ones_uuid()}'
            rp = self.call(api.ItemsAdd, prm)

            b_uuid = rp.json()['item']['uuid']
            _storage |= {'b_uuid': b_uuid}  # 存储产品B uuid

        with step('选择产品B，提交'):
            param.json['product_uuids'].append(b_uuid)
            param.uri_args({'version_uuid': _storage['ver_uuid']})

            vr = self.call(prd.VersionRelateProduct, param)
            vr.check_response('version.product_uuids', [_storage['uuid'], b_uuid])

    @story('T143671 产品版本：关联迭代')
    @story('143706 关联迭代')
    @parametrize('param', more.version_relate_sprint())
    def test_prd_version_relate_sprint(self, param, _storage):

        with step('前置条件'):
            # 新建迭代
            sprint_uuid = SprintAction.sprint_add()

        with step('选择迭代A，提交'):
            param.json['sprint_uuid'] = sprint_uuid
            param.uri_args({'version_uuid': _storage['ver_uuid']})
            add = self.call(prd.VersionRelateSprint, param)

            add.check_response('version.product_uuids', [_storage['uuid'], _storage['b_uuid']])

    @story('添加成员的组件权限')
    @parametrize('permit', ['view_product', 'manage_product'])
    def test_add_member_permit(self, permit, _storage, _user_domain):

        with step('添加成员A的权限'):
            param = more.add_member_permit(permit)[0]
            param.json['permission_rule']['context_param']['product_uuid'] = _storage['uuid']
            pem = self.call(api.PermissionAdd, param)

            _user_domain.append(pem.json()['permission_rule']['uuid'])

            pem.check_response('permission_rule.permission', permit)

    @story('T118950 查看产品权限：删除成员域')
    @parametrize('param', more._delete())
    def test_delete_member_permit(self, param, _user_domain):

        with step('查看产品权限-成员A删除'):
            if _user_domain:
                param.uri_args({'uuid': _user_domain[0]})
                self.call(prd.ProductMemberDelete, param)

    @story('T131307 产品模块：新建模块')
    @parametrize('param', more.add_product_module())
    def test_prd_add_module(self, param, _storage):

        with step('点击新建模块'):
            param.json['item']['product'] = _storage['uuid']
            add = self.call(api.ItemsAdd, param)

            add.check_response('item.item_type', param.json['item']['item_type'])
            add.check_response('item.name', param.json['item']['name'])

            _storage |= {'module_uuid': add.json()['item']['uuid']}

    @story('T131309 产品模块：新建子模块')
    @parametrize('param', more.add_product_module())
    def test_prd_add_sub_module(self, param, _storage):

        with step('点击新建子模块'):
            param.json['item']['description'] = 'submodule-submodule-submodule'
            param.json['item']['parent'] = _storage['module_uuid']
            param.json['item']['product'] = _storage['uuid']

            self.call(api.ItemsAdd, param)

    @story('T131297 产品模块：编辑模块')
    @parametrize('param', more.up_product_module())
    def test_update_prd_module(self, param, _storage):

        with step('修改模块名，描述'):
            param.uri_args({'module_uuid': _storage['module_uuid']})
            up = self.call(prd.UpdateProductModule, param)

            up.check_response('item.name', param.json['item']['name'])

    @story('T131303 产品模块：模块排序')
    @parametrize('param', more.sort_product_module())
    def test_sort_product_module(self, param, _storage):

        with step('前置条件'):
            # 新建模块B
            prm = more.add_product_module()[0]
            prm.json['item']['product'] = _storage['uuid']
            add = self.call(api.ItemsAdd, prm)
            b_mod_uuid = add.json()['item']['uuid']

        with step('同级别的模块排序-将模块A移动到模块B前'):
            param.uri_args({'module_uuid': _storage['module_uuid']})
            self.call(prd.UpdateProductModule, param)

        with step('同级别的模块排序-将模块A移动到模块B后'):
            param.json['item']['sort']['previous_uuid'] = b_mod_uuid
            self.call(prd.UpdateProductModule, param)

    @story('131304 模块：删除模块')
    @parametrize('param', more._delete())
    def test_product_module_delete(self, param, _storage):

        with step('前置条件'):
            # 新建模块C
            prm = more.add_product_module()[0]
            prm.json['item']['product'] = _storage['uuid']
            add = self.call(api.ItemsAdd, prm)
            c_mod_uuid = add.json()['item']['uuid']

        with step('点击删除模块'):
            param.uri_args({'module_uuid': c_mod_uuid})
            self.call(prd.ProductModuleDelete, param)

    @story('T23174 删除产品')
    @story('118968 产品设置-更多：删除产品')
    @parametrize('param', more.product_delete())
    def test_product_delete(self, param, _storage):
        prod_uuids = [_storage['uuid'], _storage['b_uuid']]

        with step('点击删除产品'):
            if prod_uuids:
                for u in prod_uuids:
                    param.uri_args({'product_uuid': u})
                    self.call(prd.ProductDelete, param)

    # 删除所有Pro -产品，预防清除数据异常导致未完全清除数据的情况
    # def test_del_all_pro(self):
    #     param = more.products_data()[0]
    #     res = self.call(api.ItemGraphql, param)
    #
    #     keys = [key['key'] for key in res.value('data.buckets[0].products') if 'Pro - ' in key['name']]
    #
    #     if keys:
    #         for u in keys:
    #             param.uri_args({'product_uuid': u})
    #             self.call(prd.AllProductDelete, param, with_json=False)
