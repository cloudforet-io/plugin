from spaceone.core.manager import BaseManager
# from spaceone.plugin.connector.identity_connector import IdentityConnector
from spaceone.core.connector.space_connector import SpaceConnector

class IdentityManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identity_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='identity')

    def list_domains(self, query):
        # identity_conn: IdentityConnector = self.locator.get_connector('IdentityConnector')
        # return identity_conn.list_domains(query)
        return self.identity_connector.dispatch('Domain.list', query)
