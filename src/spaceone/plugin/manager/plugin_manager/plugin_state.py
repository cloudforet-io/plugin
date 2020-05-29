# -*- coding: utf-8 -*-

import abc

from spaceone.core.manager import BaseManager
from spaceone.plugin.error import *

__all__ = [
    'PluginState',
    'ProvisioningState',
    'ActiveState',
    'ReprovisioningState',
    'ErrorState'
]

ACTIVE = 'ACTIVE'
PROVISIONING = 'PROVISIONING'
ERROR = 'ERROR'
RE_PROVISIONING = 'RE_PROVISIONING'


class PluginState(metaclass=abc.ABCMeta):

    def __init__(self):
        self.handle()

    @abc.abstractmethod
    def handle(self):
        pass


class ProvisioningState(PluginState):

    def handle(self):
        # TODO: notify to SupervisorServer?
        pass

    def __str__(self):
        return PROVISIONING


class ActiveState(PluginState):

    def handle(self):
        pass

    def __str__(self):
        return ACTIVE


class ReprovisioningState(PluginState):

    def handle(self):
        pass

    def __str__(self):
        return RE_PROVISIONING


class ErrorState(PluginState):

    def handle(self):
        # TODO: notify?
        pass

    def __str__(self):
        return ERROR


STATE_DIC = {
    'PROVISIONING'  : ProvisioningState(),
    'ERROR'         : ErrorState(),
    'ACTIVE'        : ActiveState(),
    'RE_PROVISIONING':  ReprovisioningState()
}

class PluginStateMachine:

    def __init__(self, plugin_id, state):
        self._plugin_id = plugin_id
        self._state = _compute_state(state)

    def activate(self) -> str:
        if isinstance(self._state, (ProvisioningState, ReprovisioningState)):
            self._state = ActiveState()
        else:
            raise ERROR_PLUGIN_STATE_CHANGE(action='activate', supervisor_id=self._plugin_id, state=str(self._state))
        return self.get_state()

    def make_provision(self) -> str:
        if isinstance(self._state, ErrorState):
            self._state = ProvisioningState()
        else:
            raise ERROR_PLUGIN_STATE_CHANGE(action='make_provision', supervisor_id=self._plugin_id, state=str(self._state))
        return self.get_state()

    def make_reprovision(self) -> str:
        if isinstance(self._state, (ErrorState, ActiveState)):
            self._state = ReprovisioningState()
        else:
            raise ERROR_PLUGIN_STATE_CHANGE(action='make_reprovision', supervisor_id=self._plugin_id,
                                            state=str(self._state))
        return self.get_state()

    def change_to_error(self) -> str:
        self._state = ErrorState()
        return self.get_state()

    def get_state(self) -> str:
        return str(self._state)



