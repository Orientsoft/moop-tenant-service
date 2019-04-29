from pymodm import CharField, ListField, BooleanField, DateTimeField, ObjectIdField, DictField
from pymodm.connection import connect
from pymodm import MongoModel
from app import app

connect(app.config['MONGODB_URL'])


class TENANT(MongoModel):
    name = CharField()
    logo = ObjectIdField()
    remark = CharField()
    resources = ListField(blank=True)
    delete = BooleanField()
    activated = BooleanField()
    namespace = CharField()
    createdAt = DateTimeField()
    updatedAt = DateTimeField()

    class Meta:
        collection_name = 'tenant'
        final = True


class CUSTOM(MongoModel):
    tenant = ReferenceError(TENANT)
    name = CharField()
    logo = ListField()
    background = CharField()
    remark = CharField()
    description = CharField()
    characteristic = ListField()
    introduction = ListField()
    tags = ListField()
    connect = DictField()
    createdAt = DateTimeField()
    updatedAt = DateTimeField()
    delete = BooleanField()

    class Meta:
        collection_name = 'custom'
        final = True
