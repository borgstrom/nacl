from salt.utils.odict import OrderedDict


REQUISITES = ('require', 'watch', 'use', 'require_in', 'watch_in', 'use_in')


class StateException(Exception):
    pass


class DuplicateState(StateException):
    pass


class InvalidFunction(StateException):
    pass


class StateRegistry(object):
    """
    The StateRegistry holds all of the states that have been created.
    """
    def __init__(self):
        self.empty()

    def empty(self):
        self.states = OrderedDict()
        self.requisites = []

    def salt_run(self):
        states = OrderedDict([
            (name, state())
            for name, state in self.states.iteritems()
        ])

        self.empty()

        return states

    def add(self, name, state):
        if name in self.states:
            raise DuplicateState("A state named '%s' already exists" % name)

        # if we have requisites in our stack then add them to the state
        if len(self.requisites) > 0:
            for req in self.requisites:
                if req.requisite not in state.kwargs:
                    state.kwargs[req.requisite] = []
                state.kwargs[req.requisite].append(req())

        self.states[name] = state

    def push_requisite(self, requisite):
        self.requisites.append(requisite)

    def pop_requisite(self):
        del self.requisites[-1]

default_registry = StateRegistry()


class StateRequisite(object):
    def __init__(self, requisite, module, name, registry=None):
        self.requisite = requisite
        self.module = module
        self.name = name

        if registry is None:
            self.registry = default_registry
        else:
            self.registry = registry

    def __call__(self):
        return {self.module: self.name}

    def __enter__(self):
        self.registry.push_requisite(self)

    def __exit__(self, type, value, traceback):
        self.registry.pop_requisite()


class StateFactory(object):
    """
    The StateFactory is used to generate new States through a natural syntax

    It is used by initializing it with the name of the salt module::

        File = StateFactory("file")

    Any attribute accessed on the instance returned by StateFactory is a lambda
    that is a short cut for generating State objects::

        File.managed('/path/', owner='root', group='root')

    The kwargs are passed through to the State object
    """
    def __init__(self, module, registry=None, valid_funcs=[]):
        self.module = module
        self.valid_funcs = valid_funcs
        if registry is not None:
            self.registry = registry
        else:
            self.registry = default_registry

    def __getattr__(self, func):
        if len(self.valid_funcs) > 0 and func not in self.valid_funcs:
            raise InvalidFunction("The function '%s' does not exist in the "
                                  "StateFactory for '%s'" % (func, self.module))

        def make_state(name, **kwargs):
            return State(
                name,
                self.module,
                func,
                registry=self.registry,
                **kwargs
            )
        return make_state

    def __call__(self, name, requisite='require'):
        """
        When an object is called it is being used as a requisite
        """
        # return the correct data structure for the requisite
        return StateRequisite(requisite, self.module, name,
                              registry=self.registry)


class State(object):
    """
    This represents a single item in the state tree

    The name is the name of the state, the func is the full name of the salt
    state (ie. file.managed). All the keyword args you pass in become the
    properties of your state.

    The registry is where the state should be stored. It is optional and will
    use the default registry if not specified.
    """

    def __init__(self, name, module, func, registry=None, **kwargs):
        self.name = name
        self.module = module
        self.func = func
        self.kwargs = kwargs

        self.requisite = StateRequisite('require', self.module, self.name,
                                        registry=registry)

        if registry is None:
            self.registry = default_registry
        else:
            self.registry = registry
        self.registry.add(name, self)

    @property
    def attrs(self):
        kwargs = self.kwargs

        # handle our requisites
        for attr in REQUISITES:
            if attr in kwargs:
                # our requisites should all be lists, but when you only have a
                # single item it's more convenient to provide it without
                # wrapping it in a list. transform them into a list
                if not isinstance(kwargs[attr], list):
                    kwargs[attr] = [kwargs[attr]]

                # rebuild the requisite list transforming any of the actual
                # StateRequisite objects into their representative dict
                kwargs[attr] = [
                    req() if isinstance(req, StateRequisite) else req
                    for req in kwargs[attr]
                ]

        # build our attrs from kwargs. we sort the kwargs by key so that we
        # have consistent ordering for tests
        return [
            {k: kwargs[k]}
            for k in sorted(kwargs.iterkeys())
        ]

    @property
    def full_func(self):
        return "%s.%s" % (self.module, self.func)

    def __str__(self):
        return "%s = %s:%s" % (self.name, self.full_func, self.attrs)

    def __call__(self):
        return {
            self.full_func: self.attrs
        }

    def __enter__(self):
        self.registry.push_requisite(self.requisite)

    def __exit__(self, type, value, traceback):
        self.registry.pop_requisite()
