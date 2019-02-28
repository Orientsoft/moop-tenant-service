from model import TENANT
from bson import ObjectId


class tenant_app():
    def __init__(self, requestObj=None, collection=None, updateObj=None, fields=None):
        # requestObj is used for locating the
        self.collection = collection
        self.updateObj = updateObj
        self.query_fields = ['name', 'activated']
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
                logo=ObjectId(self.requestObj['logo']),
                remark=self.requestObj['remark'],
                resources=self.requestObj['resources'],
                delete=False,
                activated=self.requestObj['activated'],
                createdAt=datetime.now(),
                updatedAt=datetime.now()
            ).save()
        except Exception as e:
            print('tenant_insert error:', e)
            return True
        return tenant

    def tenant_find_one(self):
        try:
            self.type_convert()
            tenant = TENANT.objects.get(self.requestObj)
        except TENANT.DoesNotExist as e:
            print("tenant_get doesn't exist")
            return 'DoesNotExist'
        except Exception as e:
            print('tenant_get error:', e)
            return e
        return tenant

    def tenant_find_all(self):
        try:
            self.type_convert()
            tenant = list(TENANT.objects.raw(self.requestObj))
        except TENANT.DoesNotExist:
            print("tenant_get doesn't exist")
            return 'DoesNotExist'
        except Exception as e:
            print('tenant_find_all error:', e)
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
            print('tenant_update_set error:', e)
            return e

    def tenant_delete(self):
        try:
            self.type_convert()
            # when tenant is deleted, it`s 'delete' is True, and it can never be queried normally
            TENANT.objects.raw(self.requestObj).update({'$set': {'delete': True}})
        except TENANT.DoesNotExist as e:
            print("tenant doesn't exist", e)
            return 'DoesNotExist'
        except Exception as e:
            print("tenant_delete error:", e)
            return e

    def str_to_list(self):
        fields = self.fields.replace('[', '')
        fields = fields.replace(']', '')
        fields = fields.replace(' ', '')
        result = fields.split(',')
        return result

    def get_return_by_fields(self, tenant: TENANT)-> dict:
        # ensure that object is complete
        if tenant.logo == None:
            logo = None
        else:
            logo = str(tenant.logo)
        resources = [] if tenant.resources == [] else [r.resource for r in tenant.resources]
        re = {
            "id": str(tenant._id),
            "name": tenant.name,
            "logo": logo,
            "remark": tenant.remark,
            "resources": resources,
            "activated": tenant.activated,
            # "custom_pictures": tenant,
            # "description": tenant.description,
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
        if hasattr(self, 'query_fields'):
            if 'activated' in self.requestObj.keys():
                value = self.requestObj['activated']
                if value == 'true' or value == 'True':
                    self.requestObj['activated'] = True
                else:
                    self.requestObj['activated'] = False

    def tenant_count(self):
        try:
            count = TENANT.objects.raw(self.requestObj).count()
            return count
        except Exception as e:
            print('tenant_count error:', e)
            raise
