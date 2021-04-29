import logging
import random

from spaceone.core.service import *
from spaceone.plugin.error import *
from spaceone.plugin.manager.plugin_manager import *
from spaceone.plugin.manager.supervisor_manager import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler(exclude=['get_plugin_endpoint'])
@authorization_handler(exclude=['get_plugin_endpoint'])
@mutation_handler(exclude=['get_plugin_endpoint'])
@event_handler
class PluginService(BaseService):
    def __init__(self, metadata):
        super().__init__(metadata)
        self.supervisor_mgr: SupervisorManager = self.locator.get_manager('SupervisorManager')
        #self.supervisor_ref_mgr: SupervisorRefManager = self.locator.get_manager('SupervisorRefManager')
        self.plugin_mgr: PluginManager = self.locator.get_manager('PluginManager')
        self.plugin_ref_mgr: PluginRefManager = self.locator.get_manager('PluginRefManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['plugin_id', 'version', 'domain_id'])
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
        labels = params.get('labels', {})
        self.domain_id = params['domain_id']

        # Find at Plugin Ref Manager
        req_params = params.get('query', {})
        _LOGGER.debug(f'[get_plugin_endpoint] req_params: {req_params}')
        # TODO: check ACTIVE state
        installed_plugins, total_count = self.plugin_ref_mgr.list(req_params)

        for selected_plugin in installed_plugins:
            try:
                # TODO: label match
                _LOGGER.debug(f'[get_plugin_endpoint] selected plugin: {selected_plugin.plugin_owner.endpoint}')
                return self._select_endpoint(selected_plugin)
            except Exception as e:
                _LOGGER.error(f'[get_plugin_endpoint] delete failed plugin, {selected_plugin}')
                selected_plugin.delete()

        # There is no installed plugin
        # Check plugin_id, version is valid or not
        self._check_plugin(plugin_id, version, self.domain_id)

        # Create or Fail
        matched_supervisors = self.supervisor_mgr.get_matched_supervisors(self.domain_id, labels)
        _LOGGER.debug(f'[get_plugin_endpoint] create new plugin')
        if len(matched_supervisors) > 0:
            selected_supervisor = self._select_one(matched_supervisors)
            _LOGGER.debug(f'[get_matched_supervisors] selected_supervisor: {selected_supervisor}')
            installed_plugin = self._get_installed_plugin(selected_supervisor, params)
            _LOGGER.debug(f'[get_matched_supervisors] installed_plugin: {installed_plugin}')
            return self._select_endpoint(installed_plugin)

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
            #print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            #print("XXXXXXXXX wait until activated XXXXXXXXXX")
            #self.plugin_mgr.wait_until_activated(supervisor_id, plugin_id, version)

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
            #_LOGGER.debug(f'[_get_installed_plugin] wait until ACTIVATED, {installed_plugin_ref}')
            #self.plugin_mgr.wait_until_activated(supervisor_id, plugin_id, version)
            installed_plugin_ref = self.plugin_ref_mgr.search_plugin(supervisor_id, plugin_id, version, domain_id)
        return installed_plugin_ref

    def _select_endpoint(self, plugin_ref):
        """ Select one of plugins, then return endpoint
        """
        installed_plugin = plugin_ref.plugin_owner

        # Update endpoint_called_at
        installed_plugin.update_endpoint_called_at()

        # plugin state = ACTIVE | PROVISIONING
        state = installed_plugin.state
        if state == 'ACTIVE':
            pass
        elif state == 'PROVISIONING' or state == 'RE_PROVISIONING':
            # get up-to-date installed_plugin
            # ex) installed_plugin.endpoint
            installed_plugin = self.plugin_mgr.wait_until_activated(installed_plugin.supervisor_id,
                                                 installed_plugin.plugin_id,
                                                 installed_plugin.version)
        else:
            _LOGGER.error(f'[_select_endpoint] notify failure, {installed_plugin}')
            params = {'plugin_id': installed_plugin.plugin_id,
                      'version': installed_plugin.version,
                      'supervisor_id': installed_plugin.supervisor_id,
                      'domain_id': installed_plugin.domain_id}
            self.notify_failure(params)
            raise ERROR_INSTALL_PLUGIN_TIMEOUT(supervisor_id=installed_plugin.supervisor_id,
                                               plugin_id=installed_plugin.plugin_id,
                                               version=installed_plugin.version)

        endpoint = installed_plugin.endpoint
        endpoints = installed_plugin.endpoints
        if endpoints:
            _LOGGER.debug(f'[_select_endpoint] {endpoints}')
            endpoint = self._select_one(endpoints)

        return {'endpoint': endpoint}

    @staticmethod
    def _select_one(choice_list, algorithm="random"):
        if algorithm == "random":
            return random.choice(choice_list)
        _LOGGER.error(f'[_select_one] unimplemented algorithm: {algorithm}')

    def _check_plugin(self, plugin_id, version, domain_id):
        """ Check plugin_id:version exist or not
        """
        repo_mgr = self.locator.get_manager('RepositoryManager')
        # Check plugin_id
        try:
            repo_mgr.get_plugin(plugin_id, domain_id)
        except Exception as e:
            _LOGGER.error(f'[_check_plugin] {plugin_id} does not exist')
            raise ERROR_PLUGIN_NOT_FOUND(plugin_id=plugin_id)

        # Check version
        try:
            repo_mgr.check_plugin_version(plugin_id, version, domain_id)
        except Exception as e:
            raise ERROR_INVALID_PLUGIN_VERSION(plugin_id=plugin_id, version=version)

    @transaction(append_meta={'authorization.scope': 'SYSTEM'})
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

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
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

