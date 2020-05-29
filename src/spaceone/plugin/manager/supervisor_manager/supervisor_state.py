# -*- coding: utf-8 -*-

import abc

from spaceone.core.manager import BaseManager
from spaceone.plugin.error.supervisor import ERROR_SUPERVISOR_STATE

__all__ = [
    'SupervisorState',
    'PendingState',
    'EnabledState',
    'DisabledState',
    'DisconnectedState',
    'SupervisorStateMachine'
]


PENDING =   'PENDING'
DISABLED =  'DISABLED'
ENABLED =   'ENABLED'
DISCONNECTED = 'DISCONNECTED'

class SupervisorState(metaclass=abc.ABCMeta):

    def __init__(self):
        self.handle()

    @abc.abstractmethod
    def handle(self):
        pass


class PendingState(SupervisorState):

    def handle(self):
        # TODO: Send notification? maybe?
        pass

    def __str__(self):
        return PENDING


class EnabledState(SupervisorState):

    def handle(self):
        # TODO: add this supervisor_id to watching list.
        pass

    def __str__(self):
        return ENABLED


class DisabledState(SupervisorState):

    def handle(self):
        pass

    def __str__(self):
        return DISABLED


class DisconnectedState(SupervisorState):

    def handle(self):
        # TODO: Send notification? maybe?
        pass

    def __str__(self):
        return DISCONNECTED

STATE_DIC = {
    'PENDING'   : PendingState(),
    'DISABLED'  : DisabledState(),
    'ENABLED'   : EnabledState(),
    'DISCONNECTED': DisconnectedState()
}

class SupervisorStateMachine():

    def __init__(self, supervisor_id, state):
        self.supervisor_id = supervisor_id
        self._state = STATE_DIC[state]

    def register(self):
        """
        The register action enables state from only 'PENDING'.
        """
        if isinstance(self._state, PendingState):
            self._state = EnabledState()
        else:
            raise ERROR_SUPERVISOR_STATE(action='register', supervisor_id=self.supervisor_id, state=str(self._state))

    def enable(self):
        if isinstance(self._state, (DisabledState, DisconnectedState)):
            self._state = EnabledState()
        elif isinstance(self._state, EnabledState):
            pass
        else:
            raise ERROR_SUPERVISOR_STATE(action='enable', supervisor_id=self.supervisor_id, state=str(self._state))

    def disable(self):
        if isinstance(self._state, (EnabledState, DisconnectedState)):
            self._state = DisabledState()
        elif isinstance(self._state, DisabledState):
            pass
        else:
            raise ERROR_SUPERVISOR_STATE(action='disable', supervisor_id=self.supervisor_id, state=str(self._state))

    def get_state(self):
        return str(self._state)


