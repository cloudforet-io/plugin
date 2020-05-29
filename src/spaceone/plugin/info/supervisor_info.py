# -*- coding: utf-8 -*-
import functools

from spaceone.api.plugin.v1 import supervisor_pb2

from spaceone.core.pygrpc.message_type import *

__all__ = ['SupervisorInfo', 'SupervisorsInfo']


def SupervisorInfo(supervisor_vo):
    info = {}
    info['supervisor_id'] = supervisor_vo.supervisor_id
    info['name'] = supervisor_vo.name
    info['hostname'] = supervisor_vo.hostname
    info['state'] = supervisor_vo.state
    info['is_public'] = supervisor_vo.is_public
    info['labels'] = change_struct_type(supervisor_vo.labels)
    info['tags'] = change_struct_type(supervisor_vo.tags)
    info['created_at'] = change_timestamp_type(supervisor_vo.created_at)
    info['updated_at'] = change_timestamp_type(supervisor_vo.updated_at)
    info['domain_id'] = supervisor_vo.domain_id

    return supervisor_pb2.SupervisorInfo(**info)


def SupervisorsInfo(role_vos, total_count):
    results = list(map(functools.partial(SupervisorInfo), role_vos))

    return supervisor_pb2.SupervisorsInfo(results=results, total_count=total_count)
