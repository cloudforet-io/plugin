# -*- coding: utf-8 -*-
import logging

from google.protobuf.json_format import MessageToDict

from spaceone.core import pygrpc
from spaceone.core.connector import BaseConnector
from spaceone.core.utils import parse_endpoint
from spaceone.inventory.error import *

_LOGGER = logging.getLogger(__name__)


class PluginConnector(BaseConnector):

    def __init__(self, transaction, config):
        super().__init__(transaction, config)
        self.client = None

    def initialize(self, endpoint):
        if endpoint is None:
            raise ERROR_GRPC_CONFIGURATION
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

    def verify(self, options, secret_data):
        params = {
            'options': options,
            'secret_data': secret_data
            }
        # TODO: meta (plugin has no meta)
        meta = []
        verify_info = self.client.Collector.verify(params, metadata=meta)
        return verify_info

