from falcons.com.nick import feature, story
from falcons.platform.env_init import user_init, deliver_env_init


@feature('交付插件')
class TestCaseInitDeliver:

    @story("初始化测试环境")
    def test_deliver_env_init(self):
        user_init()
        deliver_env_init(branch='zijin')  # 下载插件和清空默认团队插件信息，不需要该步骤可以注释掉
