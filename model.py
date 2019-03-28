from pymodm import CharField, ListField, BooleanField, DateTimeField, ObjectIdField
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
    createdAt = DateTimeField()
    updatedAt = DateTimeField()

    class Meta:
        collection_name = 'tenant'
        final = True
