#!/usr/bin/python
# -*- coding: utf-8 -*-
from unittest import TestCase
from nose.tools import eq_, ok_, raises
import statsd

from statsdmock import (
    StatsdMockServer, StatsdTimeOutError, STATSD_DEFAULT_PORT)

class StatsdMockServerTestCase(TestCase):
    
    def setUp(self):
        # Hook method for setting up the test fixture before exercising it
        self.server = StatsdMockServer()
        self.server.start()
        self.statsd_client = statsd.StatsClient(prefix="bigtag")
        super(StatsdMockServerTestCase, self).setUp()

    def tearDown(self):
        # Hook
        self.server.stop()
        del self.server
        super(StatsdMockServerTestCase, self).tearDown()
    
    def test_default_port(self):
        eq_(STATSD_DEFAULT_PORT, 8125)
        
    def test_normal(self):

        self.statsd_client.gauge('subtag', 1)
        self.statsd_client.gauge('subtag', 2)

        self.server.wait('bigtag.subtag', 2)
        ok_('bigtag.subtag' in self.server.metrics)
        eq_(len(self.server.metrics), 1)

        data1 = list(self.server.metrics['bigtag.subtag'])
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
        self.statsd_client.incr('subtag2', 100)
        self.statsd_client.incr('subtag2', 200)
        self.server.wait('bigtag.subtag2', 2)

        data2 = list(self.server.metrics['bigtag.subtag2'])
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
        self.statsd_client.timing('subtag3', 100)

        self.server.wait('bigtag.subtag3', 1)
        data3 = list(self.server.metrics['bigtag.subtag3'])
        eq_(len(data3), 1)

        ok_(100.0 == float(data3[0]['value']))
        eq_(data3[0]['type'], 'timer')
        eq_(data3[0]['timestamp'], None)  # for only raw
        eq_(data3[0]['rate'], 1.0)
            

    @raises(StatsdTimeOutError)
    def test_timeout(self):
        self.server.wait('bigtag.subtag', n=1, timeout_msec=100)

