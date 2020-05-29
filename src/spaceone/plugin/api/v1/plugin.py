# -*- coding: utf-8 -*-

from spaceone.api.plugin.v1 import plugin_pb2, plugin_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Plugin(BaseAPI, plugin_pb2_grpc.PluginServicer):

    pb2 = plugin_pb2
    pb2_grpc = plugin_pb2_grpc

    def get_plugin_endpoint(self, request, context):
        """Get Plugin Endpoint.

        Returns:
            PluginEndpoint

        Raises:
            ERROR_NOT_FOUND:
        """
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            data = plugin_svc.get_plugin_endpoint(params)
            return self.locator.get_info('PluginEndpoint', data)

    def notify_failure(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PluginService', metadata) as plugin_svc:
            plugin_svc.notify_failure(params)
            return self.locator.get_info('EmptyInfo')
