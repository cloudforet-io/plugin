# -*- coding: utf-8 -*-
import datetime

from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
from spaceone.plugin.model.supervisor_model import Supervisor
from spaceone.plugin.manager.plugin_manager.plugin_state import PROVISIONING, ACTIVE, ERROR, RE_PROVISIONING

__all__ = ['InstalledPlugin']


class InstalledPlugin(MongoModel):
    # TODO: check plugin_id max length
    plugin_id = StringField(max_length=255, required=True, null=False)
    supervisor_id = StringField(max_length=255, required=True, null=False)
    supervisor = ReferenceField('Supervisor', reverse_delete_rule=CASCADE,  required=True, null=False)
    domain_id = StringField(max_length=40, required=True, null=False)

    name = StringField(max_length=255)
    image = StringField(max_length=255)
    version = StringField(max_length=255)
    state = StringField(max_length=40,
                        default=PROVISIONING,
                        choices=(PROVISIONING, ACTIVE, ERROR, RE_PROVISIONING))
    endpoint = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now_add=True)

    meta = {
        'db_alias': 'default',
        'updatable_fields': [
            'name',
            'updated_at',
            'state',
            'endpoint'
        ],
        'exact_fields': [
            'domain_id',
            'plugin_id',
            'state',
            'endpoint'
        ],
        'minimal_fields': [
            'plugin_id',
            'name',
            'state'
        ],
        'change_query_keys': {
            'hostname': 'supervisor.hostname'
        },
        'reference_query_keys': {
            'supervisor': Supervisor
        },
        'ordering': ['name'],
        'indexes': [
            'plugin_id'
        ]
    }

    def update(self, data):
        data['updated_at'] = datetime.datetime.now()
        return super().update(data)
