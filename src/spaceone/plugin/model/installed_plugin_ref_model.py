from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel
#from spaceone.plugin.model.supervisor_ref_model import SupervisorRef
from spaceone.plugin.model.supervisor_model import Supervisor
from spaceone.plugin.model.installed_plugin_model import InstalledPlugin

__all__ = ['InstalledPluginRef']


class InstalledPluginRef(MongoModel):
    supervisor_id = StringField(max_length=255, required=True)
    plugin_id = StringField(max_length=255, required=True)
    version = StringField(max_length=255, required=True)
    supervisor = ReferenceField('Supervisor', required=True)
    plugin_owner = ReferenceField('InstalledPlugin', required=True)
    managed = BooleanField()
    domain_id = StringField(max_length=255, required=True)

    meta = {
        'updatable_fields': [
            'managed'
        ],
        'minimal_fields': [
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
            'plugin_id',
            'version',
            'supervisor',
            'plugin_owner',
            'supervisor_id',
            'domain_id'
        ]
    }

