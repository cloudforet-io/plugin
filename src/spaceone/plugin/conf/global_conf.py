DATABASE_AUTO_CREATE_INDEX = True
DATABASE_CASE_INSENSITIVE_INDEX = False
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
        'ttl': 300
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

QUEUES = {}
SCHEDULERS = {}
WORKERS = {}
TOKEN = ""
TOKEN_INFO = {}

