#!py

from naci import run
from naci.auto import *

File.managed('/tmp', mode='1777', owner='root', group='root')
