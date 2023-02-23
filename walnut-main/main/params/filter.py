from main.params.const import ACCOUNT


def defect_report_default_filter(detect_it_uuid: str, exclude_it_uuids: [str], project_uuid=None,
                                 online_yes_uuid=None):
    '''
    缺陷报表-默认筛选配置
    :return:
    '''
    project_uuid = project_uuid if project_uuid else ACCOUNT.project_uuid
    should_must = [
        {
            'in': {
                'field_values.field007': [detect_it_uuid]
            }
        },
        {
            'not_in': {
                'field_values.field021': exclude_it_uuids
            }
        }]
    if online_yes_uuid:
        should_must.append({
            'in': {
                'field_values.field031': [
                    online_yes_uuid]
            }
        })

    return {
        'must': [
            {
                'must': [
                    {
                        'in': {
                            'field_values.field006': [project_uuid]
                        }
                    }]
            },
            {
                'should': [
                    {
                        'must': should_must
                    }]
            }]
    }
