from unittest import TestCase

from naci.state import StateFactory, State, default_registry

File = StateFactory('file')

pydmesg_expected = ('/usr/local/bin/pydmesg', {
    'file.managed': [
        {'group': 'root'},
        {'mode': '0755'},
        {'require': [{'file': '/usr/local/bin'}]},
        {'source': 'salt://debian/files/pydmesg.py'},
        {'user': 'root'},
    ]
})
pydmesg_kwargs = dict(user='root', group='root', mode='0755',
                      source='salt://debian/files/pydmesg.py',
                      require=File('/usr/local/bin'))


class StateTests(TestCase):
    def setUp(self):
        default_registry.empty()

    def test_serialization(self):
        f = State('/usr/local/bin/pydmesg', 'file.managed', **pydmesg_kwargs)

        self.assertEqual(f(), pydmesg_expected)

    def test_factory_serialization(self):
        File.managed('/usr/local/bin/pydmesg', **pydmesg_kwargs)

        self.assertEqual(
            default_registry.states['/usr/local/bin/pydmesg'](),
            pydmesg_expected
        )
