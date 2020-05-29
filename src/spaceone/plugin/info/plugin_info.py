# -*- coding: utf-8 -*-
import functools

from spaceone.api.plugin.v1 import plugin_pb2
from spaceone.api.plugin.v1 import supervisor_pb2
from spaceone.plugin.model.installed_plugin_ref_model import InstalledPluginRef
from spaceone.core.pygrpc.message_type import *

__all__ = ['PluginInfo', 'PluginsInfo', 'PluginEndpoint']


def PluginInfo(plugin_vo: InstalledPluginRef, minimal=False):
    info = {
        'plugin_id': plugin_vo.plugin_id,
        'version': plugin_vo.version,
        'state': plugin_vo.plugin_owner.state,
        'endpoint': plugin_vo.plugin_owner.endpoint
    }
    if not minimal:
        info.update({
            'supervisor_id': plugin_vo.supervisor.supervisor_id,
            'supervisor_name': plugin_vo.supervisor.name,
            'managed': plugin_vo.managed
        })

    return supervisor_pb2.PluginInfo(**info)


def PluginsInfo(plugin_vo: InstalledPluginRef, total_count):
    results = list(map(functools.partial(PluginInfo), plugin_vo))

    return supervisor_pb2.PluginsInfo(results=results, total_count=total_count)


def PluginEndpoint(plugin_vo):
    info = {}
    info['endpoint'] = plugin_vo.plugin_owner.endpoint

    return plugin_pb2.PluginEndpoint(**info)
