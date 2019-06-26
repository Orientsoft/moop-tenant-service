from pymodm import CharField, ListField, BooleanField, DateTimeField, ObjectIdField, ReferenceField, IntegerField
from pymodm.connection import connect
from pymodm import MongoModel
from app import app

connect(app.config['MONGODB_URL'])


class TENANT(MongoModel):
    name = CharField()
    logo = ObjectIdField(blank=True)
    remark = CharField(blank=True)
    resources = ListField(blank=True)
    delete = BooleanField()
    activated = BooleanField()
    namespace = CharField()
    limit = IntegerField(blank=True)
    createdAt = DateTimeField()
    updatedAt = DateTimeField()

    class Meta:
        collection_name = 'tenant'
        final = True


class CUSTOM(MongoModel):
    tenant = ReferenceField(TENANT)
    name = CharField(blank=True)
    logo = ListField(blank=True)
    background = ObjectIdField(blank=True)
    remark = CharField(blank=True)
    description = CharField(blank=True)
    characteristic = ListField(blank=True)
    introduction = ListField(blank=True)
    tags = ListField(blank=True)
    email = CharField(blank=True)
    mobile = CharField(blank=True)
    url = CharField(blank=True)
    address = CharField(blank=True)
    teacher = CharField(blank=True)
    createdAt = DateTimeField()
    updatedAt = DateTimeField()
    delete = BooleanField()

    class Meta:
        collection_name = 'custom'
        final = True
