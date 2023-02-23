import json
import time

from falcons.check import go

from main.api import project as prj, more as mr
from main.params import more, com


class ReportInfo:

    @classmethod
    def report_key(cls, report_name, project_uuid=None, token=None):
        """获取报表key"""
        param = more.proj_reports(project_uuid=project_uuid)[0]
        resp = go(prj.ItemGraphql, param, token)

        report_key = [r['key'] for r in resp.value('data.projectReports') if r['name'] == report_name][0]

        return report_key

    @classmethod
    def report_config(cls, key, project_uuid=None, token=None):
        """获取报表config"""
        param = more.proj_reports(project_uuid=project_uuid)[0]
        resp = go(prj.ItemGraphql, param, token, is_print=False)

        report_config = [r['config'] for r in resp.value('data.projectReports') if r['key'] == key][0]

        return json.loads(report_config)

    @classmethod
    def report_info(cls, key, project_uuid=None, token=None):
        """获取报表config"""
        param = more.proj_reports(project_uuid=project_uuid)[0]
        resp = go(prj.ItemGraphql, param, token, is_print=False)

        report_info = [r for r in resp.value('data.projectReports') if r['key'] == key][0]
        report_info['config'] = json.loads(report_info['config'])
        return report_info

    @classmethod
    def report_type(cls, key, project_uuid=None, token=None):
        '''
        获取报告类型
        :param project_uuid:
        :param key:
        :param token:
        :return:
        '''
        param = more.proj_reports(project_uuid=project_uuid)[0]
        resp = go(prj.ItemGraphql, param, token)

        report_type = [r['reportType'] for r in resp.value('data.projectReports') if r['key'] == key][0]

        return report_type

    @classmethod
    def update_report_info(cls, key, param: dict, token=None):
        """更新报表信息"""
        p = more.update_proj_report(key)[0]
        if 'name' in param.keys():
            p = more.update_proj_report(key, name=param['name'])[0]
        if 'report_category' in param.keys():
            p = more.update_proj_report(key, group=param['report_category'])[0]
        p.json['variables'] |= param
        resp = go(prj.ItemGraphql, p, token)

        resp.check_response('data.updateProjectReport.key', key)

        return resp

    @classmethod
    def report_peek(cls, detail_type, config, project_uuid=None, token=None):
        """报表速览"""
        param = more.report_datasets(detail_type)[0]
        if project_uuid:
            param.uri_args({'project_uuid': project_uuid})
        param.json |= dict({'report_config': config})
        time.sleep(4)
        resp = go(mr.ReportPeek, param, token)

        return resp

    @classmethod
    def export_report(cls, detail_type, report_uuid, report_config, project_uuid=None, token=None):
        """导出报表"""
        param = more.export_proj_report(detail_type, report_uuid, project_uuid)[0]
        if project_uuid:
            param.uri_args({'project_uuid': project_uuid})
        param.json['report_config'] |= dict(report_config)

        time.sleep(6)  # 需等待6秒，导出的报表才会有文本信息
        resp = go(prj.ExportProjReport, param, token)

        return resp.response.text

    @classmethod
    def report_save_as(cls, detail_type, category, report_config, project_uuid=None, token=None):
        """报表另存为"""
        param = more.add_proj_report(detail_type, category, pid=project_uuid, config=json.dumps(report_config))[0]
        # param.json_update('variables.config', json.dumps(report_config))
        resp = go(prj.ItemGraphql, param, token)

        return resp.value('data.addProjectReport.key')

    @classmethod
    def report_list(cls, project_uuid=None, token=None):
        param = more.proj_reports(project_uuid=project_uuid)[0]
        resp = go(prj.ItemGraphql, param, token, is_print=False)
        return resp.value('data.projectReports')


def get_defect_severity_default_di_value():
    # 获取属性-严重程度的选项配置
    param = com.gen_stamp({"field": 0})
    fields = go(prj.TeamStampData, param, is_print=False).json()['field']['fields']
    severity_options = [f for f in fields if f['name'] == '严重程度'][0]['options']
    di_map = {
        "致命": 1000000,
        "严重": 300000,
        "一般": 100000,
        "提示": 10000,
        "建议": 0,
        "保留": 0
    }
    di_value_config = [{
        'uuid': s['uuid'],
        'value': di_map[s['value']]
    } for s in severity_options]
    return di_value_config
