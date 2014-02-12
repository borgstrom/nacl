import os

from salt.utils.odict import OrderedDict
from salt.utils.templates import py

from salttesting import TestCase
from salttesting.helpers import ensure_in_syspath

ensure_in_syspath('../')


def tmpl(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", name)


class NaCITests(TestCase):
    def test_naci_run(self):
        ret = py(tmpl('basic.py'), string=True)
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['data'], OrderedDict([
            ('/tmp', ('/tmp', {
                'file.managed': [
                    {'group': 'root'},
                    {'mode': '1777'},
                    {'owner': 'root'}
                ]
            })),
        ]))
