This project has been merged directly into Salt
===============================================
I've merged this project directly into Salt: https://github.com/saltstack/salt/pull/10517

No more work will be done on this repository, it will remain here for
prosperity.

----

NaCl
====
**We're definitely talking about Salt**

NaCl is an alternative interface for building complex SaltStack_ states using
pure Python instead of the default YAML renderer. The implementation does
nothing more than provide your state files with access to a number of objects
that provide a very nice & clean interface for generating the complex state
data.

Background
----------
The default YAML renderer that SaltStack_ uses is the best starting point for
building state data. It's easy to understand syntax makes it ideal for getting
your feet wet. As a state tree grows the combination of Jinja_ with YAML means
that you get to add some programmatic generation of your state tree to reduce
repetitive tasks through the use macros and other built in Jinja_ goodness.

Then your state tree starts to get bigger, and bigger, and bigger. Soon you end
up with hundreds of YAML files, some of which are hundreds of lines long and
contain complex macros using custom pillar data. This combination becomes
harder to grok and even harder to bring new team members up to speed on.

NaCl aims to allow your complex states to be expressed in an entirely
programatic way that still maintains the feeling of simplicity that the YAML
interface provides.

Installation
------------
1. Clone this repository on to each minion (yes, I know. this is a pain that
   I hope to have resolved shortly)::

    git clone https://github.com/borgstrom/nacl.git

2. Install nacl as root on each minion::

    cd nacl
    sudo python setup.py install

3. On the master prepare the renderer for distribution::

    mkdir /srv/salt/_renderers
    curl -o /srv/salt/_renderers/nacl_renderer.py https://raw2.github.com/borgstrom/nacl/master/salt_renderer/nacl_renderer.py

   This assumes that your salt file roots contain the default location of
   ``/srv/salt``, adjust the paths if you're using a different location. The
   salt master will now distribute the renderer to each minion.

Usage
-----
Let's take a look at how you use NaCl in a state file. Here's a quick example
that ensures the ``/tmp`` directory is in the correct state::

    #!nacl

    File.managed("/tmp", user='root', group='root', mode='1777')

Nice and Pythonic!

By using the "shebang" syntax to switch to the NaCl renderer we can now write
our state data using an object based interface that should feel at home to
python developers. You can import any module and do anything that you'd like
(with caution, importing sqlalchemy, django or other large frameworks has not
been tested yet). Using the NaCl renderer is exactly the same as using the
built-in Python renderer with the exception that the NaCl renderer takes care
of creating an object for each of the available states on the minion. Each
state is represented by an object that is the capitalized version of it's name
(ie. ``File``, ``Service``, ``User``, etc), and these objects expose all of
their available state functions (ie. ``File.managed``,  ``Service.running``,
etc).


Context Managers and requisites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
How about something a little more complex. Here we're going to get into the
core of what makes NaCl the best way to write states::

    #!nacl

    with Pkg.installed("nginx"):
        Service.running("nginx", enable=True)

        with Service("nginx", "watch_in"):
            File.managed("/etc/nginx/conf.d/mysite.conf",
                         owner='root', group='root', mode='0444',
                         source='salt://nginx/mysite.conf')


The objects that are returned from each of the magic method calls are setup to
be used a Python context managers (``with``) and when you use them as such all
declarations made within the scope will **automatically** use the enclosing
state as a requisite!

The above could have also been written use direct requisite statements as::

    #!nacl

    Pkg.installed("nginx")
    Service.running("nginx", enable=True, require=Pkg("nginx"))
    File.managed("/etc/nginx/conf.d/mysite.conf",
                 owner='root', group='root', mode='0444',
                 source='salt://nginx/mysite.conf',
                 watch_in=Service("nginx"))

You can use the direct requisite statement for referencing states that are
generated outside of the current file::

    #!nacl

    # some-other-package is defined in some other state file
    Pkg.installed("nginx", require=Pkg("some-other-package"))

The last thing that direct requisites provide is the ability to select which
of the SaltStack_ requisites you want to use (require, require_in, watch,
watch_in, use & use_in) when using the requisite as a context manager::

    #!nacl

    with Service("my-service", "watch_in"):
        ...

The above example would cause all declarations inside the scope of the context
manager to automatically have their ``watch_in`` set to
``Service("my-service")``.

TODO
----

* Try to integrate directly with Salt and create a pull request to get NaCl
  included in the core distribution.

.. _SaltStack: http://saltstack.org/
.. _Jinja: http://jinja.pocoo.org/
