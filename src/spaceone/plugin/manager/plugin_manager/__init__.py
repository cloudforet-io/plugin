# -*- coding: utf-8 -*-

import logging
import time

from spaceone.core.error import ERROR_NOT_FOUND
from spaceone.core.manager import BaseManager
from spaceone.plugin.manager.plugin_manager.plugin_ref_manager import *
from spaceone.plugin.manager.plugin_manager.plugin_state import *
from spaceone.plugin.connector.repository_connector import RepositoryConnector
from spaceone.plugin.model import *
from spaceone.plugin.error import *

__all__ = [
    'PluginManager',
    'PluginRefManager',
    'ProvisioningState',
    'ActiveState',
    'ReprovisioningState',
    'ErrorState'
    ]

_LOGGER = logging.getLogger(__name__)

WAIT_TIMEOUT = 60


class PluginManager(BaseManager):
    def __init__(self, transaction):
        super().__init__(transaction)
        self._installed_plugin_model: InstalledPlugin = self.locator.get_model('InstalledPlugin')

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

        _LOGGER.debug(f'[create] params: {params}')
        # Check plugin_id exist or not
        supervisor = params['supervisor']
        params['supervisor_id'] = supervisor.supervisor_id

        repo_connector = self.locator.get_connector('RepositoryConnector')
        repo_connector.get_plugin(params['plugin_id'], params['domain_id'])

        plugin = self._installed_plugin_model.create(params)
        self.transaction.add_rollback(_rollback, plugin)

        # Create Reference also
        plugin_ref_mgr = self.locator.get_manager('PluginRefManager')
        plugin_ref = params.copy()
        plugin_ref['plugin_owner'] = plugin
        plugin_ref['managed'] = True
        plugin_ref = plugin_ref_mgr.create(plugin_ref)
        self.transaction.add_rollback(_rollback, plugin_ref)

        return plugin

    def delete(self, supervisor_id, plugin_id, version, domain_id):
        """ Delete Supervisor
        """
        install_plugin = self.get(supervisor_id, domain_id, plugin_id, version)
        # TODO: delete plugin_ref also
        install_plugin.delete()

    def get(self, supervisor_id, domain_id, plugin_id, version):
        """ get installed_plugin

        Warning: Cannot get supervisor_id(Reference) directly,
        """
        plugin = self._installed_plugin_model.get(supervisor_id=supervisor_id,
                                                  domain_id=domain_id,
                                                  plugin_id=plugin_id,
                                                  version=version)
        return plugin

    def list(self, query):
        return self._installed_plugin_model.query(**query)

    def search_plugin(self, supervisor_id, plugin_id, version, domain_id, state='ACTIVE'):
        """ Get installed_plugin
        """
        try:
            # Warning DONOT USE get, state is reference
            # Warning, state query is not working, check late
            search_plugin_param = _make_search_plugin_param(supervisor_id, plugin_id, version, domain_id, state)
            plugins, total_count = self.list(search_plugin_param)
            if total_count == 1:
                print(f"XXXXX Plugin.state = {plugins[0].state}")
                return plugins[0]
            _LOGGER.debug(f'[search_plugin] not found {supervisor_id}, {plugin_id}, {version}, {state}')
            return None
        except Exception as e:
            _LOGGER.debug(f'[search_plugin] not found {supervisor_id}, {plugin_id}, {version}, {state}, {e}')
            return None

    def _get_installed_plugin(self, supervisor_id, plugin_id, version):
        return self._installed_plugin_model.get(plugin_id=plugin_id, version=version, supervisor_id=supervisor_id)

    def install_plugin(self, supervisor, plugin_id, version):
        """ Install Plugin based on supervisor info
        Wait until plugin is installed

        Returns: installed_plugin_vo
        """
        def _rollback(vo):
            vo.delete()

        create_params = {
            'supervisor': supervisor,
            'plugin_id': plugin_id,
            'version': version,
            'domain_id': supervisor.domain_id
        }
        _LOGGER.debug(f'[install_plugin] create_params: {create_params}')
        installed_plugin = self.create(create_params)
        self.transaction.add_rollback(_rollback, installed_plugin)

        return installed_plugin

#    def install_plugin(self, params):
#        def _rollback(vo):
#            vo.delete()
#
#        plugin_vo: InstalledPlugin = self._installed_plugin_model.create(params)
#        self.transaction.add_rollback(_rollback, plugin_vo)
#
#        return plugin_vo

    def update_plugin(self, params):
        def _rollback(old_data: dict):
            plugin_vo.update(old_data)

        plugin_vo: InstalledPlugin = self._get_installed_plugin(params['supervisor_id'],
                                                                params['plugin_id'],
                                                                params['version'])
        self.transaction.add_rollback(_rollback, plugin_vo.to_dict())

        return plugin_vo.update(params)

    def activate_plugin(self, params):
        def _rollback(old_data: dict):
            plugin_vo.update(old_data)

        plugin_vo: InstalledPlugin = self._get_installed_plugin(params['supervisor_id'],
                                                                params['plugin_id'],
                                                                params['version'])
        self.transaction.add_rollback(_rollback, plugin_vo.to_dict())

        plugin_state_machine = PluginStateMachine(params['plugin_id'], plugin_vo.state)
        state = plugin_state_machine.activate()
        params['state'] = state

        return plugin_vo.update(params)

    def update_plugin_state(self, plugin_id, version, state, endpoint, supervisor_id):
        plugin_vo = self._installed_plugin_model.get(supervisor_id=supervisor_id,
                                            plugin_id=plugin_id,
                                            version=version)
        return plugin_vo.update({'state':state, 'endpoint':endpoint})

    def make_reprovision(self, supervisor_id,  plugin_id, version):
        def _rollback(old_data: dict):
            plugin_vo.update(old_data)

        plugin_vo: InstalledPlugin = self._get_installed_plugin(params['supervisor_id'], params['plugin_id'], params['version'])
        self.transaction.add_rollback(_rollback, plugin_vo.to_dict())

        plugin_state_machine = PluginStateMachine(plugin_id, plugin_vo.state)
        state = plugin_state_machine.make_reprovision()

        return plugin_vo.update({'state': state})

    def mark_failure(self, supervisor_id, plugin_id, version):
        def _rollback(old_data: dict):
            plugin_vo.update(old_data)

        plugin_vo: InstalledPlugin = self._installed_plugin_model.get(
            plugin_id=plugin_id,
            version=version,
            supervisor_id=supervisor_id
        )

        self.transaction.add_rollback(_rollback, plugin_vo.to_dict())

        plugin_state_machine = PluginStateMachine(plugin_id, plugin_vo.state)
        state = plugin_state_machine.change_to_error()

        return plugin_vo.update({'state': state})

    def wait_until_activated(self, supervisor_id, plugin_id, version):
        count = 0
        while True:
            installed_plugin = self._safe_delay_get_installed_plugin(supervisor_id, plugin_id, version,  3)
            if installed_plugin and installed_plugin.state == 'ACTIVE':
                break
            # Wait
            count = count + 1
            _LOGGER.debug(f'[wait_until_activated] {count}/{WAIT_TIMEOUT}')
            if count > WAIT_TIMEOUT:
                _LOGGER.error("[wait_until_activated] Timeout for activate")
                self.mark_failure(plugin_id, version, supervisor_id)
                raise ERROR_INSTALL_PLUGIN_TIMEOUT(supervisor_id=supervisor_id, plugin_id=plugin_id, version=version)

            time.sleep(1)

        return installed_plugin

    # Verify
    def get_secret_data(self, secret_id, domain_id):
        connector = self.locator.get_connector('SecretConnector')
        return connector.get_data(secret_id, domain_id)

    def call_verify_plugin(self, plugin_endpoint, options, secret_data):
        """ Call verify function at endpoint
        """
        # Issue: CLOUD-941

    def _safe_delay_get_installed_plugin(self, supervisor_id, plugin_id, version, delay_second=0):
        if 0 < delay_second < 30:
            time.sleep(delay_second)

        try:
            _LOGGER.debug(f'[_safe_delay_get_installed_plugin] supervisor_id: {supervisor_id}')
            return self._installed_plugin_model.get(supervisor_id=supervisor_id, plugin_id=plugin_id, version=version)
        except Exception as e:
            _LOGGER.debug(f'[_safe_delay_get_installed_plugin] {e}')
            return None


# Static method
def _make_plugin_params(supervisor, plugin_id, image, version, name):
    return {
        'supervisor': supervisor,
        'supervisor_id': supervisor.supervisor_id,
        'domain_id': supervisor.domain_id,
        'name': name,
        'plugin_id': plugin_id,
        'image': image,
        'version': version
    }


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

