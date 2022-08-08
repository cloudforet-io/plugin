from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel

__all__ = ['Supervisor']


class Supervisor(MongoModel):
    supervisor_id = StringField(max_length=40, generate_id='supervisor', unique=True)
    name = StringField(max_length=255)
    hostname = StringField()
    state = StringField(max_length=40, default='ENABLED', choices=('ENABLED', 'DISABLED', 'PENDING'))
    is_public = BooleanField(default=False)
    labels = DictField()
    tags = DictField()
    domain_id = StringField(max_length=64)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(default=None, null=True)

    meta = {
        'updatable_fields': [
            'name',
            'state',
            'updated_at',
            'plugins',
            'is_public',
            'hostname',
            'labels',
            'tags'
        ],
        'minimal_fields': [
            'supervisor_id',
            'name',
            'state',
            'is_public',
            'labels'
        ],
        'ordering': ['name'],
        'indexes': [
            # 'supervisor_id',
            'name',
            'hostname',
            'domain_id',
            'state',
            'is_public',
            'labels',
        ]
    }
