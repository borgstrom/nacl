"""
The auto module builds state factories for all of the modules that the Salt
SMinion class reports as being available

TODO: This needs more testing and maybe a rewrite
"""

from nacl.state import StateFactory

from salt.config import minion_config
from salt.loader import states
from salt.minion import SMinion

_config = minion_config(None)
_config['file_client'] = 'local'
_minion = SMinion(_config)
_states = states(_config, _minion.functions)

# build our list of states and functions
_st_funcs = {}
for func in _states:
    (mod, func) = func.split(".")
    if mod not in _st_funcs:
        _st_funcs[mod] = []
    _st_funcs[mod].append(func)

# prepare for export
__all__ = []
for mod in _st_funcs:
    _st_funcs[mod].sort()
    mod_upper = mod.capitalize()
    mod_cmd = "%s = StateFactory('%s', valid_funcs=['%s'])" % (
        mod_upper, mod,
        "','".join(_st_funcs[mod])
    )
    exec(mod_cmd)
    __all__.append(mod_upper)
