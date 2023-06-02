from spaceone.core.error import *


class ERROR_PLUGIN_NOT_FOUND(ERROR_BASE):
    _message = 'Plugin does not exist. (plugin_id = {plugin_id})'


class ERROR_INVALID_PLUGIN_VERSION(ERROR_INVALID_ARGUMENT):
    _message = 'version:{version} of {plugin_id} does not exist'


class ERROR_INSTALL_PLUGIN_TIMEOUT(ERROR_BASE):
    _message = 'install plugin is failed by timeout, supervisor_id: {supervisor_id}, plugin_id: {plugin_id}, version: {version}'


class ERROR_PLUGIN_FAILURE(ERROR_BASE):
    _message = 'install plugin is failure state, supervisor_id: {supervisor_id}, plugin_id: {plugin_id}, version: {version}'


class ERROR_PLUGIN_IMAGE_NOT_FOUND(ERROR_BASE):
    _message = 'Plugin image does not exist. (plugin_id = {plugin_id})'


class ERROR_PLUGIN_ENDPOINT_NOT_FOUND(ERROR_BASE):
    _message = 'Plugin endpoint is not existed. (plugin_id = {plugin_id})'
