import logging
from typing import Union

from spaceone.core.cache import cacheable
from spaceone.core.manager import BaseManager
from spaceone.plugin.error import *
from spaceone.core.connector.space_connector import SpaceConnector

_LOGGER = logging.getLogger(__name__)


class RepositoryManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repo_connector: SpaceConnector = self.locator.get_connector(
            SpaceConnector, service="repository"
        )

    def get_plugin(self, plugin_id: str, domain_id: str, token: str) -> dict:
        return self.repo_connector.dispatch(
            "Plugin.get", {"plugin_id": plugin_id}, token=token, x_domain_id=domain_id
        )

    def check_plugin_version(
        self, plugin_id: str, version: str, token: str, domain_id: str
    ) -> None:
        response = self.repo_connector.dispatch(
            "Plugin.get_versions",
            {"plugin_id": plugin_id},
            token=token,
            x_domain_id=domain_id,
        )

        if version not in response.get("results", []):
            raise ERROR_INVALID_PLUGIN_VERSION(plugin_id=plugin_id, version=version)

    @cacheable(key="plugin-latest-version:{domain_id}:{plugin_id}", expire=600)
    def get_plugin_latest_version(
        self, plugin_id: str, domain_id: str, token: str
    ) -> Union[str, None]:
        response = self.repo_connector.dispatch(
            "Plugin.get_versions",
            {"plugin_id": plugin_id},
            token=token,
            x_domain_id=domain_id,
        )
        versions = response.get("results", [])
        if versions:
            return versions[0]
        else:
            return None
