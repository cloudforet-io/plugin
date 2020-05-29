# -*- coding: utf-8 -*-

import logging
import random

from spaceone.core.service import *
from spaceone.plugin.error.supervisor import *
from spaceone.plugin.manager.plugin_manager import *
from spaceone.plugin.manager.supervisor_manager import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler(exclude=['get_plugin_endpoint'])
@authorization_handler
@event_handler
class PluginService(BaseService):
    def __init__(self, metadata):
        super().__init__(metadata)
        self.supervisor_mgr: SupervisorManager = self.locator.get_manager('SupervisorManager')
        #self.supervisor_ref_mgr: SupervisorRefManager = self.locator.get_manager('SupervisorRefManager')
        self.plugin_mgr: PluginManager = self.locator.get_manager('PluginManager')
        self.plugin_ref_mgr: PluginRefManager = self.locator.get_manager('PluginRefManager')

    @transaction
    @check_required(['plugin_id', 'version', 'labels', 'domain_id'])
    @append_query_filter(filter_keys=['plugin_id', 'version', 'labels', 'domain_id'])
    def get_plugin_endpoint(self, params: dict):
        """ Get plugin_endpoint

        Args:
            params(dict) {
                    'plugin_id': 'str',
                    'version': 'str',
                    'labels': 'dict',
                    'domain_id': 'str'
                }
        """
        plugin_id = params['plugin_id']
        version = params['version']
        labels = params['labels']
        self.domain_id = params['domain_id']

        # Find at Plugin Ref Manager
        req_params = params.get('query', {})
        _LOGGER.debug(f'[get_plugin_endpoint] req_params: {req_params}')
        # TODO: check ACTIVE state
        installed_plugins, total_count = self.plugin_ref_mgr.list(req_params)
        if total_count > 0:
            selected_plugin = self._select_one(installed_plugins)
            _LOGGER.debug(f'[get_plugin_endpoint] selected plugin: {selected_plugin.plugin_owner.endpoint}')
            return selected_plugin

        # There is no installed plugin
        # Create or Fail
        matched_supervisors = self.supervisor_mgr.get_matched_supervisors(self.domain_id, labels)
        _LOGGER.debug(f'[get_plugin_endpoint] create new plugin')
        if len(matched_supervisors) > 0:
            selected_supervisor = self._select_one(matched_supervisors)
            _LOGGER.debug(f'[get_matched_supervisors] selected_supervisor: {selected_supervisor}')
            installed_plugin = self._get_installed_plugin(selected_supervisor, params)
            _LOGGER.debug(f'[get_matched_supervisors] installed_plugin: {installed_plugin}')
            return installed_plugin

        raise ERROR_NO_POSSIBLE_SUPERVISOR(params=params)


    def _get_installed_plugin(self, supervisor, params):
        """ Get installed plugin at supervisor which is matched with params

        Args:
            supervisor: supervisor_vo
            params (dict) : {
                'plugin_id': 'str',
                'version': 'str',
                'labels': 'dict',
                'domain_id': 'str'
            }
        Returns: installed_plugin_ref
        """
        # Find first
        supervisor_id = supervisor.supervisor_id
        plugin_id = params['plugin_id']
        version = params['version']
        domain_id = supervisor.domain_id
        installed_plugin = self.plugin_mgr.search_plugin(supervisor_id, plugin_id, version, domain_id)
        _LOGGER.debug(f'[_get_installed_plugin] {installed_plugin}')

        if installed_plugin == None:
            # If not, create it
            _LOGGER.debug(f'[_get_installed_plugin] create new plugin, supervisor_id: {supervisor_id}')
            installed_plugin = self.plugin_mgr.install_plugin(supervisor, plugin_id, version)

        installed_plugin_ref = self._get_installed_ref_plugin(supervisor, installed_plugin, params)
        return installed_plugin_ref

    def _get_installed_ref_plugin(self, supervisor, installed_plugin, params):
        supervisor_id = supervisor.supervisor_id
        plugin_id = params['plugin_id']
        version = params['version']
        domain_id = params['domain_id']

        installed_plugin_ref = self.plugin_ref_mgr.search_plugin(supervisor_id, plugin_id, version, domain_id)
        if installed_plugin_ref == None:
            _LOGGER.debug(f'[_get_installed_ref_plugin] need to create installed_plugin_ref')
            installed_plugin_ref = self.plugin_ref_mgr.install_plugin(supervisor, installed_plugin, params)
            _LOGGER.debug(f'[_get_installed_plugin] wait until ACTIVATED, {installed_plugin_ref}')
            self.plugin_mgr.wait_until_activated(supervisor_id, plugin_id, version)
            installed_plugin_ref = self.plugin_ref_mgr.search_plugin(supervisor_id, plugin_id, version, domain_id)
        return installed_plugin_ref


    def _select_one(self, choice_list, algorithm="random"):
        if algorithm == "random":
            return random.choice(choice_list)
        _LOGGER.error(f'[_select_one] unimplemented algorithm: {algorithm}')

#        # Find or create my supervisor
#        reference = False
#        matched_supvr = self.supervisor_mgr.get_matched_supervisor(self.domain_id, labels)
#        # TODO: if None, there is no matched supervisor
#        _LOGGER.debug(f'[get_plugin_endpoint] matched_supvr: {matched_supvr}')
#        if matched_supvr == None:
#            # find public supervisor
#            reference = True
#            public_matched_supvr = self.supervisor_mgr.get_public_supervisor(labels)
#            # This means public supervisor exist, but my reference does not exist
#            if public_matched_supvr:
#                _LOGGER.debug(f'[get_plugin_endpoint] public_matched_supervisor: {public_matched_supvr.supervisor_id}')
#                # TODO: label 
#                matched_supvr = self._create_supervisor_reference(public_matched_supvr, self.domain_id)
#            else:
#                # TODO: return value
#                #raise ERROR_NOT_FOUND(key='supervsior', value=labels)
#                raise ERROR_NO_POSSIBLE_SUPERVISOR(params=params)
#                return False
#
#        # In here, we have matched supervisor or supervisor_ref
#        _LOGGER.debug(f'[get_plugin_endpoint] matched supervisor: {matched_supvr} (ref:{reference})')
#        if reference:
#            # Get plugin. if no install plugin
#            try:
#                installed_plugin: InstalledPlugin = self.plugin_ref_mgr.get(
#                                                        supervisor_id=matched_supvr.supervisor_id,
#                                                        domain_id=self.domain_id,
#                                                        plugin_id=plugin_id, 
#                                                        version=version)
#            except ERROR_NOT_FOUND:
#                installed_plugin = None
#        else:
#            try:
#                installed_plugin: InstalledPlugin = self.plugin_mgr.get(
#                                                        supervisor_id=matched_supvr.supervisor_id,
#                                                        domain_id=self.domain_id,
#                                                        plugin_id=plugin_id, 
#                                                        version=version)
#            except ERROR_NOT_FOUND:
#                installed_plugin = None
#
#        if installed_plugin:
#            # return endpoint
#            return installed_plugin
#
#        # If we are here, there is no plugin installed
#        param_create = {
#            'domain_id': self.domain_id,
#            'plugin_id': plugin_id,
#            'version': version,
#            'supervisor': matched_supvr
#        }
#        if reference:
#            # TODO: there may be no installed_plugin at supervisor
#            # get public_supervisor
#            # get installed_plugins
#            # if there is no installed plugin, install it first
#            if public_matched_supvr:
#                p_domain_id = public_matched_supvr.domain_id
#                p_supervisor_id = public_matched_supvr.supervisor_id
#                (tf, p_plugin) = self.plugin_mgr.exist(p_supervisor_id,
#                                                        p_domain_id,
#                                                        plugin_id,
#                                                        version)
#                if tf == False:
#                    # Public Installed Plugin does not exist
#                    # Install It
#                    p_create = {
#                        'domain_id': p_domain_id,
#                        'plugin_id': plugin_id,
#                        'version': version,
#                        'supervisor': public_matched_supvr
#                        }
#                    p_installed_plugin = self.plugin_mgr.create(p_create)
#                    # Wait until Active
#                    p_installed_plugin = self.plugin_mgr.wait_until_activated(plugin_id, 
#                                                                        version,
#                                                                        public_matched_supvr.supervisor_id)
# 
#
#            # create plugin, return installed_plugin
#            installed_plugin: InstalledPlugin = self.plugin_ref_mgr.create(param_create)
#            installed_plugin: InstalledPlugin = self.plugin_ref_mgr.get(
#                                                    supervisor_id=matched_supvr.supervisor_id,
#                                                    domain_id=self.domain_id,
#                                                    plugin_id=plugin_id, 
#                                                    version=version)
#
#        else:
#            installed_plugin: InstalledPlugin = self.plugin_mgr.create(param_create)
#            # Wait until Active
#            installed_plugin = self.plugin_mgr.wait_until_activated(plugin_id, 
#                                                                        version,
#                                                                        matched_supvr.supervisor_id)
#        return installed_plugin

    @transaction
    @check_required(['plugin_id', 'version', 'supervisor_id', 'domain_id'])
    def notify_failure(self, param: dict):

        self.domain_id = param['domain_id']

        # since supervisor_id exists, don't need to know domain_id

        plugin_vo = self.plugin_mgr.mark_failure(
            supervisor_id=param['supervisor_id'],
            plugin_id=param['plugin_id'],
            version=param['version']
        )

        return None

    @transaction
    @check_required(['plugin_id', 'version', 'domain_id'])
    def verify(self, params: dict):
        """ Verify options and secret_data is correct information for specific plugin

        Args:
            params(dict) {
                    'plugin_id': str,
                    'version': str,
                    'options': dict,
                    'secret_id': str,
                    'domain_id': str
                }

        Returns:
            True | False
        """

        # get plugin_endpoint, then ask verify
        # labels for any match
        requested_params = {
            'plugin_id': params['plugin_id'],
            'version': params['version'],
            'labels': {},
            'domain_id': params['domain_id']
        }
        plugin_endpoint = self.get_plugin_endpoint(requested_params)

        # secret
        if 'secret_id' in params:
            # Patch secret_data from secret
            resp = self.plugin_mgr.get_secret_data(params['secret_id'], params['domain_id'])
            secret_data = resp.data
        else:
            # Empty secret
            secret_data = {}

        # options
        options = params.get('options', {})

        return self.plugin_mgr.call_verify_plugin(plugin_endpoint, options, secret_data)

#    def _create_supervisor_reference(self, supvr, domain_id):
#        params = {
#            'supervisor_id': supvr.supervisor_id,
#            'domain_id': domain_id,
#            'supervisor': supvr
#        }
#        return self.supervisor_ref_mgr.create(params)
