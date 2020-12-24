from spaceone.core.manager import BaseManager
from spaceone.plugin.connector.identity_connector import IdentityConnector


class IdentityManager(BaseManager):

    def list_domains(self, query):
        identity_conn: IdentityConnector = self.locator.get_connector('IdentityConnector')
        return identity_conn.list_domains(query)
