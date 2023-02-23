"""
@File    ：test_man_hour.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2022/3/17
@Desc    ：测试工作项登记工时
"""
from falcons.check import CheckerChain
from falcons.com.nick import feature, fixture, story, parametrize, step

from main.actions.pro import PrjAction
from main.actions.task import TaskAction
from main.api import project as prj
from main.api import task as tsk
from main.params import task as p


@fixture(scope='module')
def task():
    """准备一条测试任务"""

    # 运行维护：开始前，先切工时模式为：简单模式
    with step('全局配置：工时模式切换为"简单模式"'):
        PrjAction.work_hour_configs_update('simple')

    i = TaskAction.new_issue()

    return i[0]


@fixture(scope='module')
def man_hour_key():
    """缓存工时key"""

    return []


@fixture(scope='module')
def del_task(task):
    """准备一条测试任务"""
    yield
    TaskAction.del_task(task)


@feature('任务管理-任务详情-工时信息')
class TestManHour(CheckerChain):
    """工时相关操作"""

    @story('添加工时')
    @story('T119257 登记工时')
    @story('T23345 成员工时：检查和操作成员工时')
    @parametrize('param', p.add_man_hour())
    def test_add_man_hour_simple_module(self, param, task, man_hour_key):
        """"""

        param.json_update('variables.task', task)
        p_message = p.task_messages()[0]
        self.call('添加工时', prj.ItemGraphql, param) \
            .assert_response('data.addManhour.key', 'manhour', 'contains') \
            .cache_to(man_hour_key, 'data.addManhour.key') \
            .update_url(p_message, {'task_uuid': task}) \
            .call('查看工作项动态', tsk.TaskMessages, p_message)

    @story('T119258 登记工时：编辑登记工时记录')
    @parametrize('param', p.modify_man_hour())
    def test_modify_man_hour_simple_module(self, param, task, man_hour_key):
        """"""

        param.json_update('variables.task', task)
        param.json_update('variables.key', man_hour_key[0])

        p_fetch = p.fetch_man_hours()[0]
        p_fetch.json_update('variables.manhourFilter.task_in', [task, ])

        self.call('修改工时', prj.ItemGraphql, param) \
            .assert_response('data.updateManhour.key', man_hour_key[0]) \
            .call('获取任务工时信息', prj.ItemGraphql, p_fetch) \
            .assert_response('data.manhours[0].hours', 30 * 10000)

    @story('T119257 登记工时')
    @parametrize('param', p.add_man_hour(hour=400))
    def test_add_man_hour_400h(self, param, task, man_hour_key):
        """400小时工时超标 - 现在没有超标限制了"""

        param.json_update('variables.task', task)
        self.call('添加工时', prj.ItemGraphql, param)

    @story('141319 预估工时：新增预估工时')
    @parametrize('param', p.assess_man_hour())
    def test_add_assess_manhour(self, param, task):
        """"""

        param.uri_args({'task_uuid': task})
        self.call('添加预估工时', tsk.TaskAssessManHourUpdate, param) \
            .assert_response('code', 200)

        info_p = p.task_info()[0]
        info_p.uri_args({'task_uuid': task})

        self.call('检查预估工时', tsk.TaskInfo, info_p) \
            .assert_response('assess_manhour', param.json_value('value'))

    @story('修改预估工时')
    @parametrize('param', p.assess_man_hour())
    def test_modify_assess_manhour(self, param, task):
        """"""

        param.uri_args({'task_uuid': task})
        param.json_update('value', 6 * 10000)  # 将任务预估工时修改小一点： 6 小时
        self.call('修改预估工时', tsk.TaskAssessManHourUpdate, param) \
            .assert_response('code', 200)

        info_p = p.task_info()[0]
        info_p.uri_args({'task_uuid': task})

        self.call('检查预估工时', tsk.TaskInfo, info_p) \
            .assert_response('assess_manhour', param.json_value('value'))

    @story('T141324 预估偏差：有预估工时、登记工时或剩余工时')
    @parametrize('param', p.task_info())
    def test_check_estimate_variance(self, param, task):
        """检查工时偏差"""

        param.uri_args({'task_uuid': task})

        self.call('检查预估工时', tsk.TaskInfo, param)
        j = self.ins.json()
        assess_val = j['assess_manhour']  # 预估工时
        total_val = j['total_manhour']  # 已用工时
        estimate_val = j['estimate_variance']  # 预计偏差

        assert estimate_val == assess_val - total_val

    @story('T122347 工时进度：有剩余工时，有登记工时')
    @story('141318 预估工时：新增剩余工时')
    @parametrize('param', p.task_info())
    def test_check_time_progress(self, param, task):
        """检查工时工时进度"""

        param.uri_args({'task_uuid': task})

        self.call('检查预估工时', tsk.TaskInfo, param)
        j = self.ins.json()

        assess_val = j['assess_manhour']  # 预估工时
        total_val = j['total_manhour']  # 已用工时
        progress_val = j['time_progress']  # 工时进度
        print(progress_val, total_val % assess_val, total_val, assess_val, total_val >= assess_val)
        assert progress_val == (total_val % assess_val) if total_val < assess_val else 100 * 100000

    @story('T141314 预估工时：删除预估工时')
    @parametrize('param', p.assess_man_hour())
    def test_del_assess_manhour(self, param, task):
        """"""

        param.uri_args({'task_uuid': task})
        param.json_update('value', None)  # 将任务预估工时设为空
        self.call('删除预估工时', tsk.TaskAssessManHourUpdate, param) \
            .assert_response('code', 200)

        info_p = p.task_info()[0]
        info_p.uri_args({'task_uuid': task})

        self.call('检查预估工时', tsk.TaskInfo, info_p) \
            .assert_response('assess_manhour', param.json_value('value'))

    @story('T119262 登记工时：删除登记工时')
    @parametrize('param', p.delete_man_hour())
    def test_del_man_hour_simple_module(self, param, man_hour_key):
        """"""

        param.json_update('variables.key', man_hour_key[0])
        self.call('删除工时', prj.ItemGraphql, param) \
            .assert_response('data.deleteManhour.key', man_hour_key[0])

    @story('预估工时：添加剩余工时')
    @parametrize('param', p.remaining_hour())
    def test_add_ramaining_hour_simple_module(self, param, task):
        """"""

        param.uri_args({'task_uuid': task})
        self.call('添加剩余工时', tsk.TaskRemainingHourUpdate, param) \
            .assert_response('code', 200)
        info_p = p.task_info()[0]
        info_p.uri_args({'task_uuid': task})
        self.call('查询任务剩余工时', tsk.TaskInfo, info_p) \
            .assert_response('remaining_manhour', param.json_value('value'))

    @story('T141320 预估工时：修改剩余工时')
    @parametrize('param', p.remaining_hour())
    def test_modify_ramaining_hour_simple_module(self, param, task):
        """"""

        param.uri_args({'task_uuid': task})
        param.json_update('value', 1 * 100000)  # 修改剩余工时为1小时
        self.call('修改剩余工时', tsk.TaskRemainingHourUpdate, param) \
            .assert_response('code', 200)
        info_p = p.task_info()[0]
        info_p.uri_args({'task_uuid': task})
        self.call('查询任务剩余工时', tsk.TaskInfo, info_p) \
            .assert_response('remaining_manhour', param.json_value('value'))

    @story('T141313 预估工时：删除剩余工时')
    @parametrize('param', p.remaining_hour())
    def test_del_ramaining_hour_simple_module(self, param, task):
        """"""

        param.uri_args({'task_uuid': task})
        param.json_update('value', None)  # 修改剩余工时为空
        self.call('删除剩余工时', tsk.TaskRemainingHourUpdate, param) \
            .assert_response('code', 200)
        info_p = p.task_info()[0]
        info_p.uri_args({'task_uuid': task})
        self.call('查询任务剩余工时', tsk.TaskInfo, info_p) \
            .assert_response('remaining_manhour', param.json_value('value'))

        message_p = p.task_messages()[0]
        message_p.uri_args({'task_uuid': task})

        self.call('检查任务日志消息', tsk.TaskMessages, message_p) \
            .assert_response('messages[0].action', 'delete') \
            .assert_response('messages[0].ext.field_name', '剩余工时') \
            .assert_response('messages[0].ext.new_value', '')

    # -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*-
    # 以下三条用例需要在系统设置中将工时模式调为汇总模式
    # 执行完后改为简单莫式，以免影响其他用例执行
    # -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*-

    @story('T130754 汇总模式-工作项详情：成员登记工时')
    @parametrize('param', p.add_man_hour(mode='detailed'))
    def test_add_man_hour_detailed_module(self, param, task):
        """"""
        # 第一步调整为汇总模式
        PrjAction.work_hour_configs_update('detailed')

        param.json_update('variables.task', task)
        p_message = p.task_messages()[0]
        self.call('汇总模式添加工时', prj.ItemGraphql, param) \
            .assert_response('data.addManhour.key', 'manhour', 'contains') \
            .update_url(p_message, {'task_uuid': task}) \
            .call('查看工作项动态', tsk.TaskMessages, p_message)

    @story('T130757 汇总模式-工作项详情：新增成员预估工时（每日）')
    @parametrize('param', p.add_man_hour_detail_estimated('avg'))
    def test_add_assess_manhour_avg_detailed_mode(self, param, task):
        """"""
        param.json_update('variables.task', task)
        p_message = p.task_messages()[0]
        self.call('新增成员预估工时（每日）', prj.ItemGraphql, param) \
            .assert_response('data.addManhour.key', 'manhour', 'contains') \
            .update_url(p_message, {'task_uuid': task}) \
            .call('查看工作项动态', tsk.TaskMessages, p_message)

    @story('T130758 汇总模式-工作项详情：新增成员预估工时（汇总）')
    @parametrize('param', p.add_man_hour_detail_estimated('sum'))
    def test_add_assess_manhour_sum_detailed_mode(self, param, task):
        """"""
        param.json_update('variables.task', task)
        p_message = p.task_messages()[0]
        self.call('新增成员预估工时（汇总）', prj.ItemGraphql, param) \
            .assert_response('data.addManhour.key', 'manhour', 'contains') \
            .update_url(p_message, {'task_uuid': task}) \
            .call('查看工作项动态', tsk.TaskMessages, p_message)

        # 调为简单模式
        PrjAction.work_hour_configs_update('simple')
    # -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*-
    # 以上三条用例需要在系统设置中将工时模式调为汇总模式
    # -*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*--*-*-
