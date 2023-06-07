"""
Deprecated
"""

import logging

from spaceone.core import pygrpc
from spaceone.core.error import *
from spaceone.core.connector import BaseConnector
from spaceone.core.utils import parse_endpoint

_LOGGER = logging.getLogger(__name__)


class PluginConnector(BaseConnector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.api_class = None

    def initialize(self, endpoint, api_class):
        if endpoint is None:
            raise ERROR_GRPC_CONFIGURATION

        self.api_class = api_class
        endpoint = endpoint.replace('"', '')
        e = parse_endpoint(endpoint)
        protocol = e['scheme']

        if protocol == 'grpc':
            self.client = pygrpc.client(endpoint="%s:%s" % (e['hostname'], e['port']), version='plugin')
        elif protocol == 'http':
            # TODO:
            pass

        if self.client is None:
            _LOGGER.error(f'[initialize] Cannot access gRPC server. '
                          f'(host: {e.get("hostname")}, port: {e.get("port")}, version: plugin)')
            raise ERROR_GRPC_CONFIGURATION

    def init(self, options, domain_id):
        params = {
            'options': options,
            'domain_id': domain_id
        }

        plugin_client = getattr(self.client, self.api_class)
        _LOGGER.debug(f'[init] api class: {self.api_class}')
        _LOGGER.debug(f'[init] plugin_client: {plugin_client}')
        return getattr(plugin_client, 'init')(params, domain_id)

    def verify(self, options, secret_data):
        params = {
            'options': options,
            'secret_data': secret_data
        }
        plugin_client = getattr(self.client, self.api_class)
        plugin_client.verify(params)

