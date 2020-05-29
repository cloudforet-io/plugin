# -*- coding: utf-8 -*-

__all__ = ['InstalledPluginRef']

from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
#from spaceone.plugin.model.supervisor_ref_model import SupervisorRef
from spaceone.plugin.model.supervisor_model import Supervisor
from spaceone.plugin.model.installed_plugin_model import InstalledPlugin

class InstalledPluginRef(MongoModel):
    supervisor_id = StringField(max_length=255, required=True)
    domain_id = StringField(max_length=255, required=True)
    plugin_id = StringField(max_length=255, required=True)
    version = StringField(max_length=255, required=True)
    supervisor = ReferenceField('Supervisor', required=True)
    plugin_owner = ReferenceField('InstalledPlugin', required=True)
    managed = BooleanField()

    meta = {
        'db_alias': 'default',
        'updatable_fields': [
            'managed'
        ],
        'exact_fields': [
            'domain_id',
            'plugin_id',
            'version'
        ],
        'minimal_fields': [
            'domain_id'
            'plugin_id',
            'version'
        ],
        'change_query_keys': {
            'hostname': 'supervisor.hostname',
            'endpoint': 'plugin_owner.endpoint',
            'labels': 'supervisor.labels',
            'state': 'plugin_owner.state'
        },
        'reference_query_keys': {
            'supervisor': Supervisor,
            'plugin_owner': InstalledPlugin
        },
        'ordering': ['plugin_id'],
        'indexes': [
            'plugin_id'
        ]
    }

