gevent-statsd-mock
==================

.. image:: https://travis-ci.org/studio-ousia/gevent-statsd-mock.png?branch=master
    :target: https://travis-ci.org/studio-ousia/gevent-statsd-mock

Installation
------------

.. code-block:: bash

    $ pip install gevent-statsd-mock


Basic Usage
-----------

In this sample we use `python-statsd <https://github.com/WoLpH/python-statsd>`_ for client library

.. code-block:: python

    >>> from gstatsdmock import StatsdMockServer()
    >>> server = StatsdMockServer()
    >>> server.start()
    >>> import statsd
    >>> conn = statsd.Connection(host='127.0.0.1', port=8125)
    >>> gauge = statsd.Gauge('bigtag')
    >>> gauge.send('subtag', 10)
    >>> server.wait('bigtag.subtag', n=1)
    >>> data = list(server.metrics['bigtag.subtag'])
    >>> assert data[0] == {'value': '10', 'type': 'gauge', 'rate': 1.0, 'timestamp': None}
    >>> server.stop()

