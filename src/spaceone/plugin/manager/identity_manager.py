from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector


class IdentityManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identity_connector: SpaceConnector = self.locator.get_connector(
            SpaceConnector, service="identity"
        )

    def list_domains(self, query):
        return self.identity_connector.dispatch("Domain.list", {"query": query})
