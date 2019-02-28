from pymodm import CharField, ReferenceField, ListField,\
    IntegerField, BooleanField, DateTimeField, ObjectIdField, FloatField
from pymodm.connection import connect
from pymodm import MongoModel
from pymodm import fields
from app import app

connect(app.config['MONGODB_URL'])


class RESOURCE(MongoModel):
    resource = CharField()
    delete = BooleanField()

    class Meta:
        collection_name = 'resource'
        final = True


class TENANT(MongoModel):
    name = CharField()
    logo = CharField()
    remark = CharField()
    resources = fields.ListField(ReferenceField(RESOURCE, blank=True), blank=True)
    delete = BooleanField()
    activated = BooleanField()
    createdAt = DateTimeField()
    updatedAt = DateTimeField()

    class Meta:
        collection_name = 'tenant'
        final = True
