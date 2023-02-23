from falcons.com.nick import feature
from falcons.platform.public.topluginhelper import clear_plugins_on_teams


@feature('开放能力兼容性测试-停用卸载插件')
class TestCaseClear:
    def test_clear_plugins(self, constants):
        # 清空对应环境的插件信息
        clear_plugins_on_teams()
