# -*- coding: utf-8 -*-

__all__ = ["RepositoryConnector"]

import logging

from google.protobuf.json_format import MessageToDict

from spaceone.core import pygrpc
from spaceone.core.connector import BaseConnector
from spaceone.core.error import *
from spaceone.core.utils import parse_endpoint

_LOGGER = logging.getLogger(__name__)


class RepositoryConnector(BaseConnector):
    def __init__(self, transaction, config):
        super().__init__(transaction, config)
        _LOGGER.debug("[__init__] config: %s" % self.config)
        if 'endpoint' not in self.config:
            raise ERROR_WRONG_CONFIGURATION(key='endpoint')

        if len(self.config['endpoint']) > 1:
            raise ERROR_WRONG_CONFIGURATION(key='too many endpoint')

        for (k, v) in self.config['endpoint'].items():
            # parse endpoint
            e = parse_endpoint(v)
            self.protocol = e['scheme']
            if self.protocol == 'grpc':
                # create grpc client
                self.client = pygrpc.client(endpoint="%s:%s" % (e['hostname'], e['port']), version=k)
            elif self.protocol == 'http':
                # TODO:
                pass

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

