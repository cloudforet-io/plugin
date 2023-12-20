DATABASE_AUTO_CREATE_INDEX = True
DATABASES = {
    "default": {
        "db": "plugin",
        "host": "localhost",
        "port": 27017,
        "username": "plugin",
        "password": "",
    }
}

CACHES = {
    "default": {},
    "local": {
        "backend": "spaceone.core.cache.local_cache.LocalCache",
        "max_size": 128,
        "ttl": 300,
    },
}

CONNECTORS = {
    "IdentityConnector": {"endpoint": {"v1": "grpc://identity:50051"}},
    "pluginConnector": {},
    "RepositoryConnector": {"endpoint": {"v1": "grpc://repository:50051"}},
    "SpaceConnector": {
        "backend": "spaceone.core.connector.space_connector:SpaceConnector",
        "endpoints": {
            "identity": "grpc://identity:50051",
            "repository": "grpc://repository:50051",
            "secret": "grpc://secret:50051",
        },
    },
}

HANDLERS = {}

ENDPOINTS = {}

LOG = {}

QUEUES = {}
SCHEDULERS = {}
WORKERS = {}
TOKEN = ""
TOKEN_INFO = {}
