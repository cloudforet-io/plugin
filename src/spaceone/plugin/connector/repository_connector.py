import logging
from google.protobuf.json_format import MessageToDict

from spaceone.core import pygrpc
from spaceone.core.connector import BaseConnector
from spaceone.core.error import *
from spaceone.core.utils import parse_grpc_endpoint

__all__ = ["RepositoryConnector"]

_LOGGER = logging.getLogger(__name__)


class RepositoryConnector(BaseConnector):
    def __init__(self, transaction, config):
        super().__init__(transaction, config)

        if 'endpoint' not in self.config:
            raise ERROR_WRONG_CONFIGURATION(key='endpoint')

        for version, endpoint in self.config['endpoint'].items():
            e = parse_grpc_endpoint(endpoint)
            self.client = pygrpc.client(endpoint=e['endpoint'], ssl_enabled=e['ssl_enabled'])

    def get_plugin(self, plugin_id, domain_id):
        """ Call Plugin.get

        Returns: PluginInfo
        """
        _LOGGER.debug('[get_plugin] plugin_id:%s' % plugin_id)

        return self.client.Plugin.get({
            'plugin_id': plugin_id,
            'domain_id': domain_id
        }, metadata=self.transaction.get_connection_meta())

    def get_plugin_versions(self, plugin_id, domain_id):
        response = self.client.Plugin.get_versions({
            'plugin_id': plugin_id,
            'domain_id': domain_id
        }, metadata=self.transaction.get_connection_meta())

        data = self._change_message(response)
        return data['results']

    @staticmethod
    def _change_message(message):
        return MessageToDict(message, preserving_proto_field_name=True)

