#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import datetime
from unittest import TestCase
from nose.tools import eq_, ok_, raises
import statsd
import gevent

from gstatsdmock import StatsdMockServer, StatsdTimeOutError, STATSD_DEFAULT_PORT


class StatsdConstantsTestCase(TestCase):
    def test_default_port(self):
        eq_(STATSD_DEFAULT_PORT, 8125)


class StatsdMockServerTestCase(TestCase):
    def test_normal(self):
        server = StatsdMockServer()
        try:
            server.start(bind_address='127.0.0.1', port=8125)

            statsd_conn = statsd.Connection(host='127.0.0.1', port=8125)

            # test gauge
            guage = statsd.Gauge('bigtag', statsd_conn)

            guage.send('subtag', 1)
            guage.send('subtag', 2)

            server.wait('bigtag.subtag', 2)

            ok_('bigtag.subtag' in server.metrics)
            eq_(len(server.metrics), 1)

            data1 = list(server.metrics['bigtag.subtag'])
            eq_(len(data1), 2)

            eq_(data1[0]['value'], '1')
            eq_(data1[0]['type'], 'gauge')
            eq_(data1[0]['timestamp'], None)  # for only raw
            eq_(data1[0]['rate'], 1.0)

            eq_(data1[1]['value'], '2')
            eq_(data1[1]['type'], 'gauge')
            eq_(data1[1]['timestamp'], None)  # for only raw
            eq_(data1[1]['rate'], 1.0)

            # test counter
            counter = statsd.Counter('bigtag', statsd_conn)
            counter.increment('subtag2', 100)
            counter.increment('subtag2', 200)
            server.wait('bigtag.subtag2', 2)

            data2 = list(server.metrics['bigtag.subtag2'])
            eq_(len(data2), 2)

            eq_(data2[0]['value'], '100')
            eq_(data2[0]['type'], 'counter')
            eq_(data2[0]['timestamp'], None)  # for only raw
            eq_(data2[0]['rate'], 1.0)

            eq_(data2[1]['value'], '200')
            eq_(data2[1]['type'], 'counter')
            eq_(data2[1]['timestamp'], None)  # for only raw
            eq_(data2[1]['rate'], 1.0)

            # test timer
            def _timer():
                timer = statsd.Timer('bigtag', statsd_conn)
                timer.start()
                gevent.sleep(0.1)
                timer.stop('subtag3')

                server.wait('bigtag.subtag3', 1)
                data3 = list(server.metrics['bigtag.subtag3'])
                eq_(len(data3), 1)

                ok_(100.0 < float(data3[0]['value']))
                eq_(data3[0]['type'], 'timer')
                eq_(data3[0]['timestamp'], None)  # for only raw
                eq_(data3[0]['rate'], 1.0)
            gth_timer = gevent.spawn(_timer)
            gth_timer.join()

            # test raw
            raw = statsd.Raw('bigtag', statsd_conn)
            ts = datetime.datetime.now().strftime('%s')
            raw.send('subtag4', 'raw-value1', timestamp=ts)
            server.wait('bigtag.subtag4', n=1)

            data4 = list(server.metrics['bigtag.subtag4'])

            eq_(data4[0]['value'], 'raw-value1')
            eq_(data4[0]['type'], 'raw')
            eq_(data4[0]['timestamp'], int(ts))
            eq_(data4[0]['rate'], 1.0)

        finally:
            server.stop()

    @raises(StatsdTimeOutError)
    def test_timeout(self):
        server = StatsdMockServer()
        server.start()
        try:
            server.wait('bigtag.subtag', n=1, timeout_msec=100)
        except:
            etype, value, traceback = sys.exc_info()
            raise etype, value, traceback
