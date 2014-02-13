import os

from salt.utils.odict import OrderedDict
from salt.utils.templates import py

from salttesting import TestCase
from salttesting.helpers import ensure_in_syspath

ensure_in_syspath('../')

from nacl.state import default_registry, InvalidFunction


def tmpl(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", name)


class NaClTests(TestCase):
    def test_nacl_run(self):
        ret = py(tmpl('basic.py'), string=True)
        self.assertEqual(ret['result'], True)
        self.assertEqual(ret['data'], OrderedDict([
            ('/tmp', {
                'file.managed': [
                    {'group': 'root'},
                    {'mode': '1777'},
                    {'owner': 'root'}
                ]
            }),
        ]))

        self.assertEqual(default_registry.states, OrderedDict())

    def test_invalid_function(self):
        def _test():
            py(tmpl('invalid_function.py'), string=True)
        self.assertRaises(InvalidFunction, _test)
