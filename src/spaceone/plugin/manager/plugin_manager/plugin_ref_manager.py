# -*- coding: utf-8 -*-

import logging
import time

from spaceone.core.error import ERROR_NOT_FOUND
from spaceone.core.manager import BaseManager
from spaceone.plugin.manager.plugin_manager.plugin_state import PluginStateMachine, ACTIVE, PROVISIONING, \
    RE_PROVISIONING
from spaceone.plugin.model import *

__all__ = ['PluginRefManager']

_LOGGER = logging.getLogger(__name__)

WAIT_TIMEOUT = 60


class PluginRefManager(BaseManager):
    def __init__(self, transaction):
        super().__init__(transaction)
        self._installed_plugin_ref_model: InstalledPluginRef = self.locator.get_model('InstalledPluginRef')

    def create(self, params):
        """
        Args:
            params(dict) : {
                    'domain_id' : str,
                    'plugin_id' : str,
                    'version'   : str,
                    'supervisor': str
                }
        """
        def _rollback(vo):
            vo.delete()
        supervisor = params['supervisor']
        params['supervisor_id'] = supervisor.supervisor_id
        _LOGGER.debug(f'[create] params: {params}')
        plugin = self._installed_plugin_ref_model.create(params)
        _LOGGER.debug(f'[create] result : {plugin}')
        return plugin

    def delete(self, supervisor_id, plugin_id, version, domain_id):
        """ Delete Supervisor
        """
        installed_plugin_ref = self.get(supevisor_id, domain_id, plugin_id, version)
        installed_plugin_ref.delete()

    def get(self, supervisor_id, domain_id, plugin_id, version):
        """ get installed_plugin
        """
        plugin = self._installed_plugin_ref_model.get(supervisor_id=supervisor_id,
                                                domain_id=domain_id,
                                                plugin_id=plugin_id,
                                                version=version)
        return plugin

    def list(self, query):
        _LOGGER.debug(f'[list] query: {query}')
        result = self._installed_plugin_ref_model.query(**query)
        _LOGGER.debug(f'[list] query: {result}')
        return result

    def search_plugin(self, supervisor_id, plugin_id, version, domain_id, state='ACTIVE'):
        """ Get installed_plugin
        """
        try:
            # Warning DONOT USE get, state is reference
            # Warning, state query is not working, check late
            search_plugin_param = _make_search_plugin_param(supervisor_id, plugin_id, version, domain_id, state)
            plugins, total_count = self.list(search_plugin_param)
            if total_count == 1:
                print(f"XXXXX Plugin.state = {plugins[0].plugin_owner.state}")
                return plugins[0]
            _LOGGER.debug(f'[search_plugin] not found {supervisor_id}, {plugin_id}, {version}, {state}')
            return None
        except Exception as e:
            _LOGGER.debug(f'[search_plugin] not found {supervisor_id}, {plugin_id}, {version}, {state}, {e}')
            return None


    def install_plugin(self, supervisor, installed_plugin, params):
        """ Install Plugin at PluginRef with supervisor

        Args:
            supervisor: supervisor_vo
            params (dict): {
                'pluing_id': 'str',
                'version': 'str',
                'labels': 'dict',
                'domain_id': 'str'
            }

        Returns: installed_plugin_ref_vo
        """
        is_mine = True
        if supervisor.domain_id != params['domain_id']:
            is_mine = False

        db_params = params.copy()
        db_params.update({
                'supervisor': supervisor,
                'plugin_owner': installed_plugin,
                'managed': is_mine
                })
        _LOGGER.debug(f'[install_plugin] params: {db_params}')
        _LOGGER.debug(f'[install_plugin] installed_plugin: {installed_plugin.plugin_id}')
        installed_plugin_ref = self.create(db_params)

        return installed_plugin_ref

def _make_search_plugin_param(supervisor_id, plugin_id, version, domain_id, state):
#    return {
#        'filter': [
#            {'k': 'supervisor_id',  'v': supervisor_id, 'o': 'eq'},
#            {'k': 'plugin_id',      'v': plugin_id,     'o': 'eq'},
#            {'k': 'version',        'v': version,       'o': 'eq'},
#            {'k': 'domain_id',      'v': domain_id,     'o': 'eq'},
#            {'k': 'plugin_owner.state',          'v': state,         'o': 'eq'}
#        ]
#    }
    return {
        'filter': [
            {'k': 'supervisor_id',  'v': supervisor_id, 'o': 'eq'},
            {'k': 'plugin_id',      'v': plugin_id,     'o': 'eq'},
            {'k': 'version',        'v': version,       'o': 'eq'},
            {'k': 'domain_id',      'v': domain_id,     'o': 'eq'},
            {'k': 'state',          'v': state,         'o': 'eq'}
        ]
    }

