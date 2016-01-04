#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import gevent
import pprint
import socket
from collections import deque
import signal

from gevent.server import DatagramServer

import gevent.socket as gsocket

STATSD_DEFAULT_PORT = 8125

class StatsdTimeOutError(Exception):
    pass

class StatsdMockServer(DatagramServer):

    _metric_types = {
        'c': 'counter',
        'g': 'gauge',
        'ms': 'timer',
        'r': 'raw'
    }
        
    def __init__(self):
        self.metrics = {}
        listener = ':' + str(STATSD_DEFAULT_PORT)
        super(StatsdMockServer, self).__init__(listener)


    def handle(self, data, address):
        print('%s: got %r' % (address[0], data))
        self.socket.sendto(('Received %s bytes' % len(data)).encode('utf-8'), address)

        metric_name, value, metric_type, rate, timestamp = self._parse_packet(data) 
        self._log(metric_name, value, metric_type, rate, timestamp)

    def _parse_packet(self, packet):
        chunks = deque(packet.split('|'))
        metric_name_and_value = chunks.popleft()

        metric_name, value = metric_name_and_value.split(':')

        metric_type = chunks.popleft()
        if metric_type == 'r':  # raw type will add timestamp
            timestamp = int(chunks.popleft())
        else:
            timestamp = None
        if 0 < len(chunks) and chunks[0][0] == '@':  # rate added?
            rate = float(chunks.popleft()[1:])
        else:
            rate = 1.0
        metric_type = self._metric_types[metric_type]  # 'c' => 'counter'
        return (metric_name, value, metric_type, rate, timestamp)

    def _log(self, metric_name, value, metric_type, rate, timestamp):
        if metric_name not in self.metrics:
            self.metrics[metric_name] = deque([])
        metric_data = dict(
            value=value,
            type=metric_type,
            rate=rate,
            timestamp=timestamp
        )
        self.metrics[metric_name].append(metric_data)
    
    def wait(self, metric_name, n, timeout_msec=0):
        time_msec_start = int(time.time() * 1000)
        if metric_name not in self.metrics:
            self.metrics[metric_name] = deque([])

        while len(self.metrics[metric_name]) < n:
            gevent.sleep()
            if 0 < timeout_msec and time_msec_start + timeout_msec < int(time.time() * 1000):
                raise StatsdTimeOutError('wait() for metric \'%s\' timed out' % metric_name)

    def dump_events(self):
        print '========StatsdMockServer'
        for metric_name in self.metrics:
            print '-----%s' % metric_name
            i = 1
            for metric_data in self.metrics[metric_name]:
                print '[%d] %s' % (i, pprint.pformat(metric_data))
                i += 1

def main():
    import statsd
    print('Receiving datagrams on :8125')
    
    mock_server = StatsdMockServer()
    mock_server.start()
    print 'hello'
 
    statsd_client = statsd.StatsClient(prefix='bigtag')
 
    n = 5
    for i in range(n):
        statsd_client.gauge('subtag', i*10)
     
    mock_server.wait('bigtag.subtag', n)
    mock_server.stop()
    mock_server.dump_events()
    


if __name__ == '__main__':
    main()
    
