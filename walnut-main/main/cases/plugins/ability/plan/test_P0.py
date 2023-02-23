from falcons.com.nick import *
from falcons.platform.abilites.ability_plugin_lifecycle import *


def run_testcase_install_enable(testcase, *args, **kwargs):
    # 安装测试用例依赖的插件
    do_install(testcase, *args, **kwargs)

    # 启用测试用例依赖的插件
    do_enable(testcase, *args, **kwargs)


# 所有插件安装初始化
@feature('P0 测试用例 插件安装')
class TestP0CasePluginInstall:

    @story("插件日志能力插件安装")
    def test_run_install_init_pluginLog(self):
        run_testcase_install_enable('pluginLog-1.0.0-check')  # 版本1.0.0的插件日志能力校验

    @story("插件数据库能力插件安装")
    def test_run_install_init_pluginDatabase(self):
        run_testcase_install_enable('pluginDatabase-1.0.0-check')  # 版本1.0.0的插件数据库能力校验

    @story("系统数据库能力插件安装")
    def test_run_install_init_systemDatabase(self):
        run_testcase_install_enable('systemDatabase-1.0.0-check')  # 版本1.0.0的系统数据库能力校验

    @story("插件文件系统能力插件安装")
    def test_run_install_init_pluginFileSystem(self):
        run_testcase_install_enable('pluginFileSystem-1.0.0-check')  # 版本1.0.0的插件文件系统能力校验

    @story("插件自定义权限点能力校验能力插件安装")
    def test_run_install_init_customPermissionPoint(self):
        run_testcase_install_enable('customPermissionPoint-1.0.0-check')  # 版本1.0.0插件自定义权限点能力校验

    @story("插件自定义配置页面能力插件安装")
    def test_run_install_init_customConfigurationPage(self):
        run_testcase_install_enable('customConfigurationPage-1.0.0-check')  # 版本1.0.0插件自定义配置页面

    @story("插件接口标准错误处理能力插件安装")
    def test_run_install_init_interfaceStandardErrorHandling(self):
        run_testcase_install_enable('interfaceStandardErrorHandling-1.0.0-check')  # 版本1.0.0插件接口标准错误处理

    @story("多语言能力插件安装")
    def test_run_install_init_multi_language(self):
        run_testcase_install_enable('multi-language-1.0.0-check')  # 版本1.0.0的多语言

    @story("消息通知能力插件安装")
    def test_run_install_init_notify(self):
        run_testcase_install_enable('notify-1.0.0-check')  # 版本1.0.0的消息通知

    @story("插件超级用户能力插件安装")
    def test_run_install_init_rootUser(self):
        run_testcase_install_enable('rootUser-1.0.0-check')  # 版本1.0.0的插件超级用户

    @story("审计日志能力插件安装")
    def test_run_install_init_auditLog(self):
        run_testcase_install_enable('auditLog-1.0.0-check')  # 版本1.0.0的审计日志

    @story("文件上传能力插件安装")
    def test_run_install_init_uploadFile(self):
        run_testcase_install_enable('uploadFile-1.0.0-check')  # 版本1.0.0的文件上传

    @story("接口访问能力插件安装")
    def test_run_install_init_fetchHttp(self):
        run_testcase_install_enable('fetchHttp-1.0.0-check')  # 版本1.0.0的接口访问能力校验

    @story("标品接口替换能力插件安装")
    def test_run_install_init_projectReplace(self):
        run_testcase_install_enable('projectReplace-1.0.0-check')

    @story("标品接口前置能力插件安装")
    def test_run_install_init_projectPre(self):
        run_testcase_install_enable('projectPre-1.0.0-check')

    @story("标品接口后置能力插件安装")
    def test_run_install_init_projectSuffix(self):
        run_testcase_install_enable('projectSuffix-1.0.0-check')

    @story("wiki接口替换能力插件安装")
    def test_run_install_init_wikiapiReplace(self):
        run_testcase_install_enable('wikiapiReplace-1.0.0-check')

    @story("wiki接口前置能力插件安装")
    def test_run_install_init_wikiapiPre(self):
        run_testcase_install_enable('wikiapiPre-1.0.0-check')

    @story("wiki接口后置能力插件安装")
    def test_run_install_init_wikiapiSuffix(self):
        run_testcase_install_enable('wikiapiSuffix-1.0.0-check')

    @story("简单登录能力插件安装")
    def test_run_install_init_simpleAuth(self):
        run_testcase_install_enable('simpleAuth-1.0.0-check')  # 版本1.0.0 简单登录能力校验

    @story("事件劫持能力插件安装")
    @pytest.mark.skip(reason='环境测试暂时有误')
    def test_run_install_init_item_mutation(self):
        run_testcase_install_enable('item-mutation-1.0.0-check')  # 版本1.0.0 事件劫持能力校验

    @story("Account 支持第三方登录能力插件安装")
    def test_run_install_init_account(self, admin_token):
        run_testcase_install_enable('account-1.0.0-check')  # 版本1.0.0 Account 支持第三方登录能力

    @story("脚本属性-数字 能力插件安装")
    def test_run_install_script_float(self, admin_token):
        run_testcase_install_enable('script-float-1.0.0-check')  # 版本1.0.0 脚本属性数字能力

    @story("脚本属性-单选 能力插件安装")
    def test_run_install_init_script_select(self, admin_token):
        run_testcase_install_enable('script-select-1.0.0-check')  # 版本1.0.0 脚本属性单选能力

    @story("脚本属性-多选 能力插件安装")
    def test_run_install_init_script_mutation_select(self, admin_token):
        run_testcase_install_enable('script-mutation-select-1.0.0-check')  # 版本1.0.0 脚本属性多选能力


@feature('P0 测试用例')
class TestCaseP0:

    @story("基础能力")
    @title("插件日志")
    def test_run_Plugin(self):
        do_exec_func("pluginLog-1.0.0-check", functions=['test0'])

    @story("基础能力")
    @title("插件数据库")
    def test_run_pluginDatabase(self):
        do_exec_func("pluginDatabase-1.0.0-check")

    @story("基础能力")
    @title("插件文件系统")
    def test_run_pluginFileSystem(self):
        do_exec_func("pluginFileSystem-1.0.0-check")

    @story("基础能力")
    @title("自定义权限点能力校验")
    def test_run_pluginCustomPermissionPoint(self):
        do_exec_func("customPermissionPoint-1.0.0-check")

    @story("基础能力")
    @title("自定义配置页面")
    def test_run_customConfigurationPage(self):
        do_exec_func("customConfigurationPage-1.0.0-check")

    @story("基础能力")
    @title("插件接口标准错误处理")
    def test_run_interfaceStandardErrorHandling(self):
        do_exec_func("interfaceStandardErrorHandling-1.0.0-check")

    @story("基础能力")
    @title("多语言")
    def test_run_multi_language(self):
        do_exec_func("multi-language-1.0.0-check")

    @story("基础能力")
    @title("消息通知")
    def test_run_notify(self):
        do_exec_func('notify-1.0.0-check')  # 消息通知

    @story("基础能力")
    @title("插件超级用户")
    def test_run_rootUser(self):
        do_exec_func('rootUser-1.0.0-check')  # 插件超级用户

    @story("基础能力")
    @title("审计日志")
    def test_run_auditLog(self, admin_token):
        do_exec_func('auditLog-1.0.0-check', headers=admin_token)  # 审计日志

    @story("基础能力")
    @title("文件上传")
    def test_run_uploadFile(self, admin_token):
        do_exec_func('uploadFile-1.0.0-check', headers=admin_token)  # 文件上传

    @story("接口能力")
    @title("接口访问")
    def test_run_fetchHttp(self):
        do_exec_func('fetchHttp-1.0.0-check')

    @story("接口能力")
    @title("接口注册")
    def test_run_apiRegister(self):
        do_exec_func('projectRegister-1.0.0-check')

    @story("接口能力")
    @title("标品接口替换")
    def test_run_ProReplace(self):
        do_exec_func('projectReplace-1.0.0-check')

    @story("接口能力")
    @title("标品接口前置")
    def test_run_proPre(self):
        do_exec_func('projectPre-1.0.0-check')

    @story("接口能力")
    @title("标品接口后置")
    def test_run_proSuf(self):
        do_exec_func('projectSuffix-1.0.0-check')

    @story("接口能力")
    @title("wiki接口替换")
    def test_run_wikiReplace(self):
        do_exec_func('wikiapiReplace-1.0.0-check')

    @story("接口能力")
    @title("wiki接口前置")
    def test_run_wikiPre(self):
        do_exec_func('wikiapiPre-1.0.0-check')

    @story("接口能力")
    @title("wiki接口后置")
    def test_run_wikiSuf(self):
        do_exec_func('wikiapiSuffix-1.0.0-check')

    @story("业务能力")
    @title("简单登录")
    def test_run_simpleAuth(self):
        do_exec_func("simpleAuth-1.0.0-check")

    @story("业务能力")
    @title("事件劫持")
    @pytest.mark.skip(reason='环境测试暂时有误')
    def test_run_item_mutation(self, admin_token):
        do_exec_func("item-mutation-1.0.0-check", headers=admin_token)

    @story("业务能力")
    @title("Account 第三方登录")
    @pytest.mark.skip(reason='环境测试暂时有误')
    def test_run_account(self, admin_token):
        do_exec_func("account-1.0.0-check", headers=admin_token)
