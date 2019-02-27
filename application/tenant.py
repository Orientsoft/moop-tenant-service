from flask import Blueprint, jsonify, request

tenants = Blueprint('tenants', __name__)


@tenants.route('/tenants', methods=['GET'])
def tenant_list():
    from application.tenant_app import tenant_app
    requestObj = {}
    if request.args:
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
    returnObj['data'] = tenant_ln_list
    return jsonify(returnObj)


@tenants.route('/tenants', methods=['POST'])
def tenant_create():
    from application.tenant_app import tenant_app
    from auth import raise_status
    requestObj = request.get_json()
    fields = request.args.get('fields')
    needed = ['name', 'remark', 'activated']
    for i in needed:
        if i not in requestObj.keys():
            return jsonify(raise_status(400, '信息有缺失'))
    list_supply = ['resources']
    for i in list_supply:
        if i not in requestObj.keys():
            requestObj[i] = []
    if 'logo' not in requestObj.keys():
        requestObj['logo'] = None
    try:
        tenant = tenant_app(requestObj=requestObj).tenant_insert()
        re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
        return jsonify(re)
    except Exception as e:
        print(e)
        return jsonify(raise_status(400, '租户创建失败'))


@tenants.route('/tenants/<tenant_id>', methods=['GET'])
def tenant_get_by_id(tenant_id):
    from application.tenant_app import tenant_app
    requestObj = {'_id': tenant_id}
    fields = request.args.get('fields')
    tenant = tenant_app(requestObj=requestObj, collection='tenant').tenant_find_one()
    re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
    return jsonify(re)


@tenants.route('/tenants/<tenant_id>', methods=['PUT'])
def tenant_update_totally(tenant_id):
    from application.tenant_app import tenant_app
    from auth import raise_status
    requestObj = {'_id': tenant_id}
    updateObj = request.get_json()
    fields = request.args.get('fields')
    # check if the json has all needed attrs in tenantInResponse
    needed = ['activated', 'name', 'logo', 'remark', 'resources']
    for i in needed:
        if i not in updateObj.keys():
            # todo: what to return, when it comes to error
            # return jsonify({"error": "need more attr"}), 400
            info = '数据不全'
            return raise_status(400, info)
    tenant_app(requestObj=requestObj, updateObj=updateObj).tenant_update_set()
    tenant = tenant_app(requestObj=requestObj, collection='tenant').tenant_find_one()
    re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
    return jsonify(re)


@tenants.route('/tenants/<tenant_id>', methods=['PATCH'])
def tenant_update_partly(tenant_id):
    from application.tenant_app import tenant_app
    requestObj = {'_id': tenant_id}
    updateObj = request.get_json()
    fields = request.args.get('fields')
    tenant_app(requestObj=requestObj, updateObj=updateObj).tenant_update_set()
    tenant = tenant_app(requestObj=requestObj, collection='tenant').tenant_find_one()
    re = tenant_app(fields=fields).get_return_by_fields(tenant=tenant)
    return jsonify(re)


@tenants.route('/tenants/<tenant_id>', methods=['DELETE'])
def tenant_delete(tenant_id):
    from application.tenant_app import tenant_app
    from auth import raise_status
    requestObj = {'_id': tenant_id}
    tenant_app(requestObj=requestObj).tenant_delete()
    return raise_status(200)
