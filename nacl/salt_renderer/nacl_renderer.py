import logging

try:
    from nacl.auto import *
    from nacl.state import default_registry
    HAS_NACL = True
except ImportError:
    HAS_NACL = False

__virtualname__ = 'nacl'
log = logging.getLogger(__virtualname__)


def __virtual__():
    if HAS_NACL:
        log.info("NaCl renderer available")
        return __virtualname__
    return False


def render(template, saltenv='base', sls='',
           tmplpath=None, rendered_sls=None, **kwargs):
    pillar = __pillar__
    grains = __grains__
    salt = __salt__

    exec(template.read())
    return default_registry.salt_data()
