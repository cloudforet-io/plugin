import functools
from spaceone.api.core.v1 import tag_pb2
from spaceone.api.plugin.v1 import supervisor_pb2
from spaceone.core.pygrpc.message_type import *

__all__ = ['SupervisorInfo', 'SupervisorsInfo']


def SupervisorInfo(supervisor_vo):
    info = {
        'supervisor_id': supervisor_vo.supervisor_id,
        'name': supervisor_vo.name,
        'hostname': supervisor_vo.hostname,
        'state': supervisor_vo.state,
        'is_public': supervisor_vo.is_public,
        'labels': change_struct_type(supervisor_vo.labels),
        'created_at': change_timestamp_type(supervisor_vo.created_at),
        'updated_at': change_timestamp_type(supervisor_vo.updated_at),
        'domain_id': supervisor_vo.domain_id
    }

    if supervisor_vo.tags:
        info['tags'] = [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in supervisor_vo.tags]

    return supervisor_pb2.SupervisorInfo(**info)


def SupervisorsInfo(role_vos, total_count):
    results = list(map(functools.partial(SupervisorInfo), role_vos))

    return supervisor_pb2.SupervisorsInfo(results=results, total_count=total_count)
