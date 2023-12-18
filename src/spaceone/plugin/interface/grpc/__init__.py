from spaceone.core.pygrpc.server import GRPCServer
from spaceone.plugin.interface.grpc.plugin import Plugin
from spaceone.plugin.interface.grpc.supervisor import Supervisor

__all__ = ["app"]

app = GRPCServer()
app.add_service(Plugin)
app.add_service(Supervisor)
