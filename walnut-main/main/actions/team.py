from falcons.check import go
from falcons.ops import ProjectOps, WikiOps
from typing import Union

from main.params import com
from main.api import plugin
from main.params.const import ACCOUNT
from main.api import project


class TeamAction:

    @classmethod
    def org_stamp(cls, param: dict, org_uuid=None, token: dict = None) -> Union[ProjectOps, WikiOps]:
        """
        调用全局org_stamp类型信息
        :param param: 查询数据 参数 如 `{"org_teams": 0}`
        :param token: 可选
        :return:
        """
        if not org_uuid:
            team_info = cls.team_info(ACCOUNT.user.team_uuid)
            org_uuid = team_info['org_uuid']
        param = com.gen_stamp(param)
        param.uri_args({"org_uuid": org_uuid})
        res = go(plugin.OrgStampsData, param, token, is_print=False)

        return res

    @classmethod
    def team_info(cls, uuid):
        """
        团队信息
        :param uuid: 团队uuid
        :return: team_info, team_no : 团队信息，团队列表序号
        """
        p = com.generate_param({})[0]
        token_info = go(project.TokenInfo, p)
        tt = [(i, t) for i, t in enumerate(token_info.value('teams')) if t['uuid'] == uuid]
        if tt:
            return tt[0][1], tt[0][0] + 1
        else:
            raise ValueError(f'团队不存在，team_uuid: {uuid}')

    @classmethod
    def global_user(cls, token=None):
        p = com.generate_param({})[0]
        token_info = go(project.TokenInfo, p, token=token, is_print=False)
        return token_info.value('user')

    @classmethod
    def org_users(cls):
        res = cls.org_stamp({
            "org_members": 0
        })
        return res.value('org_members.members')
