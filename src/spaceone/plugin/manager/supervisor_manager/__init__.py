# -*- coding: utf-8 -*-

import logging
import random

from spaceone.core.manager import BaseManager

from spaceone.plugin.error import *
from spaceone.plugin.manager.supervisor_manager.supervisor_state import * 
from spaceone.plugin.model.supervisor_model import Supervisor

__all__ = [
    'SupervisorManager',
    'PendingState',
    'EnabledState',
    'DisabledState',
    'DisconnectedState',
    'SupervisorStateMachine'
]

_LOGGER = logging.getLogger(__name__)


class SupervisorManager(BaseManager):
    def __init__(self, transaction):
        super().__init__(transaction)
        self._supervisor_model = self.locator.get_model('Supervisor')

    def create(self, params):
        def _rollback(vo):
            vo.delete()

        _LOGGER.debug(f'[create] params: {params}')
        supervisor: Supervisor = self._supervisor_model.create(params)
        self.transaction.add_rollback(_rollback, supervisor)
        return supervisor

    def get_by_hostname(self, hostname, domain_id):
        return self._supervisor_model.get(hostname=hostname, domain_id=domain_id)

    def get_by_id(self, supervisor_id, domain_id):
        return self._supervisor_model.get(supervisor_id=supervisor_id, domain_id=domain_id)

    def get_by_id_or_hostname(self, supervisor_id, hostname, domain_id):
        if supervisor_id and hostname:
            return self._supervisor_model.get(supervisor_id=supervisor_id, hostname=hostname, domain_id=domain_id)
        if supervisor_id:
            return self._supervisor_model.get(supervisor_id=supervisor_id, domain_id=domain_id)
        if hostname:
            return self._supervisor_model.get(hostname=hostname, domain_id=domain_id)
        raise ERROR_NO_POSSIBLE_SUPERVISOR(params=domain_id)

    def delete(self, supervisor_id, domain_id):
        supervisor = self.get_by_id(supervisor_id, domain_id)

        # TODO: Check Installed Plugin(No Cascade)
        plugin_mgr = self.locator.getManager('PluginManager')
        installed_plugins = plugin_mgr.list_plugins_by_supervisor_id(supervisor_id, domain_id)
        if installed_plugins.total_count > 0:
            raise ERROR_INSTALLED_PLUGIN_EXIST(supervisor_id=supervisor_id)
        supervisor.delete()

    def register(self, supervisor_id, domain_id):
        supervisor = self.get_by_id(supervisor_id, domain_id)

        supervisor_state_machine = SupervisorStateMachine(supervisor_id, supervisor.state)
        supervisor_state_machine.register()

        return supervisor.update({'state': supervisor_state_machine.get_state()})

    def update(self, params):
        """
        Update method updates only [is_public, priority, labels, tags] fields.
        :param params: Supervisor
        :return: Supervisor
        """
        supervisor: Supervisor = self._supervisor_model.get(
            supervisor_id=params['supervisor_id'],
            domain_id=params['domain_id']
        )

        updatable_fields = ['is_public', 'priority', 'labels', 'tags', 'supervisor_id', 'domain_id']
        for key in list(params.keys()):
            if key not in updatable_fields:
                raise ERROR_SUPERVISOR_UPDATE(key=key)
        return supervisor.update(params)

    def enable(self, supervisor_id, domain_id):
        supervisor: Supervisor = self.get_by_id(supervisor_id, domain_id)

        supervisor_state_machine = SupervisorStateMachine(supervisor_id, supervisor.state)
        supervisor_state_machine.enable()
        return supervisor.update({'state': supervisor_state_machine.get_state()})

    def disable(self, supervisor_id, domain_id):
        supervisor: Supervisor = self.get_by_id(supervisor_id, domain_id)

        supervisor_state_machine = SupervisorStateMachine(supervisor_id, supervisor.state)
        supervisor_state_machine.disable()
        return supervisor.update({'state': supervisor_state_machine.get_state()})

    def get_all_supervisors(self, domain_id):
        """ List my supervisors and public supervisors
        """
        return self.list_supervisors(_query_domain_id_or_public(domain_id))

    def list_supervisors(self, query):
        return self._supervisor_model.query(**query)

    def stat_supervisors(self, query):
        return self._supervisor_model.stat(**query)

#    def get_matched_supervisor(self, domain_id, labels):
#        supervisors, total_count = self.get_all_supervisors(domain_id)
#        matched_supervisor = _get_matched_supervisor(supervisors, labels)
#        _LOGGER.debug(f'[get_matched_supervisor] matched_supervisor: {matched_supervisor}')
#        return matched_supervisor

    def get_matched_supervisors(self, domain_id, labels):
        supervisors, total_count = self.get_all_supervisors(domain_id)
        _LOGGER.debug(f'[get_matched_supervisors] possible list before label matching: {supervisors}')
        matched_supervisors = _get_matched_supervisors(supervisors, labels)
        _LOGGER.debug(f'[get_matched_supervisor] matched_supervisors: {matched_supervisors}')
        return matched_supervisors

#    def get_public_supervisor(self, labels):
#        query = _query_public()
#        supervisors, total_count = self.list_supervisors(query)
#        _LOGGER.debug(f'[get_public_supervisor] {total_count}')
#
#        matched_supervisor = _get_matched_supervisor(supervisors, labels)
#        return matched_supervisor

    def list_plugins(self, query):
        _LOGGER.debug(f'[supervisor_manager] list_plugins: {query}')
        plugin_mgr = self.locator.get_manager('PluginManager')
        return plugin_mgr.list(query)


def _get_matched_supervisors(supervisors, labels):
    matched_supervisors = list(map(
        lambda supervisor: supervisor if set(supervisor.labels).issuperset(labels) else None,
        supervisors
    ))
    return matched_supervisors


#def _get_matched_supervisor(supervisors, labels):
#    matched_supervisors = list(map(
#        lambda supervisor: supervisor if set(supervisor.labels).issuperset(labels) else None,
#        supervisors
#    ))
#
#    if matched_supervisors and len(matched_supervisors) > 0:
#        return random.choice(matched_supervisors)
#    return None


def _query_domain_id_and_enabled(domain_id):
    return {
        'filter': [
            {
                'k': 'domain_id',
                'v': domain_id,
                'o': 'eq'
            },
            {
                'k': 'state',
                'v': 'ENABLED',
                'o': 'eq'
            }
        ]
    }


def _query_domain_id(domain_id):
    return {
        'filter': [
            {
                'k': 'domain_id',
                'v': domain_id,
                'o': 'eq'
            }
        ]
    }


def _query_domain_id_or_public(domain_id):
    return {
        'filter_or': [
            {
                'k': 'domain_id',
                'v': domain_id,
                'o': 'eq'
            },
            {
                'k': 'is_public',
                'v': True,
                'o': 'eq'
            }
        ],
        'filter': [
            {
                'k': 'state',
                'v': 'ENABLED',
                'o': 'eq'
            }
        ]
    }

def _query_public():
    return {
        'filter': [
            {
                'k': 'is_public',
                'v': True,
                'o': 'eq'
            },
            {
                'k': 'state',
                'v': 'ENABLED',
                'o': 'eq'
            }
        ]
    }


# def _domain_params():
#     return {
#         'name': name,
#         'hostname': hostname,
#         'secret_key': secret_key,
#         'plugin_info': plugin_info,
#         'tags': tags
#     }
