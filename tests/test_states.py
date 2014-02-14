from unittest import TestCase

from salt.utils.odict import OrderedDict

from nacl.state import StateFactory, State, default_registry

File = StateFactory('file')

pydmesg_expected = {
    'file.managed': [
        {'group': 'root'},
        {'mode': '0755'},
        {'require': [{'file': '/usr/local/bin'}]},
        {'source': 'salt://debian/files/pydmesg.py'},
        {'user': 'root'},
    ]
}
pydmesg_salt_expected = OrderedDict([('/usr/local/bin/pydmesg', pydmesg_expected)])
pydmesg_kwargs = dict(user='root', group='root', mode='0755',
                      source='salt://debian/files/pydmesg.py')


class StateTests(TestCase):
    def setUp(self):
        default_registry.empty()

    def test_serialization(self):
        f = State('/usr/local/bin/pydmesg', 'file', 'managed',
                  require=File('/usr/local/bin'),
                  **pydmesg_kwargs)

        self.assertEqual(f(), pydmesg_expected)

    def test_factory_serialization(self):
        File.managed('/usr/local/bin/pydmesg',
                     require=File('/usr/local/bin'),
                     **pydmesg_kwargs)

        self.assertEqual(
            default_registry.states['/usr/local/bin/pydmesg'](),
            pydmesg_expected
        )

    def test_context_manager(self):
        with File('/usr/local/bin'):
            pydmesg = File.managed('/usr/local/bin/pydmesg', **pydmesg_kwargs)

            self.assertEqual(
                default_registry.states['/usr/local/bin/pydmesg'](),
                pydmesg_expected
            )

            with pydmesg:
                File.managed('/tmp/something', owner='root')

                self.assertEqual(
                    default_registry.states['/tmp/something'](),
                    {
                        'file.managed': [
                            {'owner': 'root'},
                            {'require': [
                                {'file': '/usr/local/bin'},
                                {'file': '/usr/local/bin/pydmesg'}
                            ]},
                        ]
                    }
                )

    def test_salt_data(self):
        File.managed('/usr/local/bin/pydmesg',
                     require=File('/usr/local/bin'),
                     **pydmesg_kwargs)

        self.assertEqual(
            default_registry.states['/usr/local/bin/pydmesg'](),
            pydmesg_expected
        )

        self.assertEqual(
            default_registry.salt_data(),
            pydmesg_salt_expected
        )

        self.assertEqual(
            default_registry.states,
            OrderedDict()
        )
