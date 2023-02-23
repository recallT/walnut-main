from falcons.check import Checker
from falcons.com.nick import parametrize, feature, fixture, story, step, mark

from main.actions.sprint import SprintAction
from main.api import more as prd
from main.api import project as api
from main.params import data, more


@fixture(scope='module')
def _storage():
    p = {}
    return p


@mark.smoke
@feature('版本管理相关')
class TestVersions(Checker):

    @story('T143705 新建版本')
    @parametrize('param', data.version_add())
    def test_version_add(self, param, _storage):
        uuids = []
        with step('新建版本，填写名称等信息'):
            for n in range(3):
                param.json['version']['title'] = f'V-Status-{n}'
                add = self.call(api.VersionAdd, param)

                add.check_response('version.category', 'todo')

                uuids.append(add.json()['version']['uuid'])

        _storage |= {'uuids': uuids}

        with step('新建版本，检验名称必填项'):
            param.json['version']['title'] = ''
            add = self.call(api.VersionAdd, param, status_code=400)
            add.check_response('errcode', 'InvalidParameter.Version.Title', check_type='contains')

    @story('143716 状态管理：版本状态切换检查')
    @parametrize(('category', 'index'), (('in_progress', 1), ('done', 2)))  # 进行中, 已完成
    def test_version_status_change(self, category, index, _storage):
        param = more.version_update()[0]

        with step('状态变更'):
            param.json['version']['uuid'] = _storage['uuids'][index]
            param.json['version']['category'] = category
            param.uri_args({'version_uuid': _storage['uuids'][index]})
            up = self.call(api.VersionUpdate, param)

            up.check_response('version.category', category)

    # @story('更新版本-分配人员错误')
    # @mark.xfail(reason='接口校验失败812')
    # @parametrize('param', data.version_update())
    # def test_version_update_assign_812(self, param, _storage):
    #     for s in _storage['uuids']:
    #         param.uri_args({'version_uuid': s})
    #         param.json['version']['assign'] = 'nobody'
    #         self.call(api.VersionUpdate, param, status_code=812)

    @story('T143708 状态管理：未开始版本')
    def test_version_list(self):
        param = more._search()[0]

        with step('查看未开始tab'):
            q = self.call(api.VersionList, param)
            category = [c['category'] for c in q.json()['versions']]
            assert 'in_progress' in category

    @story('T143670 版本：关联产品')
    @story('143707 版本管理-关联产品：添加关联产品')
    @parametrize('param', more.version_relate_product())
    def test_version_relate_product(self, param, _storage):

        with step('前置条件'):
            # 新建产品
            prm = data.product_add()[0]
            rp = self.call(api.ItemsAdd, prm)
            prd_uuid = rp.json()['item']['uuid']

            _storage |= {'prd_uuid': prd_uuid}

        with step('选择产品，提交'):
            param.json['product_uuids'].append(prd_uuid)
            param.uri_args({'version_uuid': _storage['uuids'][0]})

            vr = self.call(prd.VersionRelateProduct, param)
            vr.check_response('version.product_uuids[0]', prd_uuid)

    @story('T143717 关联产品操作')
    def test_version_product_delete(self, _storage):

        with step('移除产品'):
            param = more._delete()[0]
            param.uri_args({'version_uuid': _storage['uuids'][0], 'product_uuid': _storage['prd_uuid']})
            self.call(prd.VersionProductDelete, param)

    @story('更新版本')
    @story('143713 状态管理：版本操作检查')
    @parametrize('param', data.version_update())
    def test_version_update(self, param, _storage):
        for uuid in _storage['uuids']:
            param.uri_args({'version_uuid': uuid})
            up = self.call(api.VersionUpdate, param)

            up.check_response('version.uuid', uuid)
            up.check_response('version.title', param.json['version']['title'])

    @story('T143671 版本：关联迭代')
    @parametrize('param', more.version_relate_sprint())
    def test_version_relate_sprint(self, param, _storage):

        with step('前置条件'):
            # 新建迭代
            sprint_uuid = SprintAction.sprint_add()

            _storage |= {'sprint_uuid': sprint_uuid}

        with step('选择迭代A，提交'):
            param.json['sprint_uuid'] = sprint_uuid
            param.uri_args({'version_uuid': _storage['uuids'][0]})
            self.call(prd.VersionRelateSprint, param)

    @story('T143714 关联迭代操作')
    def test_version_sprint_delete(self, _storage):

        with step('移除迭代'):
            param = more._delete()[0]
            param.uri_args({'version_uuid': _storage['uuids'][0], 'sprint_uuid': _storage['sprint_uuid']})
            self.call(prd.VersionSprintDelete, param)

    @story('T143709 版本日志支持富文本编辑')
    @parametrize('desc', ('版本日志Test,TEST', 'a href=\"https://ones.ai/\" target=\"_blank\">网页插入</a>'))
    def test_version_rich_edit(self, desc, _storage):
        param = more.version_update()[0]
        with step('编辑版本日志'):
            param.json['version']['desc'] = f'<p>{desc}</p>\n'
            param.uri_args({'version_uuid': _storage['uuids'][0]})
            self.call(api.VersionUpdate, param)

    @story('删除版本')
    def test_version_delete(self, _storage):
        param = more._delete()[0]
        if _storage['uuids']:
            for uuid in _storage['uuids']:
                param.uri_args({'version_uuid': uuid})
                self.call(api.VersionDelete, param)

    # 删除所有Version -产品，预防清除数据异常导致未完全清除数据的情况
    # def test_all_version_delete(self):
    #     param = more._delete()[0]
    #     resp = self.call(api.VersionList, param, with_json=False)
    #
    #     version_uuids = [v['uuid'] for v in resp.value('versions') if 'ProVersion' in v['title']]
    #
    #     if version_uuids:
    #         for uuid in version_uuids:
    #             param.uri_args({'version_uuid': uuid})
    #             self.call(api.VersionDelete, param)
