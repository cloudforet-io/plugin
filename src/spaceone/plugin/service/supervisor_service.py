import logging
from datetime import datetime, timedelta

from spaceone.core.error import *
from spaceone.core.service import *
# from spaceone.plugin.model import Supervisor, SupervisorRef
from spaceone.plugin.error import *
from spaceone.plugin.manager.plugin_manager import *
from spaceone.plugin.manager.supervisor_manager import *
from spaceone.plugin.manager.identity_manager import *

_LOGGER = logging.getLogger(__name__)

ELAPSED_DAYS = 2


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class SupervisorService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self._supervisor_mgr: SupervisorManager = self.locator.get_manager('SupervisorManager')
        # self._supervisor_ref_mgr: SupervisorRefManager = self.locator.get_manager('SupervisorRefManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'hostname', 'domain_id'])
    def publish(self, params):
        _LOGGER.debug(f'[publish] params: {params}')
        plugin_mgr: PluginManager = self.locator.get_manager('PluginManager')

        domain_id = params['domain_id']
        try:
            # unique: hostname + name
            supervisor = self._supervisor_mgr.get_by_hostname(params['hostname'], domain_id)
        except ERROR_NOT_FOUND:
            # create new supervisor
            supervisor = self._supervisor_mgr.create(params)
            ###############################
            # East EGG for Automatic Test
            ###############################
            if params['name'] == 'root':
                self._supervisor_mgr.update(
                    {'supervisor_id': supervisor.supervisor_id, 'is_public': True, 'domain_id': domain_id})

        if supervisor:
            plugins_info = params.get('plugin_info', [])
            print(f'[publish] plugin_info: {plugins_info}')
            for plugin in plugins_info:
                # Update State (XXXX -> ACTIVE)
                # Update endpoint (grpc://xxxx)
                # There may be no plugin at DB (maybe deleted, or supervisor's garbage)
                # self._plugin_mgr.update_plugin(plugin)
                _LOGGER.debug(f'[publish] plugin={plugin}')
                try:
                    plugin_mgr.update_plugin_state(plugin['plugin_id'],
                                                   plugin['version'],
                                                   plugin['state'],
                                                   plugin['endpoint'],
                                                   supervisor.supervisor_id)
                except Exception as e:
                    _LOGGER.error(f'[publish] e={e}')
                    _LOGGER.warning(f'[publish] Failed update plugin.state:{plugin["state"]}')
                # Update endpoints, if needed
                if 'endpoints' in plugin:
                    _LOGGER.debug(f'[publish] endpoints: {plugin["endpoints"]}')
                    plugin_mgr.update_plugin_endpoints(plugin['plugin_id'],
                                                       plugin['version'],
                                                       supervisor.supervisor_id,
                                                       plugin['endpoints'])
        else:
            # There is no plugin_info
            supervisor = self._supervisor_mgr.create(params)

        return supervisor

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['supervisor_id', 'domain_id'])
    def register(self, params):
        domain_id = params['domain_id']
        _LOGGER.debug(f'[register] params: {params}')

        # TODO: Should I validate supervisor_id?
        return self._supervisor_mgr.register(params['supervisor_id'], domain_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['supervisor_id', 'domain_id'])
    def update(self, params):
        domain_id = params['domain_id']
        _LOGGER.debug(f'[update] params: {params}')

        # TODO: Should I validate supervisor_id?
        return self._supervisor_mgr.update(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['supervisor_id', 'domain_id'])
    def deregister(self, params):
        domain_id = params['domain_id']
        _LOGGER.debug(f'[deregister] supervisor_id: {params["supervisor_id"]}')
        self._supervisor_mgr.delete(params['supervisor_id'], domain_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['supervisor_id', 'domain_id'])
    def enable(self, params):
        domain_id = params['domain_id']
        _LOGGER.debug(f'[enable] supervisor_id: {params["supervisor_id"]}')
        return self._supervisor_mgr.enable(params['supervisor_id'], domain_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['supervisor_id', 'domain_id'])
    def disable(self, params):
        domain_id = params['domain_id']
        _LOGGER.debug(f'[disable] supervisor_id: {params["supervisor_id"]}')
        return self._supervisor_mgr.disable(params['supervisor_id'], domain_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['supervisor_id', 'plugin_id', 'version', 'domain_id'])
    def recover_plugin(self, params):
        """ Recover plugin if exist
        """
        supervisor_id = params['supervisor_id']
        domain_id = params['domain_id']

        try:
            supervisor = self._get_supervisor_by_id(supervisor_id, domain_id)
        except Exception as e:
            _LOGGER.info(f'[recover_plugin] No matched supervisor, \
                                supervisor_id: {supervisor_id}, domain_id: {domain_id}')
            raise ERROR_NOT_SUPPORT_RECOVER_PLUGIN(supervisor_id=supervisor_id)

        plugin_id = params['plugin_id']
        version = params['version']

        # Get plugin_info
        plugin_mgr: PluginManager = self.locator.get_manager('PluginManager')

        plugin_vo = plugin_mgr.get(supervisor_id, domain_id, plugin_id, version)

        # Get endpoint
        endpoint = plugin_vo.endpoint
        plugin_vo = plugin_mgr.make_reprovision(supervisor_id, plugin_id, version)
        return plugin_vo

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['supervisor_id', 'domain_id'])
    def get(self, params):
        """ Get PluginManager

        Args:
            params:
                - supervisor_id
                - domain_id (from metadata)
                - only (list)
        Returns:
            PluginManagerData
        """

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['supervisor_id', 'name', 'is_public', 'hostname', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['supervisor_id', 'name', 'hostname'])
    def list(self, params):
        query = params.get('query', {})
        return self._supervisor_mgr.list_supervisors(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['supervisor_id', 'name', 'hostname'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.get('query', {})
        return self._supervisor_mgr.stat_supervisors(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['domain_id', 'supervisor_id', 'hostname', 'plugin_id', 'version', 'state', 'endpoint'])
    @append_keyword_filter(['supervisor_id', 'hostname', 'plugin_id'])
    def list_plugins(self, params):
        """
        Find all plugins at plugin_ref
        This function is usually called by Supervisor for sync plugins
        """

        query = params.get('query', {})
        plugin_ref_manager = self.locator.get_manager('PluginRefManager')
        return plugin_ref_manager.list(query)

    @transaction(append_meta={'authorization.scope': 'SYSTEM'})
    @check_required(['domain_id'])
    def cleanup_plugins(self, params):
        """ cleanup unused plugins of domain
        """
        domain_id = params['domain_id']
        # Find plugins of last_get_endpoint
        now = datetime.utcnow()
        delta = timedelta(days=ELAPSED_DAYS)
        diff = now-delta
        plugin_mgr: PluginManager = self.locator.get_manager('PluginManager')
        query = {'filter':
                    [
                        {'k': 'endpoint_called_at', 'v': diff.isoformat(), 'o': 'datetime_lt'},
                        {'k': 'domain_id', 'v': domain_id, 'o': 'eq'}
                    ]
                }
        (plugins, total_count) = plugin_mgr.list(query)
        for plugin in plugins:
            try:
                supervisor_id = plugin.supervisor_id
                plugin_id = plugin.plugin_id
                version = plugin.version
                _LOGGER.debug(f'[cleanup_plugins] delete plugin: {supervisor_id}, {plugin_id}, {version}, {domain_id}')
                plugin_mgr.delete(supervisor_id, plugin_id, version, domain_id)
            except Exception as e:
                _LOGGER.error(f'[cleanup_plugins] failed to delete plugin: {plugin}\n{e}')

    @transaction(append_meta={'authorization.scope': 'SYSTEM'})
    @append_query_filter([])
    def list_domains(self, params):
        """ This is used by Scheduler
        Returns:
            results (list)
            total_count (int)
        """
        mgr = self.locator.get_manager('IdentityManager')
        query = params.get('query', {})
        result = mgr.list_domains(query)
        return result

    def _get_supervisor_by_id(self, supervisor_id, domain_id):
        """ Find Supervisor with supervisor_id
        Return may be Supervisor
        """
        return self._supervisor_mgr.get_by_id(supervisor_id, domain_id)

    def _find_supervisor(self, supervisor_id, hostname, domain_id):
        """ Return supervisor from supervisor
        """
        try:
            resp = self._supervisor_mgr.get_by_id_or_hostname(supervisor_id, hostname, domain_id)
            return resp
        except Exception as e:
            _LOGGER.debug(f'[_find_supervisor] not found at supervisor, \
                                supervisor_id: {supervisor_id}, domain_id: {domain_id}, {e}')


def _query_supervisor(supervisor_id, domain_id):
    return {
        'filter': [
            {
                'k': 'domain_id',
                'v': domain_id,
                'o': 'eq'
            },
            {
                'k': 'supervisor_id',
                'v': supervisor_id,
                'o': 'eq'
            }
        ]
    }
