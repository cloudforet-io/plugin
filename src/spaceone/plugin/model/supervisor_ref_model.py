from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
from spaceone.plugin.model.supervisor_model import Supervisor

__all__ = ['SupervisorRef']


class SupervisorRef(MongoModel):
    supervisor_id = StringField(max_length=40)
    supervisor = ReferenceField('Supervisor', required=True, null=False)
    domain_id = StringField(max_length=64)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'updated_at'
        ],
        'minimal_fields': [
            'supervisor_id',
            'supervisors'
        ],
        'ordering': ['domain_id'],
        'indexes': [
            'supervisor_id',
            'domain_id'
        ]
    }
