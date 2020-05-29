# -*- coding: utf-8 -*-

__all__ = ['SupervisorRef']

from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
from spaceone.plugin.model.supervisor_model import Supervisor

class SupervisorRef(MongoModel):
    domain_id = StringField(max_length=64)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now_add=True)
    supervisor_id = StringField(max_length=40)
    supervisor = ReferenceField('Supervisor', required=True, null=False)

    meta = {
        'db_alias': 'default',
        'updatable_fields': [
            'updated_at'
        ],
        'exact_fields': [
            'supervisor_id',
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
