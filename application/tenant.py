from flask import Blueprint, jsonify, request
from bson import ObjectId
from auth import filter, raise_status
from model import TENANT, CUSTOM
from datetime import datetime
import logging
import traceback

tenants = Blueprint('tenants', __name__)


@tenants.route('/tenants', methods=['GET'])
def tenant_list():
    from application.tenant_app import tenant_app
    from auth import raise_status
    from model import TENANT
    requestObj = {}
    page = int(request.args.get('page', '1'))
    pageSize = int(request.args.get('pageSize', '20'))
    if request.args.get('id'):
        id_list = request.args['id'].replace('[', '').replace(']', '').replace(' ', ''). \
            replace("'", '').replace('"', '').split(',')
        ObjectId_list = []
        for i in id_list:
            ObjectId_list.append(ObjectId(i))
        model_list = list(TENANT.objects.raw({'_id': {'$in': ObjectId_list}, 'delete': False}))
        tenant_dict = {}
        for tenant_model in model_list:
            if tenant_model.logo == None:
                logo = None
            else:
                logo = str(tenant_model.logo)
            tenant_dict[str(tenant_model._id)] = {
                'id': str(tenant_model._id),
                'name': tenant_model.name,
                'logo': logo,
                'remark': tenant_model.remark,
                'limit': tenant_model.limit,
                'namespace': tenant_model.namespace,
                'resources': tenant_model.resources,
                "activated": tenant_model.activated,
                "createdAt": tenant_model.createdAt,
                "updatedAt": tenant_model.updatedAt
            }
        return jsonify(tenant_dict)
    if request.args.get('all'):
        page = pageSize = None
    else:
        try:
            count = tenant_app().tenant_count()
        except Exception:
            return raise_status(500, 'SystemError')
        if count % pageSize == 0:
            totalpage = count // pageSize
        else:
            totalpage = (count // pageSize) + 1
        if page > totalpage:
            return raise_status(400, '页数超出范围')
    if request.args.get('fields'):
        queries = list(request.args.keys())
        for query in queries:
            requestObj[query] = request.args.get(query)
        fields = requestObj.pop('fields')
    else:
        fields = {}
    tenants_list = tenant_app(requestObj=requestObj, collection='tenant').tenant_find_all()
    tenant_ln_list = []
    for tenant in tenants_list:
        re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
        tenant_ln_list.append(re)
    returnObj = {}
    returnObj['tenant'] = tenant_ln_list
    if not request.args.get('all'):
        returnObj['meta'] = {'page': page, 'pageSize': pageSize, 'total': count, 'totalPage': totalpage}
    return jsonify(returnObj)


@tenants.route('/tenants', methods=['POST'])
def tenant_create():
    from application.tenant_app import tenant_app
    requestObj = request.get_json()
    fields = request.args.get('fields')
    needed = ['name', 'remark', 'activated', 'namespace']
    query_list = ['name', 'logo', 'remark', 'resources', 'activated', 'namespace', 'limit']
    requestObj = filter(query_list=query_list, updateObj=requestObj)
    for i in needed:
        if i not in requestObj.keys():
            return '信息有缺失', 400
    try:
        TENANT.objects.get({'name': requestObj['name'], 'delete': False})
        return '租户名已存在', 400
    except TENANT.DoesNotExist:
        if not requestObj.get('resources'):
            requestObj['resources'] = {}
        if 'logo' not in requestObj.keys():
            requestObj['logo'] = None
        try:
            tenant = tenant_app(requestObj=requestObj).tenant_insert()
            re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)

            return jsonify(re)
        except Exception as e:
            logging.error('Request Error: {}\nStack: {}\n'.format(e, traceback.format_exc()))
            return '租户创建失败', 400


@tenants.route('/tenants/<tenant_id>', methods=['GET'])
def tenant_get_by_id(tenant_id):
    from application.tenant_app import tenant_app
    try:
        TENANT.objects.get({'_id': ObjectId(tenant_id), 'delete': False})
    except TENANT.DoesNotExist:
        return raise_status(400, '无效的租户id')
    requestObj = {'_id': tenant_id}
    fields = request.args.get('fields')
    tenant = tenant_app(requestObj=requestObj, collection='tenant').tenant_find_one()
    if tenant == 'DoesNotExist':
        return raise_status(400, '错误的id')
    re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
    return jsonify(re)


@tenants.route('/tenants/<tenant_id>', methods=['PUT'])
def tenant_update_totally(tenant_id):
    from application.tenant_app import tenant_app
    try:
        TENANT.objects.get({'_id': ObjectId(tenant_id), 'delete': False})
    except TENANT.DoesNotExist:
        return raise_status(400, '无效的租户id')
    requestObj = {'_id': tenant_id}
    updateObj = request.get_json()
    fields = request.args.get('fields')
    query_list = ['name', 'logo', 'remark', 'resources', 'activated', 'namespace']
    needed = ['name', 'remark', 'activated', 'namespace', 'resources', 'logo']
    for i in needed:
        if i not in updateObj.keys():
            return raise_status(400, '信息有缺失')
    updateObj = filter(query_list=query_list, updateObj=updateObj)
    tenant_app(requestObj=requestObj, updateObj=updateObj).tenant_update_set()
    tenant = tenant_app(requestObj=requestObj, collection='tenant').tenant_find_one()
    re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
    return jsonify(re)


@tenants.route('/tenants/<tenant_id>', methods=['PATCH'])
def tenant_update_partly(tenant_id):
    from application.tenant_app import tenant_app
    try:
        TENANT.objects.get({'_id': ObjectId(tenant_id), 'delete': False})
    except TENANT.DoesNotExist:
        return raise_status(400, '无效的租户id')
    requestObj = {'_id': tenant_id}
    updateObj = request.get_json()
    fields = request.args.get('fields')
    query_list = ['name', 'logo', 'remark', 'resources', 'activated', 'namespace']
    updateObj = filter(query_list=query_list, updateObj=updateObj)
    tenant_app(requestObj=requestObj, updateObj=updateObj).tenant_update_set()
    tenant = tenant_app(requestObj=requestObj, collection='tenant').tenant_find_one()
    re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
    return jsonify(re)


@tenants.route('/tenants/<tenant_id>', methods=['DELETE'])
def tenant_delete(tenant_id):
    from application.tenant_app import tenant_app
    try:
        TENANT.objects.get({'_id': ObjectId(tenant_id), 'delete': False})
    except TENANT.DoesNotExist:
        return '无效的租户id', 400
    requestObj = {'_id': tenant_id}
    tenant_app(requestObj=requestObj).tenant_delete()
    return '操作成功', 200


@tenants.route('/tenants/<tenant_id>/custom', methods=['POST'])
def tenant_custom_create(tenant_id):
    from application.tenant_app import unfold_custom
    try:
        TENANT.objects.get({'_id': ObjectId(tenant_id), 'delete': False})
    except TENANT.DoesNotExist:
        return '无效的租户', 400
    query_list = ['name', 'logo', 'background', 'description', 'characteristic', 'introduction', 'remark', 'tags',
                  'email', 'url', 'mobile', 'address', 'teacher', 'about', 'license', 'companys', 'features']
    insertObj = filter(query_list=query_list, updateObj=request.json)
    try:
        check = CUSTOM.objects.get({'tenant': ObjectId(tenant_id), 'delete': False})
        # 若该租户已有定制数据，则替换为新的定制数据，因此数据库中一个租户应该只有一套定制数据
        insertObj['updatedAt'] = datetime.now()
        CUSTOM.objects.raw({'_id': check._id, 'delete': False}).update({'$set': insertObj})
        Model = CUSTOM.objects.get({'_id': check._id, 'delete': False})
    except CUSTOM.DoesNotExist:
        Model = CUSTOM(
            name=insertObj.get('name'),
            logo=insertObj.get('logo'),
            background=insertObj.get('background'),
            description=insertObj.get('description'),
            characteristic=insertObj.get('characteristic'),
            introduction=insertObj.get('introduction'),
            remark=insertObj.get('remark'),
            tags=insertObj.get('tags'),
            email=insertObj.get('email'),
            about=insertObj.get('about'),
            license=insertObj.get('license'),
            companys=insertObj.get('companys'),
            features=insertObj.get('features'),
            mobile=insertObj.get('mobile'),
            url=insertObj.get('url'),
            address=insertObj.get('address'),
            teacher=insertObj.get('teacher'),
            tenant=ObjectId(tenant_id),
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            delete=False
        ).save()
    custom = unfold_custom(Model=Model, embed=request.args.get('embed'))
    return jsonify(custom)


@tenants.route('/tenants/<tenant_id>/custom', methods=['GET'])
def tenant_custom_get(tenant_id):
    from application.tenant_app import unfold_custom
    try:
        Model = CUSTOM.objects.get({'tenant': ObjectId(tenant_id), 'delete': False})
    except CUSTOM.DoesNotExist:
        # 若数据库中没有该租户定制信息，则自动创建
        try:
            TENANT.objects.get({'_id': ObjectId(tenant_id), 'delete': False})
        except TENANT.DoesNotExist:
            return '租户已删除', 400
        Model = CUSTOM(
            name=None,
            logo=None,
            background=None,
            description=None,
            characteristic=None,
            introduction=None,
            remark=None,
            tags=None,
            email=None,
            mobile=None,
            url=None,
            address=None,
            teacher=None,
            tenant=ObjectId(tenant_id),
            about=None,
            license=None,
            companys=None,
            features=None,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            delete=False
        ).save()
    custom = unfold_custom(Model=Model, embed=request.args.get('embed'))
    return jsonify(custom)


@tenants.route('/tenants/<tenant_id>/custom', methods=['PATCH'])
def tenant_custom_change(tenant_id):
    from application.tenant_app import unfold_custom
    try:
        CUSTOM.objects.get({'tenant': ObjectId(tenant_id), 'delete': False})
    except CUSTOM.DoesNotExist:
        return '请先创建定制数据', 400
    query_list = ['name', 'logo', 'background', 'description', 'characteristic', 'introduction', 'remark', 'tags',
                  'email', 'url', 'mobile', 'address', 'teacher', 'about', 'license', 'companys', 'features']
    updateObj = filter(query_list=query_list, updateObj=request.json)
    updateObj['updatedAt'] = datetime.now()
    # 处理ObjectId转字符串问题
    if 'logo' in updateObj:
        updateObj['logo'] = [ObjectId(x) for x in updateObj['logo']]
    if 'background' in updateObj:
        updateObj['background'] = ObjectId(updateObj['background'])
    if 'introduction' in updateObj:
        for x in updateObj['introduction']:
            if 'thumb' in x:
                x['thumb'] = ObjectId(x['thumb'])
            else:
                x['thumb'] = None
    CUSTOM.objects.raw({'tenant': ObjectId(tenant_id), 'delete': False}).update({'$set': updateObj})
    Model = CUSTOM.objects.get({'tenant': ObjectId(tenant_id), 'delete': False})
    custom = unfold_custom(Model=Model, embed=request.args.get('embed'))
    return jsonify(custom)


@tenants.route('/tenants/<tenant_id>/custom', methods=['DELETE'])
def tenant_custom_delete(tenant_id):
    try:
        CUSTOM.objects.get({'tenant': ObjectId(tenant_id), 'delete': False})
    except CUSTOM.DoesNotExist:
        return '不存在定制数据', 400
    CUSTOM.objects.raw({'tenant': ObjectId(tenant_id), 'delete': False}).update({'$set': {'delete': True}})
