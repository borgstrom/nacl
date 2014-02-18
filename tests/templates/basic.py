#!py

from nacl.auto import *

File.managed('/tmp', mode='1777', owner='root', group='root')
