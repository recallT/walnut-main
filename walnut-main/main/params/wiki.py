from falcons.helper import mocks
from falcons.ops import generate_param


def add_page_classification():
    """新增页面分类"""
    return generate_param({
        "query": "mutation {\n    addSpaceCategory (name: $name parent: $parent) {\n        key\n        name\n        parent {\n            name\n        }\n        position\n        isDefault\n    }\n} ",
        "variables": {
            "name": f"页面组分类" + mocks.num(),
            "parent": ""
        }
    })


def add_wiki_space(is_open_share_page):
    """新增页面组"""
    return generate_param({
        "title": f"页面组" + mocks.num(),
        "description": "",
        "homepage": f"页面组" + mocks.num(),
        "is_open_share_page": is_open_share_page,
        "space_category_uuid": ""
    })


def add_wiki_pages():
    """"新增wiki pages"""
    return generate_param({
        "page_uuid": mocks.ones_uuid(),
        "title": "wiki_pages_title" + mocks.num(),
        "content": "<p>content-content</p>\n",
        "status": 1
    })


def update_wiki_pages(page_uuid, from_version=0):
    """更新wiki页面"""
    return generate_param({
        "from_version": from_version,
        "page_uuid": page_uuid,
        "title": "title" + mocks.num(),
        "content": "<p>content-content</p>\n",
        "status": 2
    })


def deploy_wiki_pages(space_uuid, page_uuid, uuid):
    """发布wiki页面"""
    return generate_param({
        "title": "test-api-wiki-title" + mocks.num(),
        "content": "<p>content-content</p>\n",
        "space_uuid": space_uuid,
        "page_uuid": page_uuid,
        "uuid": uuid,
        "is_published": True
    })


def update_deploy_wiki_pages(space_uuid, page_uuid, uuid, from_version=0):
    """更新wiki页面-发布"""
    return generate_param({
        "uuid": uuid,
        "from_version": from_version,
        "page_uuid": page_uuid,
        "space_uuid": space_uuid,
        "status": 2,
        "title": "title" + mocks.num(),
        "content": "<p>content-content</p>\n",
        "is_published": True
    })


def wiki_param():
    """空请求"""
    return generate_param({})


def add_template_space():
    """新建Wiki页面 组模版"""
    return generate_param({
        "title": "template_title" + mocks.num(),
        "content": "<p>content--content</p>\n" + mocks.name()
    })


def add_collaborate_wiki_global_template():
    """新建协同Wiki页面 组模版"""
    return generate_param({
        "title": "collaborate_wiki_template_title" + mocks.num(),
        "copy_src_type": ""
    })


def add_joint_template_space(space_uuid):
    """新建Wiki协同页面 组模版"""
    return generate_param({
        "title": "协同页面template_title" + mocks.num(),
        "space_uuid": space_uuid,
        "copy_src_type": ""
    })


def update_space_info(title, description, is_open_share_page,
                      space_category_uuid):
    """更新页面组信息"""
    return generate_param({
        "title": title,
        "description": description,
        "is_open_share_page": is_open_share_page,
        "space_category_uuid": space_category_uuid
    })


def space_type():
    """获取页面组分类信息"""
    return generate_param({
        "query": "{\n  spaceCategories(orderBy: {isDefault: ASC, position: ASC}){\n        uuid\n        name\n        path\n        position\n        spaceCount\n        parent{\n            uuid\n            name\n        }\n        isDefault\n    }\n} ",
        "variables": {}
    })


def add_global_template(template_id):
    """添加到全局模版"""
    return generate_param({
        "copy_src_type": "",
        "copy_src_uuid": template_id,
        "title": "global_template" + mocks.num(),
        "templateId": template_id
    })


def pages_restore():
    """回收站 放回原处"""

    return generate_param({
        "new_space_uuid": "",
        "new_parent_uuid": ""
    })


def copy_pages(copy_src_uuid, page_uuid):
    """复制页面"""
    return generate_param({
        "copy_src_type": "page",
        "copy_src_uuid": copy_src_uuid,
        "page_uuid": page_uuid,
        "status": 1
    })


def move_wiki_page(space_uuid, parent_uuid):
    """移动页面"""
    return generate_param({
        "space_uuid": space_uuid,
        "parent_uuid": parent_uuid,
        "version": 0
    })


def page_add_template(copy_src_uuid):
    """将页面添加为页面组模版"""
    return generate_param({
        "copy_src_type": "page",
        "copy_src_uuid": copy_src_uuid,
        "title": "title" + mocks.num()
    })
