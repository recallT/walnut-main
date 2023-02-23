from falcons.com.nick import feature, story
from falcons.platform.env_init import env_init, user_init


@feature('开放能力兼容性测试-初始化测试环境')
class TestCaseInitAbility:
    @story("初始化测试环境")
    def test_set_user_token(self):
        user_init()
        env_init()  # 下载插件和清空默认团队插件信息，不需要该步骤可以注释掉
