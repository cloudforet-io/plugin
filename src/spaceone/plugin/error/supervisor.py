# -*- coding: utf-8 -*-

from spaceone.core.error import ERROR_BASE


class ERROR_REPOSITORY_BACKEND(ERROR_BASE):
    _message = 'Repository backend has problem. ({host})'


class ERROR_SUPERVISOR_STATE(ERROR_BASE):
    _message = 'This "{action}" cannot be processed. (supervisor_id = {supervisor_id}, state = {state})'


class ERROR_SUPERVISOR_UPDATE(ERROR_BASE):
    _message = 'This field is not updatable over "update" api. (key = {key})'


class ERROR_PLUGIN_STATE_CHANGE(ERROR_BASE):
    _message = 'This "{action}" cannot be processed. (plugin_id = {supervisor_id}, state = {state})'


class ERROR_NO_POSSIBLE_SUPERVISOR(ERROR_BASE):
    _message = 'There is no supervisor to run plugin. params: {params}'


class ERROR_NOT_SUPPORT_RECOVER_PLUGIN(ERROR_BASE):
    _message = 'recover_plugin is not supported. supervisor_id: {supervisor_id}'


class ERROR_NOT_SUPPORT_LIST_PLUGINS(ERROR_BASE):
    _message = 'This supervisor does not support list plugins: {supervisor_id}'


class ERROR_INSTALLED_PLUGIN_EXIST(ERROR_BASE): 
    _message = 'Installed plugins exist, {supervisor_id}'
