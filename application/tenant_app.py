from model import TENANT
from bson import ObjectId
import logging
import traceback


class tenant_app():
    def __init__(self, requestObj=None, collection=None, updateObj=None, fields=None):
        # requestObj is used for locating the
        self.collection = collection
        self.updateObj = updateObj
        self.query_fields = ['name']
        if requestObj:
            self.requestObj = requestObj
            self.requestObj['delete'] = False
        else:
            self.requestObj = {'delete': False}
        if fields:
            fields = fields.replace('[', '').replace(']', '').replace(' ', '').split(',')
        self.fields = fields

    def tenant_insert(self):
        from datetime import datetime
        try:
            self.type_convert()
            tenant = TENANT(
                name=self.requestObj['name'],
                logo=ObjectId(self.requestObj['logo']) if self.requestObj['logo'] and (
                            self.requestObj['logo'] != '') else None,
                remark=self.requestObj['remark'],
                resources=self.requestObj['resources'],
                limit=self.requestObj.get('limit'),
                delete=False,
                activated=self.requestObj['activated'],
                namespace=self.requestObj['namespace'],
                createdAt=datetime.now(),
                updatedAt=datetime.now()
            ).save()
        except Exception as e:
            logging.error('Request Error: {}\nStack: {}\n'.format(e, traceback.format_exc()))
            return True
        return tenant

    def tenant_find_one(self):
        try:
            self.type_convert()
            tenant = TENANT.objects.get(self.requestObj)
        except TENANT.DoesNotExist:
            return 'DoesNotExist'
        except Exception as e:
            logging.error('Request Error: {}\nStack: {}\n'.format(e, traceback.format_exc()))
            return e
        return tenant

    def tenant_find_all(self):
        try:
            self.type_convert()
            tenant = list(TENANT.objects.raw(self.requestObj))
        except TENANT.DoesNotExist:
            return 'DoesNotExist'
        except Exception as e:
            logging.error('Request Error: {}\nStack: {}\n'.format(e, traceback.format_exc()))
            return e
        return tenant

    def tenant_update_set(self):
        from datetime import datetime
        try:
            self.type_convert()
            self.updateObj['updatedAt'] = datetime.now()
            if self.updateObj.get('logo'):
                self.updateObj['logo'] = ObjectId(self.updateObj['logo'])
            TENANT.objects.raw(self.requestObj).update({'$set': self.updateObj})
        except Exception as e:
            logging.error('Request Error: {}\nStack: {}\n'.format(e, traceback.format_exc()))
            return e

    def tenant_delete(self):
        try:
            self.type_convert()
            # when tenant is deleted, it`s 'delete' is True, and it can never be queried normally
            TENANT.objects.raw(self.requestObj).update({'$set': {'delete': True}})
        except TENANT.DoesNotExist:
            return 'DoesNotExist'
        except Exception as e:
            logging.error('Request Error: {}\nStack: {}\n'.format(e, traceback.format_exc()))
            return e

    def str_to_list(self):
        fields = self.fields.replace('[', '')
        fields = fields.replace(']', '')
        fields = fields.replace(' ', '')
        result = fields.split(',')
        return result

    def get_return_by_fields(self, tenant: TENANT):
        # ensure that object is complete
        if tenant.logo == None:
            logo = None
        else:
            logo = str(tenant.logo)
        # resources = [] if tenant.resources == [] else [r.resource for r in tenant.resources]
        re = {
            "id": str(tenant._id),
            "name": tenant.name,
            "logo": logo,
            "remark": tenant.remark,
            'limit': tenant.limit,
            "resources": tenant.resources,
            "namespace": tenant.namespace,
            "activated": tenant.activated,
            "createdAt": tenant.createdAt,
            "updatedAt": tenant.updatedAt
        }
        # select by fields
        fields = self.fields
        if fields:
            keys = list(re.keys())
            for item in keys:
                if item not in fields:
                    re.pop(item)
        return re

    def type_convert(self):
        # ListField preprocess
        if hasattr(self, 'list_fields'):
            for item in self.list_fields:
                if item in self.requestObj.keys():
                    a = self.requestObj[item]
                    if self.requestObj[item] is not None and self.requestObj[item] is not []:
                        self.requestObj[item] = list(map(ObjectId, self.requestObj[item]))
        # _id
        if '_id' in self.requestObj.keys():
            self.requestObj['_id'] = ObjectId(self.requestObj['_id'])

    def tenant_count(self):
        try:
            count = TENANT.objects.raw(self.requestObj).count()
            return count
        except Exception as e:
            logging.error('Request Error: {}\nStack: {}\n'.format(e, traceback.format_exc()))
            raise


def unfold_tenant(Model):
    return {
        'id': str(Model._id),
        'name': Model.name,
        'logo': str(Model.logo) if Model.logo else None,
        'remark': Model.remark,
        'resources': Model.resources,
        'activated': Model.activated,
        'namespace': Model.namespace,
        'updatedAt': Model.updatedAt,
        'createdAt': Model.createdAt
    }


def unfold_custom(Model, embed=None):
    if Model.introduction:
        introduction = Model.introduction
        for x in introduction:
            if 'thumb' in x and x['thumb']:
                x['thumb'] = str(x['thumb'])
    else:
        introduction = None
    return {
        'id': str(Model._id),
        'name': Model.name,
        'logo': [str(x) if x else None for x in Model.logo] if Model.logo else None,
        'background': str(Model.background) if Model.background else None,
        'remark': Model.remark,
        'description': Model.description,
        'introduction': introduction,
        'characteristic': Model.characteristic,
        'tags': Model.tags,
        'email': Model.email,
        'mobile': Model.mobile,
        'url': Model.url,
        'address': Model.address,
        'teacher': Model.teacher,
        'tenant': str(Model.tenant._id) if not embed else unfold_tenant(Model.tenant),
        'createdAt': Model.createdAt,
        'updatedAt': Model.updatedAt
    }
