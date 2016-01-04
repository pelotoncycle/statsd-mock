statsd-mock
============

.. image:: https://travis-ci.org/tarzan0820/statsd-mock.png?branch=master
    :target: https://travis-ci.org/tarzan0820/statsd-mock

Based entirely on - `studio-ousia/gevent-statsd-moc <https://github.com/studio-ousia/gevent-statsd-mock>`_ 
with `python-statsd <https://github.com/WoLpH/python-statsd>`_ dependency changed to `pystatsd <https://github.com/jsocol/pystatsd>`_
and gevent.server.DatagramServer used to handle the server portion

Installation
------------

.. code-block:: bash

    $ pip install mock-statd


Basic Usage
-----------

In this sample we use `pystatsd <https://github.com/jsocol/pystatsd>`_ for client library

.. code-block:: python

    >>> from statsdmock import StatsdMockServer
    >>> server = StatsdMockServer()
    >>> server.start()
    >>> import statsd
    >>> c = statsd.StatsClient(prefix='bigtag')
    >>> c.gauge('subtag', 10)
    >>> server.wait('bigtag.subtag', n=1)
    >>> data = list(server.metrics['bigtag.subtag'])
    >>> assert data[0] == {'value': '10', 'type': 'gauge', 'rate': 1.0, 'timestamp': None}
    >>> server.stop()
    >>> del server

