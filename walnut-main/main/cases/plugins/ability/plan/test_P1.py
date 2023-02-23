from falcons.com.nick import *
from falcons.platform.abilites.ability_plugin_lifecycle import *


@feature('P1 测试用例')
class TestCaseP1:

    @story("业务能力")
    @title("脚本属性-数字")
    def test_run_script_float(self, admin_token):
        do_exec_func("script-float-1.0.0-check", headers=admin_token)

    @story("业务能力")
    @title("脚本属性-单选")
    def test_run_script_select(self, admin_token):
        do_exec_func("script-select-1.0.0-check", headers=admin_token)

    @story("业务能力")
    @title("脚本属性-多选")
    def test_run_script_mutation_select(self, admin_token):
        do_exec_func("script-mutation-select-1.0.0-check", headers=admin_token)
