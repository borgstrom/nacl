"""
The auto module builds state factories for all of the modules that the Salt
SMinion class reports as being available

TODO: This needs more testing and maybe a rewrite
"""

from naci.state import StateFactory

from salt.config import minion_config
from salt.minion import SMinion

_config = minion_config(None)
_config['file_client'] = 'local'
_minion = SMinion(_config)

# prepare for export
__all__ = []
for func in _minion.functions:
    (mod, name) = func.split(".")
    mod_upper = mod.capitalize()

    exec("%s = StateFactory('%s')" % (mod_upper, mod))

    __all__.append(mod_upper)
