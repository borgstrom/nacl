from unittest import TestCase

from naci.state import StateFactory, State, default_registry

pydmesg_expected = ('/usr/local/bin/pydmesg', {
    'file.managed': [
        {'group': 'root'},
        {'mode': '0755'},
        {'source': 'salt://debian/files/pydmesg.py'},
        {'user': 'root'},
    ]
})
pydmesg_kwargs = dict(user='root', group='root', mode='0755',
                      source='salt://debian/files/pydmesg.py')


class StateTests(TestCase):
    def setUp(self):
        default_registry.empty()

    def test_serialization(self):
        f = State('/usr/local/bin/pydmesg', 'file.managed', **pydmesg_kwargs)

        self.assertEqual(f.serialize(), pydmesg_expected)

    def test_factory_serialization(self):
        File = StateFactory('file')
        File.managed('/usr/local/bin/pydmesg',
                     user='root', group='root', mode='0755',
                     source='salt://debian/files/pydmesg.py')

        self.assertEqual(
            default_registry.states['/usr/local/bin/pydmesg'].serialize(),
            pydmesg_expected
        )
