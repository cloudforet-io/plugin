import functools
from spaceone.api.plugin.v1 import supervisor_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils

__all__ = ['SupervisorInfo', 'SupervisorsInfo']


def SupervisorInfo(supervisor_vo):
    info = {
        'supervisor_id': supervisor_vo.supervisor_id,
        'name': supervisor_vo.name,
        'hostname': supervisor_vo.hostname,
        'state': supervisor_vo.state,
        'is_public': supervisor_vo.is_public,
        'labels': change_struct_type(supervisor_vo.labels),
        'created_at': utils.datetime_to_iso8601(supervisor_vo.created_at),
        'updated_at': utils.datetime_to_iso8601(supervisor_vo.updated_at),
        'domain_id': supervisor_vo.domain_id
    }

    if supervisor_vo.tags:
        info['tags'] = change_struct_type(utils.tags_to_dict(supervisor_vo.tags))

    return supervisor_pb2.SupervisorInfo(**info)


def SupervisorsInfo(role_vos, total_count):
    results = list(map(functools.partial(SupervisorInfo), role_vos))

    return supervisor_pb2.SupervisorsInfo(results=results, total_count=total_count)
