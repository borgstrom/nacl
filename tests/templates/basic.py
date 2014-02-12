from naci import run
from naci.state import StateFactory

File = StateFactory('file')

File.managed('/tmp', mode='1777', owner='root', group='root')
