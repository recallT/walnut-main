#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：test_task_graphql_2.py
@Author  ：Zeno
@Email   ：zhangyongjun@ones.ai
@Date    ：2021/12/10 
@Desc    ：任务管理筛选器测试用例
"""

from falcons.com.nick import feature, story, mark, parametrize, step

from main.api.project import ItemGraphql
from main.params import graphql


@mark.smoke
@feature('任务管理-任务筛选')
class TestTaskFilter:
    @story('133787 任务管理-任务筛选-系统关联关系：根据「关联」筛选（包含）')
    @story('133792 任务管理-任务筛选-系统属性：根据「标题」筛选（包含）')
    @story('133797 任务管理-任务筛选-系统属性：根据「处理结果」筛选（包含）')
    @story('133808 任务管理-任务筛选-系统属性：根据「创建时间」筛选（等于）（准确日期）')
    @story('133814 任务管理-任务筛选-系统属性：根据「创建者」筛选（包含）（成员）')
    @story('133838 任务管理-任务筛选-系统属性：根据「发布日期」筛选（等于）（准确日期）')
    @story('133845 任务管理-任务筛选-系统属性：根据「负责人」筛选（包含）（成员）')
    @story('133861 任务管理-任务筛选-系统属性：根据「更新时间」筛选（等于）（准确日期）')
    @story('133874 任务管理-任务筛选-系统属性：根据「关联发布」筛选（包含）')
    @story('133888 任务管理-任务筛选-系统属性：根据「关注者」筛选（包含）（成员）')
    @story('133901 任务管理-任务筛选-系统属性：根据「ID」筛选（等于）')
    @story('133935 任务管理-任务筛选-系统属性：根据「截止日期」筛选（等于）（准确日期）')
    @story('133943 任务管理-任务筛选-系统属性：根据「解决者」筛选（包含）（成员）')
    @story('133958 任务管理-任务筛选-系统属性：根据「进度」筛选（等于）')
    @story('133963 任务管理-任务筛选-系统属性：根据「缺陷类型」筛选（包含）')
    @story('133969 任务管理-任务筛选-系统属性：根据「是否线上缺陷」筛选（包含）')
    @story('133975 任务管理-任务筛选-系统属性：根据「所属产品」筛选（包含）')
    @story('133981 任务管理-任务筛选-系统属性：根据「所属迭代」筛选（包含）')
    @story('133987 任务管理-任务筛选-系统属性：根据「所属功能模块」筛选（包含）')
    @story('133993 任务管理-任务筛选-系统属性：根据「严重程度」筛选（包含）')
    @story('133998 任务管理-任务筛选-系统属性：根据「优先级」筛选（包含）')
    @story('134001 任务管理-任务筛选-系统属性：根据「状态类型」筛选（包含）')
    @story('134004 任务管理-任务筛选-系统属性：根据「状态」筛选（包含）')
    @story('134007 任务管理-任务筛选-系统属性：根据「子工作项类型」筛选（包含）')
    @story('134015 任务管理-任务筛选-自定义关联关系-「单向多对多」：根据「发起关联方描述」筛选（包含）')
    @story('134030 任务管理-任务筛选-自定义关联关系：根据「相互关联关系」筛选（包含）')
    @story('134042 任务管理-任务筛选-自定义属性：根据「出现时间」筛选（等于）（准确日期）')
    @story('134053 任务管理-任务筛选-自定义属性：根据「单选菜单」筛选（包含）')
    @story('134060 任务管理-任务筛选-自定义属性：根据「单选成员」筛选（包含）（成员）')
    @story('134079 任务管理-任务筛选-自定义属性：根据「多选菜单」筛选（包含）')
    @story('134086 任务管理-任务筛选-自定义属性：根据「多选成员」筛选（包含）（成员）')
    @story('134099 任务管理-任务筛选-自定义属性：根据「多选项目」筛选（包含）')
    @story('134128 任务管理-任务筛选-自定义属性：根据「日期」筛选（等于）（准确日期）')
    @story('134141 任务管理-任务筛选-自定义属性：根据「时间」筛选（等于）（准确日期）')
    @story('134176 任务管理-任务筛选：验证或关系')
    @story('134177 任务管理-任务筛选：验证且关系')
    @story('133909 任务管理-任务筛选-系统属性：根据「计划开始日期」筛选（等于）（准确日期）')
    @story('133922 任务管理-任务筛选-系统属性：根据「计划完成日期」筛选（等于）（准确日期）')
    @parametrize('param', graphql.task_graphql_1())
    def test_task_filter_1(self, param):
        """不勾选自定义复制的数据"""
        cpy = ItemGraphql()
        # 调用接口
        cpy.call(param.json, **param.extra)
        # 检查接口响应码
        cpy.is_response_code(200)


@mark.smoke
@feature('项目列表-筛选-系统属性')
class TestProjectFilter:
    @story('138016 项目列表-筛选-系统属性：根据「创建时间」筛选（等于）（准确日期）')
    @story('138073 项目列表-筛选-系统属性：根据「项目负责人」筛选（包含）（成员）')
    @story('138083 项目列表-筛选-系统属性：根据「项目名称」筛选（包含）')
    @story('138087 项目列表-筛选-系统属性：根据「项目状态」筛选（包含）')
    @parametrize('param', graphql.project_graphql())
    def test_project_filter(self, param):
        """筛选-系统属性"""
        cpy = ItemGraphql()
        step_name, p = param
        with step(step_name):
            # 调用接口
            cpy.call(p.json, **p.extra)
            # 检查接口响应码
            cpy.is_response_code(200)
