from spaceone.api.plugin.v1 import supervisor_pb2, supervisor_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Supervisor(BaseAPI, supervisor_pb2_grpc.SupervisorServicer):

    pb2 = supervisor_pb2
    pb2_grpc = supervisor_pb2_grpc

    def publish(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            data = supervisor_svc.publish(params)
            return self.locator.get_info('SupervisorInfo', data)

    def register(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            data = supervisor_svc.register(params)
            return self.locator.get_info('SupervisorInfo', data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            data = supervisor_svc.update(params)
            return self.locator.get_info('SupervisorInfo', data)


    def deregister(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            supervisor_svc.deregister(params)
            return self.locator.get_info('EmptyInfo')

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            data = supervisor_svc.enable(params)
            return self.locator.get_info('SupervisorInfo', data)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            data = supervisor_svc.disable(params)
            return self.locator.get_info('SupervisorInfo', data)

    def recover_plugin(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            data = supervisor_svc.recover_plugin(params)
            return self.locator.get_info('PluginInfo', data)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            data = supervisor_svc.get(params)
            return self.locator.get_info('SupervisorInfo', data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            supervisors_vo, total_count = supervisor_svc.list_supervisors(params)
            return self.locator.get_info('SupervisorsInfo', supervisors_vo, total_count)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            return self.locator.get_info('StatisticsInfo', supervisor_svc.stat(params))

    def list_plugins(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('SupervisorService', metadata) as supervisor_svc:
            plugins_vo, total_count = supervisor_svc.list_plugins(params)
            return self.locator.get_info('PluginsInfo', plugins_vo, total_count)
