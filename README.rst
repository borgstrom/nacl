NaCI
====
NaCI is an alternative interface for building complex SaltStack_ states using
pure Python instead of the default YAML renderer. It is **not** a renderer, but
rather a standard Python package that you use in conjunction with the standard
``#!py`` renderer that's built into SaltStack_.


Project Motivation
------------------
The default YAML renderer that SaltStack_ uses is the best starting point for
building state data. It's easy to write & grok syntax make it ideal for getting
your feet wet. As a state tree grows the combination of Jinja_ with YAML mean
that you get to add some programmatic generation of your state tree to reduce
repetitive tasks through the use macros and other built in Jinja_ goodness.

Then your state tree starts to get bigger, and bigger, and bigger. Soon you end
up with hundreds of YAML files, some of which a hundreds if not thousands of
lines big. Soon you have giant, very complex macros, state & pillar data that
becomes harder to grok and even harder to bring new team members up to speed
on.

As a Python hacker my initial reaction to my growing state tree was simply to
reach for the built-in ``#!py`` renderer. While you do gain the power of Python
it also comes with a huge amount of responsibility in terms of getting Salt's,
quite complex, data structure right. I also didn't like that I had to define a
``run()`` function in each file I built. It felt very un-pragmatic to me, but
I do understand the architectural reasons for doing it this way.

So I set about to create a more convenient way to write state data using pure
Python...


What about pydsl?
^^^^^^^^^^^^^^^^^
It's true, SaltStack_ ships with a renderer named ``#!pydsl`` built in. But,
it's the personal preference of the author of NaCI that DSL's are things that
are rarely the right solution to a problem and that the ``#!pydsl`` renderer
specifically is actually more cumbersome to write state data in. I tried it,
and I didn't like it (at all, sorry pydsl author...)


Usage
-----
Great. Now how do we use NaCI?

As mentioned it is not a SaltStack_ renderer, which means that it is not
included by default when you install Salt (maybe some day). Instead NaCI is
a full standalone Python package available on the cheese shop (PyPI). This
means that to install it you can simply install it globally using
``easy_install``::

    sudo easy_install naci

NaCI needs to be installed globally so that salt can find it when your state
files are being rendered.

Now, let's take a look at how you use NaCI in a state file. Here's a quick
example that ensures the ``/tmp`` directory is in the correct state::

    #!py
    from naci.run import run
    from naci.auto import *

    File.managed("/tmp", user='root', group='root', mode='1777')

Nice and Pythonic!

Here NaCI provides a ``run`` function that you simply import and it will
handle all of the integration with Salt. Next we import everything from the
``naci.auto`` module. This module takes care of creating an object for each
of the available states on the minion. Each state is represented by an object
that is the capitalized version of it's name (ie. ``File``, ``Service``,
``User``, etc), and these objects have a magic method that exposes all of the
available state functions (ie. ``File.managed``).

State Factories
^^^^^^^^^^^^^^^
Use the ``naci.auto`` module provides you a convenient way to get access to
all of the available SaltStack_ states. You can also generate these interfaces
directly yourself if you don't want to incur the overhead of auto-discovering
the available states::

    #!py
    from naci.run import run
    from naci.state import StateFactory

    File = StateFactory("file")
    Pkg = StateFactory("pkg")
    Service = StateFactory("service")

    ...

Context Managers and requisites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
How about something a little more complex. Here we're going to get into the
core of what makes NaCI the best way to write states::

    #!py
    from naci.run import run
    from naci.auto import *

    nginx = Pkg.installed("nginx")
    with nginx:
        Service.running("nginx", enable=True)
        with Service("nginx", "watch_in"):
            File.managed("/etc/nginx/conf.d/mysite.conf",
                         owner='root', group='root', mode='0444',
                         source='salt://nginx/mysite.conf')


The objects that are returned from each of the magic method calls are setup to
be used a Python context managers (``with``) and when you use them as such all
declarations made within the scope will **automatically** use the enclosing
state as a requisite! (See below for more info on direct requisite usage).

The above could have also been written use direct requisite statements as::

    #!py
    from naci.run import run
    from naci.auto import *

    Pkg.installed("nginx")
    Service.running("nginx", enable=True, require=Pkg("nginx"))
    File.managed("/etc/nginx/conf.d/mysite.conf",
                 owner='root', group='root', mode='0444',
                 source='salt://nginx/mysite.conf',
                 watch_in=Service("nginx"))

You can use the direct requisite statement for referencing states that are
generated outside of the current file::

    #!py
    from naci.run import run
    from naci.auto import *

    # some-other-package is defined else where
    Pkg.installed("nginx", require=Pkg("some-other-package"))

The last thing that direct requisites provide is the ability to select which
of the SaltStack_ requisites you want to use (require, require_in, watch,
watch_in, use & use_in) when using the requisite as a context manager::

    #!py
    from naci.run import run
    from naci.auto import *

    with Service("my-service", "watch_in"):
        ...

TODO
----

* Get the package up on PyPI
* Allow for better imports so that authors building state data can ship
  reusable code in the form of their own modules without needed to muck with
  the system path themselves.

.. _SaltStack: http://saltstack.org/
.. _Jinja: http://jinja.poco.org/
