DATABASES = {
    'default': {
        'db': 'plugin',
        'host': 'localhost',
        'port': 27017,
        'username': 'plugin',
        'password': ''
    }
}

CACHES = {
    'default': {},
    'local': {
        'backend': 'spaceone.core.cache.local_cache.LocalCache',
        'max_size': 128,
        'ttl': 86400
    }
}

CONNECTORS = {
    'IdentityConnector': {
        'endpoint': {
            'v1': 'grpc://identity:50051'
        }
    },
    'pluginConnector': {
    },
    'RepositoryConnector': {
        'endpoint': {
            'v1': 'grpc://repository:50051'
        }
    }
}

HANDLERS = {
}

ENDPOINTS = {
}

LOG = {
}
