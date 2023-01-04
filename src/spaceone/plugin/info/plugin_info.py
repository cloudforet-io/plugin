import functools

from spaceone.api.plugin.v1 import plugin_pb2
from spaceone.api.plugin.v1 import supervisor_pb2
from spaceone.plugin.model.installed_plugin_ref_model import InstalledPluginRef
from spaceone.core.pygrpc.message_type import *

__all__ = ['PluginInfo', 'PluginsInfo', 'PluginEndpoint']


def PluginInfo(plugin_vo: InstalledPluginRef, minimal=False):
    if isinstance(plugin_vo, InstalledPluginRef):
        info = {
            'plugin_id': plugin_vo.plugin_id,
            'version': plugin_vo.version,
            'state': plugin_vo.plugin_owner.state,
            'endpoint': plugin_vo.plugin_owner.endpoint,
            'endpoints': change_list_value_type(plugin_vo.plugin_owner.endpoints)
        }
        if not minimal:
            info.update({
                'supervisor_id': plugin_vo.supervisor.supervisor_id,
                'supervisor_name': plugin_vo.supervisor.name,
                'managed': plugin_vo.managed,
                'domain_id': plugin_vo.plugin_domain_id if plugin_vo.plugin_domain_id else plugin_vo.domain_id
            })
    else:
        # InstalledPlugin
        info = {
            'plugin_id': plugin_vo.plugin_id,
            'version': plugin_vo.version,
            'state': plugin_vo.state,
            'supervisor_id': plugin_vo.supervisor_id,
            'managed': True,
            'domain_id': plugin_vo.domain_id

        }
    return supervisor_pb2.PluginInfo(**info)


def PluginsInfo(plugin_vo: InstalledPluginRef, total_count):
    results = list(map(functools.partial(PluginInfo), plugin_vo))

    return supervisor_pb2.PluginsInfo(results=results, total_count=total_count)


def PluginEndpoint(endpoint):
    return plugin_pb2.PluginEndpoint(**endpoint)
