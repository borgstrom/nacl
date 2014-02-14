from .state import default_registry


def run():
    return default_registry.salt_data()
