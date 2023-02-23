from falcons.ops import ProjectOps


class VersionRelateProduct(ProjectOps):
    """版本关联产品"""
    uri = '/team/{team_uuid}/version/{version_uuid}/products/add'
    name = '版本关联产品'
    api_type = 'POST'


class VersionRelateSprint(ProjectOps):
    """版本关联迭代"""
    uri = '/team/{team_uuid}/version/{version_uuid}/sprints/add'
    name = '版本关联产迭代'
    api_type = 'POST'


class UpdateProductModule(ProjectOps):
    """产品模块更新"""
    uri = '/team/{team_uuid}/item/product_module-{module_uuid}/update'
    name = '产品模块更新'
    api_type = 'POST'


class ProductModuleDelete(ProjectOps):
    """删除产品模块"""
    uri = '/team/{team_uuid}/item/product_module-{module_uuid}/delete'
    name = '删除产品模块'
    api_type = 'POST'


class ProductMemberDelete(ProjectOps):
    """删除产品成员"""
    uri = '/team/{team_uuid}/permission_rule/{uuid}/delete'
    name = '删除产品成员'
    api_type = 'POST'


class ProductDelete(ProjectOps):
    """删除产品"""
    uri = '/team/{team_uuid}/item/product-{product_uuid}/delete'
    name = '删除产品'
    api_type = 'POST'


class AllProductDelete(ProductDelete):
    """删除所有产品"""
    uri = '/team/{team_uuid}/item/{product_uuid}/delete'
    name = '删除所有产品'
    api_type = 'POST'


# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*


class VersionProductDelete(ProjectOps):
    uri = '/team/{team_uuid}/version/{version_uuid}/product/{product_uuid}/delete'
    name = '删除版本关联的产品'
    api_type = 'POST'


class VersionSprintDelete(ProjectOps):
    uri = '/team/{team_uuid}/version/{version_uuid}/sprint/{sprint_uuid}/delete'
    name = '删除版本关联的迭代'
    api_type = 'POST'


# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*


class ReportExport(ProjectOps):
    uri = '/team/{team_uuid}/reports/export'
    name = '报表导出'
    api_type = 'POST'


class ReportPeek(ProjectOps):
    uri = '/team/{team_uuid}/project/{project_uuid}/reports/peek'
    name = '报表数据集'
    api_type = 'POST'
