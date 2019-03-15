from flask import Blueprint, jsonify, request
from bson import ObjectId
from auth import filter, raise_status
from model import TENANT
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
        model_list = list(TENANT.objects.raw({'_id': {'$in': ObjectId_list}}))
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
    needed = ['name', 'remark', 'activated']
    query_list = ['name', 'logo', 'remark', 'resources', 'activated']
    requestObj = filter(query_list=query_list, updateObj=requestObj)
    for i in needed:
        if i not in requestObj.keys():
            return raise_status(400, '信息有缺失')
    try:
        TENANT.objects.get({'name': requestObj['name']})
        return raise_status(400, '租户名已存在')
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
            return raise_status(400, '租户创建失败')


@tenants.route('/tenants/<tenant_id>', methods=['GET'])
def tenant_get_by_id(tenant_id):
    from application.tenant_app import tenant_app
    try:
        TENANT.objects.get({'_id': ObjectId(tenant_id)})
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
        TENANT.objects.get({'_id': ObjectId(tenant_id)})
    except TENANT.DoesNotExist:
        return raise_status(400, '无效的租户id')
    requestObj = {'_id': tenant_id}
    updateObj = request.get_json()
    fields = request.args.get('fields')
    query_list = ['name', 'logo', 'remark', 'resources', 'activated']
    needed = ['name', 'remark', 'activated']
    for i in needed:
        if i not in updateObj.keys():
            return raise_status(400, '信息有缺失')
    requestObj = filter(query_list=query_list, updateObj=requestObj)
    tenant_app(requestObj=requestObj, updateObj=updateObj).tenant_update_set()
    tenant = tenant_app(requestObj=requestObj, collection='tenant').tenant_find_one()
    re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
    return jsonify(re)


@tenants.route('/tenants/<tenant_id>', methods=['PATCH'])
def tenant_update_partly(tenant_id):
    from application.tenant_app import tenant_app
    try:
        TENANT.objects.get({'_id': ObjectId(tenant_id)})
    except TENANT.DoesNotExist:
        return raise_status(400, '无效的租户id')
    requestObj = {'_id': tenant_id}
    updateObj = request.get_json()
    fields = request.args.get('fields')
    query_list = ['name', 'logo', 'remark', 'resources', 'activated']
    requestObj = filter(query_list=query_list, updateObj=requestObj)
    tenant_app(requestObj=requestObj, updateObj=updateObj).tenant_update_set()
    tenant = tenant_app(requestObj=requestObj, collection='tenant').tenant_find_one()
    re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
    return jsonify(re)


@tenants.route('/tenants/<tenant_id>', methods=['DELETE'])
def tenant_delete(tenant_id):
    from application.tenant_app import tenant_app
    try:
        TENANT.objects.get({'_id': ObjectId(tenant_id)})
    except TENANT.DoesNotExist:
        raise_status(400, '无效的租户id')
    requestObj = {'_id': tenant_id}
    tenant_app(requestObj=requestObj).tenant_delete()
    return raise_status(200)
